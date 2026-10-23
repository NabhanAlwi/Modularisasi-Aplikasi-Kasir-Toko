# Kasir Toko (Point of Sale) — aplikasi MONOLITIK: semua kode ada di satu file ini.
# Tugas mahasiswa: pecah menjadi modul tanpa mengubah perilakunya (lihat README.md).
from flask import Flask, request, jsonify, render_template_string, redirect
import json, os, datetime

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


@app.route("/")
def index():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    baris = ""
    for p in data["produk"]:
        harga = "Rp {:,.0f}".format(p["harga"]).replace(",", ".")
        warna = "#fde2e2" if p["stok"] < 5 else "white"
        baris += "<tr style='background:" + warna + "'><td>" + p["kode"] + "</td><td>" + p["nama"] + "</td><td>" + p["kategori"] + "</td><td>" + harga + "</td><td>" + str(p["stok"]) + "</td></tr>"
    menipis = [p["nama"] for p in data["produk"] if p["stok"] < 5]
    html = """
    <html><head><title>Kasir Toko</title>
    <style>body{font-family:sans-serif;margin:30px} table{border-collapse:collapse} td,th{border:1px solid #ccc;padding:6px 10px} nav a{margin-right:15px}</style></head>
    <body><nav><a href="/">Produk</a><a href="/transaksi">Transaksi Baru</a><a href="/laporan">Laporan</a></nav>
    <h1>Daftar Produk</h1>
    {% if menipis %}<p style="color:#b00">Stok menipis: {{ menipis|join(", ") }}</p>{% endif %}
    <table><tr><th>Kode</th><th>Nama</th><th>Kategori</th><th>Harga</th><th>Stok</th></tr>{{ baris|safe }}</table>
    </body></html>"""
    return render_template_string(html, baris=baris, menipis=menipis)


