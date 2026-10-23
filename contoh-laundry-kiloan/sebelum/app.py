# Laundry Kiloan — CONTOH versi MONOLITIK: semua kode ada di satu file ini.
# Bandingkan dengan folder ../sesudah/ (versi modular dengan perilaku yang sama).
from flask import Flask, request, jsonify, render_template_string, redirect
import json, os, datetime, re

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


@app.route("/")
def index():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    status = request.args.get("status", "")
    baris = ""
    for n in data["nota"]:
        if status == "" or n["status"] == status:
            baris += "<tr><td>" + n["no"] + "</td><td>" + n["nama"] + "</td><td>" + n["layanan"] + (" (express)" if n["express"] else "") + "</td>"
            baris += "<td>" + str(n["berat"]) + " kg</td><td>Rp " + "{:,}".format(n["total"]).replace(",", ".") + "</td><td>" + n["estimasi_selesai"] + "</td>"
            baris += "<td>" + n["status"] + "</td><td><form method='post' action='/nota/" + n["no"] + "/status'><button>Lanjut</button></form></td></tr>"
    pesan = request.args.get("pesan", "")
    return render_template_string("""
    <html><head><title>Laundry Kiloan</title><style>body{font-family:sans-serif;margin:30px} td,th{border-bottom:1px solid #ddd;padding:6px 10px} input,select{margin:4px}</style></head>
    <body><h1>🧺 Laundry Kiloan</h1><p><a href="/">Semua</a> · <a href="/?status=diterima">Diterima</a> · <a href="/?status=siap">Siap diambil</a> · <a href="/laporan">Laporan</a></p>
    <p style="color:#b00">{{ pesan }}</p>
    <form method="post" action="/nota">Nama <input name="nama"> HP <input name="hp"> Layanan <select name="layanan"><option value="cuci_kering">Cuci kering</option>
    <option value="cuci_setrika">Cuci setrika</option><option value="setrika">Setrika saja</option></select> Berat (kg) <input name="berat" size="4">
    <label><input type="checkbox" name="express"> express</label> <button>Buat nota</button></form>
    <table><tr><th>No</th><th>Nama</th><th>Layanan</th><th>Berat</th><th>Total</th><th>Selesai</th><th>Status</th><th></th></tr>{{ baris|safe }}</table>
    </body></html>""", baris=baris, pesan=pesan)


@app.route("/nota", methods=["POST"])
def buat_nota():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    nama = request.form.get("nama", "").strip()
    hp = request.form.get("hp", "").strip()
    layanan = request.form.get("layanan", "")
    express = request.form.get("express") == "on"
    try:
        berat = float(request.form.get("berat", "0").replace(",", "."))
    except ValueError:
        berat = 0
    if layanan not in ["cuci_kering", "cuci_setrika", "setrika"]:
        return redirect("/?pesan=Layanan tidak dikenal")
    if berat <= 0 or berat > 50:
        return redirect("/?pesan=Berat harus lebih dari 0 dan maksimal 50 kg")
    if nama == "":
        return redirect("/?pesan=Nama wajib diisi")
    if not re.match(r"^08\d{8,11}$", hp):
        return redirect("/?pesan=Nomor HP tidak valid")
    if layanan == "cuci_kering":
        tarif = 7000
    elif layanan == "cuci_setrika":
        tarif = 9000
    else:
        tarif = 6000
    berat_ditagih = berat if berat > 3 else 3
    harga_dasar = round(berat_ditagih * tarif)
    biaya_express = harga_dasar * 50 // 100 if express else 0
    member = False
    for p in data["pelanggan"]:
        if p["hp"] == hp and p["member"]:
            member = True
    diskon = (harga_dasar + biaya_express) * 10 // 100 if member else 0
    hari_ini = datetime.date.today()
    selesai = hari_ini + datetime.timedelta(days=1 if express else 2)
    if selesai.weekday() == 6:
        selesai = selesai + datetime.timedelta(days=1)
    urut = len([n for n in data["nota"] if n["tanggal"] == hari_ini.isoformat()]) + 1
    no = "LDY-" + hari_ini.strftime("%y%m%d") + "-" + str(urut).zfill(2)
    data["nota"].append({"no": no, "tanggal": hari_ini.isoformat(), "hp": hp, "nama": nama, "layanan": layanan, "berat": berat, "berat_ditagih": berat_ditagih,
                         "express": express, "harga_dasar": harga_dasar, "biaya_express": biaya_express, "diskon": diskon,
                         "total": harga_dasar + biaya_express - diskon, "estimasi_selesai": selesai.isoformat(), "status": "diterima",
                         "tgl_diambil": None, "biaya_simpan": 0})
    f = open(DATA_FILE, "w", encoding="utf-8")
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.close()
    return redirect("/?pesan=Nota " + no + " dibuat, selesai " + selesai.strftime("%d-%m-%Y"))


@app.route("/nota/<no>/status", methods=["POST"])
def lanjut_status(no):
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    urutan = ["diterima", "dicuci", "siap", "diambil"]
    for n in data["nota"]:
        if n["no"] == no:
            i = urutan.index(n["status"])
            if i == len(urutan) - 1:
                return redirect("/?pesan=Nota sudah diambil")
            n["status"] = urutan[i + 1]
            if n["status"] == "diambil":
                hari_ini = datetime.date.today()
                lewat = (hari_ini - datetime.date.fromisoformat(n["estimasi_selesai"])).days - 7
                n["tgl_diambil"] = hari_ini.isoformat()
                n["biaya_simpan"] = lewat * 2000 if lewat > 0 else 0
            f = open(DATA_FILE, "w", encoding="utf-8")
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.close()
            return redirect("/?pesan=" + no + " sekarang " + n["status"])
    return redirect("/?pesan=Nota tidak ditemukan")


