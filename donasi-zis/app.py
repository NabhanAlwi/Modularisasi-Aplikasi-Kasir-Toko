# Donasi ZIS & Wakaf (zakat, infaq, sedekah, wakaf) — aplikasi MONOLITIK: semua kode ada di satu file ini.
# Tugas mahasiswa: pecah menjadi modul tanpa mengubah perilakunya (lihat README.md).
from flask import Flask, request, jsonify, render_template_string
import json, os, datetime

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

CSS = "<style>body{font-family:'Trebuchet MS';margin:30px;max-width:820px;color:#123} .bar{background:#e5efe8;height:14px;border-radius:7px} .isi{background:#1f7a4d;height:14px;border-radius:7px} .p{border:1px solid #cde;padding:12px;margin:10px 0;border-radius:8px} nav a{margin-right:14px}</style>"
NAV = "<nav><a href='/'>Program</a><a href='/kalkulator'>Kalkulator Zakat</a><a href='/laporan'>Laporan</a></nav>"


@app.route("/")
def index():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    html = "<html><head><title>Donasi ZIS</title>" + CSS + "</head><body>" + NAV + "<h1>Program Kebaikan</h1>"
    for p in data["program"]:
        terkumpul = 0
        for d in data["donasi"]:
            if d["program"] == p["id"] and d["status"] == "berhasil":
                terkumpul += d["diterima"]
        persen = round(terkumpul / p["target"] * 100, 1)
        lebar = 100 if persen > 100 else persen
        html += "<div class='p'><b>" + p["nama"] + "</b> <small>(" + p["jenis"] + ")</small><br>Rp " + "{:,}".format(terkumpul).replace(",", ".") + " dari Rp " + "{:,}".format(p["target"]).replace(",", ".")
        html += " · " + str(persen) + "%<div class='bar'><div class='isi' style='width:" + str(lebar) + "%'></div></div><a href='/donasi/" + p["id"] + "'>Donasi</a></div>"
    return html + "</body></html>"


@app.route("/donasi/<id_program>", methods=["GET", "POST"])
def donasi(id_program):
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    program = None
    for p in data["program"]:
        if p["id"] == id_program:
            program = p
    if program is None:
        return "Program tidak ditemukan", 404
    pesan = ""
    if request.method == "POST":
        nama = request.form.get("nama", "").strip()
        anonim = request.form.get("anonim") == "on"
        metode = request.form.get("metode", "")
        try:
            jumlah = int(request.form.get("jumlah", "0"))
        except ValueError:
            jumlah = 0
        if jumlah < 10000:
            pesan = "Donasi minimal Rp 10.000"
        elif metode not in ["qris", "transfer", "va"]:
            pesan = "Metode pembayaran tidak dikenal"
        elif nama == "" and not anonim:
            pesan = "Nama wajib diisi (atau centang anonim)"
        else:
            if metode == "qris":
                admin = round(jumlah * 0.007)
            elif metode == "va":
                admin = 4000
            else:
                admin = 0
            tgl = datetime.date.today()
            nomor = len(data["donasi"]) + 1
            baru = {"id": "DN" + str(nomor).zfill(4), "kuitansi": "ZIS/" + str(tgl.year) + "/" + str(tgl.month).zfill(2) + "/" + str(nomor).zfill(4),
                    "program": id_program, "nama": nama, "anonim": anonim, "jumlah": jumlah, "metode": metode, "biaya_admin": admin,
                    "diterima": jumlah - admin, "tanggal": tgl.isoformat(), "status": "berhasil"}
            data["donasi"].append(baru)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            pesan = "Jazakallahu khairan. Kuitansi " + baru["kuitansi"] + ", diterima program Rp " + "{:,}".format(baru["diterima"]).replace(",", ".")
    donatur = ""
    for d in reversed(data["donasi"]):
        if d["program"] == id_program and d["status"] == "berhasil":
            donatur += "<li>" + ("Hamba Allah" if d["anonim"] else d["nama"]) + " — Rp " + "{:,}".format(d["jumlah"]).replace(",", ".") + "</li>"
    return render_template_string("<html><head>" + CSS + "</head><body>" + NAV + """<h1>{{ p.nama }}</h1><p><b>{{ pesan }}</b></p>
    <form method="post">Nama <input name="nama"> <label><input type="checkbox" name="anonim"> sembunyikan nama</label><br>
    Jumlah <input type="number" name="jumlah"> Metode <select name="metode"><option value="qris">QRIS (0,7%)</option><option value="transfer">Transfer bank</option><option value="va">Virtual account (Rp 4.000)</option></select>
    <button>Tunaikan</button></form><h3>Donatur terbaru</h3><ul>""" + donatur + "</ul></body></html>", p=program, pesan=pesan)