@app.route("/transaksi", methods=["GET", "POST"])
def transaksi():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    pesan = ""
    struk = None
    if request.method == "POST":
        member_id = request.form.get("member", "").strip()
        bayar = request.form.get("bayar", "0").strip()
        items = []
        error = None
        for line in request.form.get("items", "").strip().splitlines():
            if line.strip() == "":
                continue
            bagian = line.split(",")
            if len(bagian) != 2:
                error = "Format item salah: " + line
                break
            kode = bagian[0].strip().upper()
            try:
                qty = int(bagian[1].strip())
            except ValueError:
                error = "Jumlah harus angka: " + line
                break
            produk = None
            for p in data["produk"]:
                if p["kode"] == kode:
                    produk = p
            if produk is None:
                error = "Produk tidak ditemukan: " + kode
                break
            if qty <= 0:
                error = "Jumlah harus lebih dari 0: " + kode
                break
            if produk["stok"] < qty:
                error = "Stok " + produk["nama"] + " tidak cukup (sisa " + str(produk["stok"]) + ")"
                break
            items.append({"kode": kode, "nama": produk["nama"], "qty": qty, "harga": produk["harga"]})
        if error is None and len(items) == 0:
            error = "Keranjang kosong"
        if error is None:
            subtotal = 0
            for it in items:
                subtotal += it["qty"] * it["harga"]
            persen = 0
            for m in data["member"]:
                if m["id"] == member_id:
                    if m["level"] == "gold":
                        persen = 10
                    elif m["level"] == "silver":
                        persen = 5
            if subtotal >= 1000000:
                persen += 5
            if persen > 15:
                persen = 15
            diskon = round(subtotal * persen / 100)
            ppn = round((subtotal - diskon) * 0.11)
            total = subtotal - diskon + ppn
            try:
                bayar = int(bayar)
            except ValueError:
                bayar = 0
            if bayar < total:
                error = "Uang bayar kurang. Total " + "Rp {:,.0f}".format(total).replace(",", ".")
            else:
                tanggal = datetime.date.today().isoformat()
                urut = 1
                for t in data["transaksi"]:
                    if t["tanggal"] == tanggal:
                        urut += 1
                no = "TRX-" + tanggal.replace("-", "") + "-" + str(urut).zfill(3)
                for it in items:
                    for p in data["produk"]:
                        if p["kode"] == it["kode"]:
                            p["stok"] -= it["qty"]
                struk = {"no": no, "tanggal": tanggal, "member": member_id, "items": items, "subtotal": subtotal,
                         "diskon": diskon, "ppn": ppn, "total": total, "bayar": bayar, "kembali": bayar - total}
                data["transaksi"].append(struk)
                f = open(DATA_FILE, "w", encoding="utf-8")
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.close()
        if error:
            pesan = error
    html = """
    <html><head><title>Transaksi</title>
    <style>body{font-family:sans-serif;margin:30px} textarea,input{display:block;margin:6px 0 14px;padding:6px} nav a{margin-right:15px} .struk{border:1px dashed #333;padding:15px;width:340px;font-family:monospace}</style></head>
    <body><nav><a href="/">Produk</a><a href="/transaksi">Transaksi Baru</a><a href="/laporan">Laporan</a></nav>
    <h1>Transaksi Baru</h1>
    {% if pesan %}<p style="color:#b00">{{ pesan }}</p>{% endif %}
    {% if struk %}<div class="struk"><b>{{ struk.no }}</b><br>{{ struk.tanggal }}<br><br>
      {% for it in struk['items'] %}{{ it.nama }} x{{ it.qty }} = {{ "Rp {:,.0f}".format(it.qty*it.harga).replace(",", ".") }}<br>{% endfor %}<br>
      Subtotal: {{ "Rp {:,.0f}".format(struk.subtotal).replace(",", ".") }}<br>Diskon: {{ "Rp {:,.0f}".format(struk.diskon).replace(",", ".") }}<br>
      PPN 11%: {{ "Rp {:,.0f}".format(struk.ppn).replace(",", ".") }}<br><b>Total: {{ "Rp {:,.0f}".format(struk.total).replace(",", ".") }}</b><br>
      Bayar: {{ "Rp {:,.0f}".format(struk.bayar).replace(",", ".") }}<br>Kembali: {{ "Rp {:,.0f}".format(struk.kembali).replace(",", ".") }}</div>{% endif %}
    <form method="post">
      <label>ID Member (kosongkan jika bukan member)</label><input name="member">
      <label>Item, satu per baris: KODE,JUMLAH</label><textarea name="items" rows="5" cols="30">P001,2</textarea>
      <label>Uang bayar</label><input name="bayar" type="number">
      <button>Proses</button>
    </form></body></html>"""
    return render_template_string(html, pesan=pesan, struk=struk)


@app.route("/laporan")
def laporan():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    tanggal = request.args.get("tanggal", datetime.date.today().isoformat())
    omzet = 0
    jumlah = 0
    terjual = {}
    for t in data["transaksi"]:
        if t["tanggal"] == tanggal:
            omzet += t["total"]
            jumlah += 1
            for it in t["items"]:
                terjual[it["nama"]] = terjual.get(it["nama"], 0) + it["qty"]
    terlaris = sorted(terjual.items(), key=lambda x: x[1], reverse=True)[:3]
    html = """
    <html><head><title>Laporan</title><style>body{font-family:sans-serif;margin:30px} nav a{margin-right:15px}</style></head>
    <body><nav><a href="/">Produk</a><a href="/transaksi">Transaksi Baru</a><a href="/laporan">Laporan</a></nav>
    <h1>Laporan Harian {{ tanggal }}</h1>
    <form><input type="date" name="tanggal" value="{{ tanggal }}"><button>Lihat</button></form>
    <p>Jumlah transaksi: {{ jumlah }}<br>Omzet: {{ omzet }}</p>
    <h3>Produk terlaris</h3><ol>{% for n, q in terlaris %}<li>{{ n }} ({{ q }})</li>{% endfor %}</ol>
    </body></html>"""
    return render_template_string(html, tanggal=tanggal, jumlah=jumlah, omzet="Rp {:,.0f}".format(omzet).replace(",", "."), terlaris=terlaris)


