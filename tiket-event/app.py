# Tiket Event Kampus (pemesanan tiket) — aplikasi MONOLITIK: semua kode ada di satu file ini.
# Tugas mahasiswa: pecah menjadi modul tanpa mengubah perilakunya (lihat README.md).
from flask import Flask, request, jsonify, render_template_string
import json, os, datetime, re

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


@app.route("/")
def index():
    data = json.load(open(DATA_FILE, encoding="utf-8"))
    kartu = ""
    for e in data["event"]:
        info = ""
        for nama_kat, k in e["kategori"].items():
            terjual = sum(p["jumlah"] for p in data["pesanan"] if p["event"] == e["id"] and p["kategori"] == nama_kat and p["status"] == "lunas")
            sisa = k["kuota"] - terjual
            info += "<li>" + nama_kat + ": Rp " + "{:,}".format(k["harga"]).replace(",", ".") + " — " + ("<b style='color:red'>HABIS</b>" if sisa <= 0 else "sisa " + str(sisa)) + "</li>"
        tgl = datetime.date.fromisoformat(e["tanggal"])
        bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"][tgl.month - 1]
        kartu += "<div style='border:1px solid #ccc;border-radius:10px;padding:14px;margin:12px 0'><h2><a href='/event/" + e["id"] + "'>" + e["nama"] + "</a></h2>"
        kartu += "<p>" + str(tgl.day) + " " + bulan + " " + str(tgl.year) + " · " + e["lokasi"] + "</p><ul>" + info + "</ul></div>"
    return "<html><head><title>Tiket Event</title></head><body style='font-family:Arial;margin:30px;max-width:760px'><h1>🎫 Event Kampus</h1>" + kartu + "<p><a href='/cek'>Cek pesanan</a></p></body></html>"