@app.route("/kalkulator", methods=["GET", "POST"])
def kalkulator():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    harga_emas = data["pengaturan"]["harga_emas_per_gram"]
    hasil = ""
    if request.method == "POST":
        jenis = request.form.get("jenis")
        try:
            a = int(request.form.get("a") or 0)
            b = int(request.form.get("b") or 0)
            c = int(request.form.get("c") or 0)
        except ValueError:
            a = b = c = 0
        if jenis == "penghasilan":
            nisab = round(85 * harga_emas / 12)
            total = a + b
            if total >= nisab:
                hasil = "Wajib zakat: Rp " + "{:,}".format(round(total * 0.025)).replace(",", ".") + " per bulan"
            else:
                hasil = "Belum wajib zakat (nisab Rp " + "{:,}".format(nisab).replace(",", ".") + " per bulan)"
        else:
            nisab = 85 * harga_emas
            bersih = a + b - c
            if bersih >= nisab and request.form.get("haul") == "on":
                hasil = "Wajib zakat maal: Rp " + "{:,}".format(round(bersih * 0.025)).replace(",", ".")
            else:
                hasil = "Belum wajib zakat maal (nisab Rp " + "{:,}".format(nisab).replace(",", ".") + ", harus genap 1 tahun)"
    return render_template_string("<html><head>" + CSS + "</head><body>" + NAV + """<h1>Kalkulator Zakat</h1><p>Harga emas: Rp {{ emas }}/gram</p><p><b>{{ hasil }}</b></p>
    <div class="p"><h3>Zakat penghasilan</h3><form method="post"><input type="hidden" name="jenis" value="penghasilan">Gaji/bulan <input name="a"> Pendapatan lain <input name="b"> <button>Hitung</button></form></div>
    <div class="p"><h3>Zakat maal</h3><form method="post"><input type="hidden" name="jenis" value="maal">Tabungan & investasi <input name="a"> Emas (Rp) <input name="b"> Utang jatuh tempo <input name="c">
    <label><input type="checkbox" name="haul"> sudah 1 tahun</label> <button>Hitung</button></form></div></body></html>""",
                                  emas="{:,}".format(harga_emas).replace(",", "."), hasil=hasil)


@app.route("/laporan")
def laporan():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    bulan = request.args.get("bulan", datetime.date.today().strftime("%Y-%m"))
    per_jenis = {}
    for d in data["donasi"]:
        if d["tanggal"][:7] == bulan and d["status"] == "berhasil":
            jenis = [p["jenis"] for p in data["program"] if p["id"] == d["program"]][0]
            per_jenis[jenis] = per_jenis.get(jenis, 0) + d["jumlah"]
    baris = "".join("<li>" + j.capitalize() + ": Rp " + "{:,}".format(v).replace(",", ".") + "</li>" for j, v in per_jenis.items())
    return "<html><head>" + CSS + "</head><body>" + NAV + "<h1>Laporan " + bulan + "</h1><ul>" + (baris or "<li>Belum ada donasi</li>") + "</ul></body></html>"


# ---------------- API JSON ----------------

@app.route("/api/program")
def api_program():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    hasil = []
    for p in data["program"]:
        terkumpul = sum(d["diterima"] for d in data["donasi"] if d["program"] == p["id"] and d["status"] == "berhasil")
        persen = round(terkumpul / p["target"] * 100, 1)
        hasil.append(dict(p, terkumpul=terkumpul, persen=persen, tercapai=persen >= 100))
    return jsonify(hasil)