# ---------------- API JSON ----------------

@app.route("/api/produk")
def api_produk():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    kategori = request.args.get("kategori")
    hasil = []
    for p in data["produk"]:
        if kategori is None or p["kategori"] == kategori:
            hasil.append(p)
    return jsonify(hasil)


@app.route("/api/transaksi", methods=["POST"])
def api_transaksi():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    body = request.get_json(silent=True) or {}
    member_id = body.get("member", "")
    items = []
    for item in body.get("items", []):
        kode = str(item.get("kode", "")).upper()
        qty = item.get("qty", 0)
        produk = None
        for p in data["produk"]:
            if p["kode"] == kode:
                produk = p
        if produk is None:
            return jsonify({"error": "Produk tidak ditemukan: " + kode}), 404
        if not isinstance(qty, int) or qty <= 0:
            return jsonify({"error": "Jumlah harus lebih dari 0: " + kode}), 400
        if produk["stok"] < qty:
            return jsonify({"error": "Stok " + produk["nama"] + " tidak cukup (sisa " + str(produk["stok"]) + ")"}), 400
        items.append({"kode": kode, "nama": produk["nama"], "qty": qty, "harga": produk["harga"]})
    if len(items) == 0:
        return jsonify({"error": "Keranjang kosong"}), 400
    subtotal = sum(it["qty"] * it["harga"] for it in items)
    persen = 0
    for m in data["member"]:
        if m["id"] == member_id:
            if m["level"] == "gold":
                persen = 10
            elif m["level"] == "silver":
                persen = 5
    if subtotal >= 1000000:
        persen += 5
    if persen > 15:
        persen = 15
    diskon = round(subtotal * persen / 100)
    ppn = round((subtotal - diskon) * 0.11)
    total = subtotal - diskon + ppn
    bayar = body.get("bayar", 0)
    if bayar < total:
        return jsonify({"error": "Uang bayar kurang", "total": total}), 400
    tanggal = body.get("tanggal") or datetime.date.today().isoformat()
    urut = 1
    for t in data["transaksi"]:
        if t["tanggal"] == tanggal:
            urut += 1
    no = "TRX-" + tanggal.replace("-", "") + "-" + str(urut).zfill(3)
    for it in items:
        for p in data["produk"]:
            if p["kode"] == it["kode"]:
                p["stok"] -= it["qty"]
    struk = {"no": no, "tanggal": tanggal, "member": member_id, "items": items, "subtotal": subtotal,
             "diskon": diskon, "ppn": ppn, "total": total, "bayar": bayar, "kembali": bayar - total}
    data["transaksi"].append(struk)
    f = open(DATA_FILE, "w", encoding="utf-8")
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.close()
    return jsonify(struk), 201


@app.route("/api/laporan")
def api_laporan():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    tanggal = request.args.get("tanggal", datetime.date.today().isoformat())
    omzet = 0
    jumlah = 0
    terjual = {}
    for t in data["transaksi"]:
        if t["tanggal"] == tanggal:
            omzet += t["total"]
            jumlah += 1
            for it in t["items"]:
                terjual[it["nama"]] = terjual.get(it["nama"], 0) + it["qty"]
    terlaris = sorted(terjual.items(), key=lambda x: x[1], reverse=True)[:3]
    return jsonify({"tanggal": tanggal, "jumlah_transaksi": jumlah, "omzet": omzet, "terlaris": [{"nama": n, "qty": q} for n, q in terlaris]})


@app.route("/api/stok-menipis")
def api_stok_menipis():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    return jsonify([p for p in data["produk"] if p["stok"] < 5])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