@app.route("/event/<id_event>", methods=["GET", "POST"])
def detail(id_event):
    data = json.load(open(DATA_FILE, encoding="utf-8"))
    event = None
    for e in data["event"]:
        if e["id"] == id_event:
            event = e
    if event is None:
        return "Event tidak ditemukan", 404
    pesan = ""
    if request.method == "POST":
        kategori = request.form.get("kategori", "")
        nama = request.form.get("nama", "").strip()
        email = request.form.get("email", "").strip()
        kode_promo = request.form.get("promo", "").strip().upper()
        try:
            jumlah = int(request.form.get("jumlah", "0"))
        except ValueError:
            jumlah = 0
        hari_ini = datetime.date.today()
        if nama == "" or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            pesan = "Nama dan email yang valid wajib diisi"
        elif jumlah < 1 or jumlah > 5:
            pesan = "Jumlah tiket 1–5 per pesanan"
        elif kategori not in event["kategori"]:
            pesan = "Kategori tidak tersedia"
        else:
            terjual = sum(p["jumlah"] for p in data["pesanan"] if p["event"] == id_event and p["kategori"] == kategori and p["status"] == "lunas")
            if event["kategori"][kategori]["kuota"] - terjual < jumlah:
                pesan = "Kuota tidak mencukupi"
            else:
                dasar = event["kategori"][kategori]["harga"] * jumlah
                early = 0
                if (datetime.date.fromisoformat(event["tanggal"]) - hari_ini).days >= 30:
                    early = dasar * 15 // 100
                diskon_promo = 0
                if kode_promo:
                    for pr in data["promo"]:
                        if pr["kode"] == kode_promo and pr["terpakai"] < pr["kuota"] and hari_ini.isoformat() <= pr["berlaku_sampai"]:
                            diskon_promo = min((dasar - early) * pr["persen"] // 100, pr["maks"])
                            pr["terpakai"] += 1
                layanan = 5000 * jumlah
                total = dasar - early - diskon_promo + layanan
                kode = "TIX-" + id_event + "-" + str(len(data["pesanan"]) + 1).zfill(4)
                data["pesanan"].append({"kode": kode, "event": id_event, "kategori": kategori, "jumlah": jumlah, "nama": nama, "email": email,
                                        "tanggal_pesan": hari_ini.isoformat(), "harga_dasar": dasar, "diskon_early": early, "diskon_promo": diskon_promo,
                                        "kode_promo": kode_promo if diskon_promo > 0 else "", "biaya_layanan": layanan, "total": total, "status": "lunas", "refund": 0})
                json.dump(data, open(DATA_FILE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
                pesan = "Pesanan " + kode + " berhasil. Total bayar Rp " + "{:,}".format(total).replace(",", ".")
    pilihan = "".join("<option>" + k + "</option>" for k in event["kategori"])
    return render_template_string("""<html><body style='font-family:Arial;margin:30px'><a href='/'>← semua event</a>
    <h1>{{ e.nama }}</h1><p>{{ e.tanggal }} · {{ e.lokasi }}</p><p><b>{{ pesan }}</b></p>
    <form method='post'>Kategori <select name='kategori'>""" + pilihan + """</select><br>Jumlah <input name='jumlah' type='number' value='1'><br>
    Nama <input name='nama'><br>Email <input name='email'><br>Kode promo <input name='promo'><br><button>Pesan</button></form></body></html>""", e=event, pesan=pesan)


@app.route("/cek")
def cek():
    data = json.load(open(DATA_FILE, encoding="utf-8"))
    kode = request.args.get("kode", "").strip().upper()
    hasil = None
    for p in data["pesanan"]:
        if p["kode"] == kode:
            hasil = p
    return render_template_string("""<html><body style='font-family:Arial;margin:30px'><a href='/'>← semua event</a><h1>Cek Pesanan</h1>
    <form><input name='kode' value='{{ kode }}' placeholder='TIX-...'><button>Cek</button></form>
    {% if p %}<p>{{ p.kode }} · {{ p.event }} {{ p.kategori }} × {{ p.jumlah }} · status <b>{{ p.status }}</b> · total {{ p.total }}</p>{% elif kode %}<p>Tidak ditemukan</p>{% endif %}
    </body></html>""", p=hasil, kode=kode)


# ---------------- API JSON ----------------

@app.route("/api/event")
def api_event():
    data = json.load(open(DATA_FILE, encoding="utf-8"))
    hasil = []
    for e in data["event"]:
        sisa = {}
        for nama_kat, k in e["kategori"].items():
            terjual = sum(p["jumlah"] for p in data["pesanan"] if p["event"] == e["id"] and p["kategori"] == nama_kat and p["status"] == "lunas")
            sisa[nama_kat] = k["kuota"] - terjual
        hasil.append({"id": e["id"], "nama": e["nama"], "tanggal": e["tanggal"], "lokasi": e["lokasi"], "sisa_kuota": sisa})
    return jsonify(hasil)


@app.route("/api/promo/<kode>")
def api_promo(kode):
    data = json.load(open(DATA_FILE, encoding="utf-8"))
    tanggal = request.args.get("tanggal") or datetime.date.today().isoformat()
    for pr in data["promo"]:
        if pr["kode"] == kode.upper():
            if pr["terpakai"] >= pr["kuota"]:
                return jsonify({"kode": pr["kode"], "valid": False, "alasan": "Kuota promo habis"})
            if tanggal > pr["berlaku_sampai"]:
                return jsonify({"kode": pr["kode"], "valid": False, "alasan": "Promo sudah berakhir"})
            return jsonify({"kode": pr["kode"], "valid": True, "persen": pr["persen"], "maks": pr["maks"]})
    return jsonify({"kode": kode.upper(), "valid": False, "alasan": "Kode tidak dikenal"})


@app.route("/api/pesan", methods=["POST"])
def api_pesan():
    data = json.load(open(DATA_FILE, encoding="utf-8"))
    b = request.get_json(silent=True) or {}
    event = next((e for e in data["event"] if e["id"] == b.get("event")), None)
    if event is None:
        return jsonify({"error": "Event tidak ditemukan"}), 404
    nama = str(b.get("nama", "")).strip()
    email = str(b.get("email", "")).strip()
    if nama == "" or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify({"error": "Nama dan email yang valid wajib diisi"}), 400
    jumlah = b.get("jumlah")
    if not isinstance(jumlah, int) or jumlah < 1 or jumlah > 5:
        return jsonify({"error": "Jumlah tiket 1–5 per pesanan"}), 400
    kategori = b.get("kategori")
    if kategori not in event["kategori"]:
        return jsonify({"error": "Kategori tidak tersedia"}), 400
    terjual = 0
    for p in data["pesanan"]:
        if p["event"] == event["id"] and p["kategori"] == kategori and p["status"] == "lunas":
            terjual += p["jumlah"]
    if event["kategori"][kategori]["kuota"] - terjual < jumlah:
        return jsonify({"error": "Kuota tidak mencukupi", "sisa": event["kategori"][kategori]["kuota"] - terjual}), 409
    tgl = datetime.date.fromisoformat(b["tanggal"]) if b.get("tanggal") else datetime.date.today()
    dasar = event["kategori"][kategori]["harga"] * jumlah
    early = dasar * 15 // 100 if (datetime.date.fromisoformat(event["tanggal"]) - tgl).days >= 30 else 0
    kode_promo = str(b.get("promo", "")).upper()
    diskon_promo = 0
    if kode_promo:
        promo = next((pr for pr in data["promo"] if pr["kode"] == kode_promo), None)
        if promo is None or promo["terpakai"] >= promo["kuota"] or tgl.isoformat() > promo["berlaku_sampai"]:
            return jsonify({"error": "Kode promo tidak berlaku"}), 400
        diskon_promo = (dasar - early) * promo["persen"] // 100
        if diskon_promo > promo["maks"]:
            diskon_promo = promo["maks"]
        promo["terpakai"] += 1
    layanan = 5000 * jumlah
    pesanan = {"kode": "TIX-" + event["id"] + "-" + str(len(data["pesanan"]) + 1).zfill(4), "event": event["id"], "kategori": kategori, "jumlah": jumlah,
               "nama": nama, "email": email, "tanggal_pesan": tgl.isoformat(), "harga_dasar": dasar, "diskon_early": early, "diskon_promo": diskon_promo,
               "kode_promo": kode_promo, "biaya_layanan": layanan, "total": dasar - early - diskon_promo + layanan, "status": "lunas", "refund": 0}
    data["pesanan"].append(pesanan)
    json.dump(data, open(DATA_FILE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    return jsonify(pesanan), 201


@app.route("/api/batal", methods=["POST"])
def api_batal():
    data = json.load(open(DATA_FILE, encoding="utf-8"))
    b = request.get_json(silent=True) or {}
    pesanan = next((p for p in data["pesanan"] if p["kode"] == b.get("kode")), None)
    if pesanan is None:
        return jsonify({"error": "Pesanan tidak ditemukan"}), 404
    if pesanan["status"] != "lunas":
        return jsonify({"error": "Pesanan sudah dibatalkan"}), 400
    event = next(e for e in data["event"] if e["id"] == pesanan["event"])
    tgl = datetime.date.fromisoformat(b["tanggal"]) if b.get("tanggal") else datetime.date.today()
    sisa_hari = (datetime.date.fromisoformat(event["tanggal"]) - tgl).days
    if sisa_hari < 1:
        return jsonify({"error": "Pembatalan ditutup pada hari H"}), 400
    bisa_refund = pesanan["total"] - pesanan["biaya_layanan"]
    if sisa_hari >= 7:
        refund = bisa_refund
    else:
        refund = bisa_refund * 50 // 100
    pesanan["status"] = "batal"
    pesanan["refund"] = refund
    json.dump(data, open(DATA_FILE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    return jsonify({"kode": pesanan["kode"], "status": "batal", "refund": refund})


@app.route("/api/laporan/<id_event>")
def api_laporan(id_event):
    data = json.load(open(DATA_FILE, encoding="utf-8"))
    event = next((e for e in data["event"] if e["id"] == id_event), None)
    if event is None:
        return jsonify({"error": "Event tidak ditemukan"}), 404
    per_kategori = {}
    pendapatan = 0
    batal = 0
    total_kuota = 0
    total_terjual = 0
    for nama_kat, k in event["kategori"].items():
        terjual = sum(p["jumlah"] for p in data["pesanan"] if p["event"] == id_event and p["kategori"] == nama_kat and p["status"] == "lunas")
        per_kategori[nama_kat] = {"terjual": terjual, "sisa": k["kuota"] - terjual}
        total_kuota += k["kuota"]
        total_terjual += terjual
    for p in data["pesanan"]:
        if p["event"] == id_event:
            if p["status"] == "lunas":
                pendapatan += p["total"]
            else:
                batal += 1
                pendapatan += p["total"] - p["refund"]
    return jsonify({"event": id_event, "per_kategori": per_kategori, "pendapatan": pendapatan, "pesanan_batal": batal,
                    "okupansi_persen": round(total_terjual / total_kuota * 100, 1)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