@app.route("/laporan")
def laporan():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    tanggal = request.args.get("tanggal", datetime.date.today().isoformat())
    jumlah = 0
    kg = 0
    pendapatan = 0
    per_layanan = {}
    for n in data["nota"]:
        if n["tanggal"] == tanggal:
            jumlah += 1
            kg += n["berat"]
            pendapatan += n["total"]
            per_layanan[n["layanan"]] = per_layanan.get(n["layanan"], 0) + 1
    return render_template_string("""<html><body style="font-family:sans-serif;margin:30px"><a href="/">← kembali</a><h1>Laporan {{ t }}</h1>
    <form><input type="date" name="tanggal" value="{{ t }}"><button>Lihat</button></form>
    <p>{{ j }} nota · {{ kg }} kg · Rp {{ p }}</p><ul>{% for l, c in pl.items() %}<li>{{ l }}: {{ c }}</li>{% endfor %}</ul></body></html>""",
                                  t=tanggal, j=jumlah, kg=round(kg, 1), p="{:,}".format(pendapatan).replace(",", "."), pl=per_layanan)


# ---------------- API JSON ----------------

@app.route("/api/nota")
def api_daftar():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    status = request.args.get("status")
    return jsonify([n for n in data["nota"] if status is None or n["status"] == status])


@app.route("/api/nota", methods=["POST"])
def api_buat():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    b = request.get_json(silent=True) or {}
    nama = str(b.get("nama", "")).strip()
    hp = str(b.get("hp", "")).strip()
    layanan = b.get("layanan")
    berat = b.get("berat", 0)
    express = bool(b.get("express", False))
    if layanan not in ["cuci_kering", "cuci_setrika", "setrika"]:
        return jsonify({"error": "Layanan tidak dikenal"}), 400
    if not isinstance(berat, (int, float)) or berat <= 0 or berat > 50:
        return jsonify({"error": "Berat harus lebih dari 0 dan maksimal 50 kg"}), 400
    if nama == "":
        return jsonify({"error": "Nama wajib diisi"}), 400
    if not re.match(r"^08\d{8,11}$", hp):
        return jsonify({"error": "Nomor HP tidak valid"}), 400
    tarif = {"cuci_kering": 7000, "cuci_setrika": 9000, "setrika": 6000}[layanan]
    berat_ditagih = max(berat, 3)
    harga_dasar = round(berat_ditagih * tarif)
    biaya_express = 0
    if express:
        biaya_express = harga_dasar * 50 // 100
    member = any(p["hp"] == hp and p["member"] for p in data["pelanggan"])
    diskon = 0
    if member:
        diskon = (harga_dasar + biaya_express) * 10 // 100
    tgl = datetime.date.fromisoformat(b["tanggal"]) if b.get("tanggal") else datetime.date.today()
    selesai = tgl + datetime.timedelta(days=1 if express else 2)
    if selesai.weekday() == 6:
        selesai += datetime.timedelta(days=1)
    urut = len([n for n in data["nota"] if n["tanggal"] == tgl.isoformat()]) + 1
    nota = {"no": "LDY-" + tgl.strftime("%y%m%d") + "-" + str(urut).zfill(2), "tanggal": tgl.isoformat(), "hp": hp, "nama": nama, "layanan": layanan,
            "berat": berat, "berat_ditagih": berat_ditagih, "express": express, "harga_dasar": harga_dasar, "biaya_express": biaya_express,
            "diskon": diskon, "total": harga_dasar + biaya_express - diskon, "estimasi_selesai": selesai.isoformat(), "status": "diterima",
            "tgl_diambil": None, "biaya_simpan": 0}
    data["nota"].append(nota)
    f = open(DATA_FILE, "w", encoding="utf-8")
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.close()
    return jsonify(nota), 201


@app.route("/api/nota/<no>/status", methods=["POST"])
def api_status(no):
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    b = request.get_json(silent=True) or {}
    urutan = ["diterima", "dicuci", "siap", "diambil"]
    nota = next((n for n in data["nota"] if n["no"] == no), None)
    if nota is None:
        return jsonify({"error": "Nota tidak ditemukan"}), 404
    if nota["status"] == "diambil":
        return jsonify({"error": "Nota sudah diambil"}), 400
    nota["status"] = urutan[urutan.index(nota["status"]) + 1]
    if nota["status"] == "diambil":
        tgl = datetime.date.fromisoformat(b["tanggal"]) if b.get("tanggal") else datetime.date.today()
        lewat = (tgl - datetime.date.fromisoformat(nota["estimasi_selesai"])).days - 7
        nota["tgl_diambil"] = tgl.isoformat()
        nota["biaya_simpan"] = max(lewat, 0) * 2000
    f = open(DATA_FILE, "w", encoding="utf-8")
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.close()
    return jsonify(nota)


@app.route("/api/laporan")
def api_laporan():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    tanggal = request.args.get("tanggal", datetime.date.today().isoformat())
    harian = [n for n in data["nota"] if n["tanggal"] == tanggal]
    per_layanan = {}
    for n in harian:
        per_layanan[n["layanan"]] = per_layanan.get(n["layanan"], 0) + 1
    return jsonify({"tanggal": tanggal, "jumlah_nota": len(harian), "total_kg": round(sum(n["berat"] for n in harian), 1),
                    "pendapatan": sum(n["total"] for n in harian), "per_layanan": per_layanan})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