@app.route("/api/donasi", methods=["POST"])
def api_donasi():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    b = request.get_json(silent=True) or {}
    program = next((p for p in data["program"] if p["id"] == b.get("program")), None)
    if program is None:
        return jsonify({"error": "Program tidak ditemukan"}), 404
    jumlah = b.get("jumlah")
    if not isinstance(jumlah, int) or jumlah < 10000:
        return jsonify({"error": "Donasi minimal Rp 10.000"}), 400
    metode = b.get("metode")
    if metode == "qris":
        admin = round(jumlah * 0.007)
    elif metode == "va":
        admin = 4000
    elif metode == "transfer":
        admin = 0
    else:
        return jsonify({"error": "Metode pembayaran tidak dikenal"}), 400
    nama = str(b.get("nama", "")).strip()
    anonim = bool(b.get("anonim", False))
    if nama == "" and not anonim:
        return jsonify({"error": "Nama wajib diisi (atau pilih anonim)"}), 400
    tgl = datetime.date.fromisoformat(b["tanggal"]) if b.get("tanggal") else datetime.date.today()
    nomor = len(data["donasi"]) + 1
    baru = {"id": "DN" + str(nomor).zfill(4), "kuitansi": "ZIS/" + str(tgl.year) + "/" + str(tgl.month).zfill(2) + "/" + str(nomor).zfill(4),
            "program": program["id"], "nama": nama, "anonim": anonim, "jumlah": jumlah, "metode": metode, "biaya_admin": admin,
            "diterima": jumlah - admin, "tanggal": tgl.isoformat(), "status": "berhasil"}
    data["donasi"].append(baru)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return jsonify(baru), 201


@app.route("/api/program/<id_program>/donatur")
def api_donatur(id_program):
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    hasil = []
    for d in reversed(data["donasi"]):
        if d["program"] == id_program and d["status"] == "berhasil":
            hasil.append({"nama": "Hamba Allah" if d["anonim"] else d["nama"], "jumlah": d["jumlah"], "tanggal": d["tanggal"]})
    return jsonify(hasil)


@app.route("/api/zakat/penghasilan", methods=["POST"])
def api_zakat_penghasilan():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    b = request.get_json(silent=True) or {}
    total = b.get("gaji", 0) + b.get("pendapatan_lain", 0)
    nisab = round(85 * data["pengaturan"]["harga_emas_per_gram"] / 12)
    wajib = total >= nisab
    return jsonify({"penghasilan": total, "nisab_bulanan": nisab, "wajib": wajib, "zakat": round(total * 0.025) if wajib else 0})


@app.route("/api/zakat/maal", methods=["POST"])
def api_zakat_maal():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    b = request.get_json(silent=True) or {}
    bersih = b.get("tabungan", 0) + b.get("emas", 0) + b.get("investasi", 0) - b.get("utang", 0)
    nisab = 85 * data["pengaturan"]["harga_emas_per_gram"]
    if bersih < nisab:
        return jsonify({"harta_bersih": bersih, "nisab": nisab, "wajib": False, "alasan": "Belum mencapai nisab", "zakat": 0})
    if not b.get("haul", False):
        return jsonify({"harta_bersih": bersih, "nisab": nisab, "wajib": False, "alasan": "Belum genap haul (1 tahun)", "zakat": 0})
    return jsonify({"harta_bersih": bersih, "nisab": nisab, "wajib": True, "zakat": round(bersih * 0.025)})


@app.route("/api/pengaturan/emas", methods=["POST"])
def api_harga_emas():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    harga = (request.get_json(silent=True) or {}).get("harga_emas_per_gram")
    if not isinstance(harga, int) or harga <= 0:
        return jsonify({"error": "Harga emas harus bilangan bulat > 0"}), 400
    data["pengaturan"]["harga_emas_per_gram"] = harga
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return jsonify(data["pengaturan"])


@app.route("/api/laporan")
def api_laporan():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    bulan = request.args.get("bulan", datetime.date.today().strftime("%Y-%m"))
    per_jenis = {}
    admin = 0
    donatur = 0
    for d in data["donasi"]:
        if d["tanggal"][:7] == bulan and d["status"] == "berhasil":
            jenis = [p["jenis"] for p in data["program"] if p["id"] == d["program"]][0]
            per_jenis[jenis] = per_jenis.get(jenis, 0) + d["jumlah"]
            admin += d["biaya_admin"]
            donatur += 1
    return jsonify({"bulan": bulan, "per_jenis": per_jenis, "total": sum(per_jenis.values()), "total_biaya_admin": admin, "jumlah_donasi": donatur})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
