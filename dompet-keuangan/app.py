# Dompet Mahasiswa (pencatatan keuangan pribadi) — aplikasi MONOLITIK: semua kode ada di satu file ini.
# Tugas mahasiswa: pecah menjadi modul tanpa mengubah perilakunya (lihat README.md).
from flask import Flask, request, jsonify, render_template_string, Response, redirect
import json, os, datetime

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

HALAMAN = """
<html><head><title>Dompet Mahasiswa</title>
<style>body{font-family:system-ui;margin:30px;max-width:900px} .angka{font-size:22px;font-weight:bold} .kotak{display:inline-block;padding:12px 18px;margin:6px;border-radius:8px;background:#eef}
.aman{color:green}.waspada{color:#c80}.melebihi{color:#c00} table{border-collapse:collapse} td,th{padding:5px 10px;border-bottom:1px solid #ddd}</style></head>
<body><h1>Dompet Mahasiswa — {{ bulan }}</h1>
<form>Bulan <input type="month" name="bulan" value="{{ bulan }}"><button>Lihat</button> · <a href="/export.csv?bulan={{ bulan }}">Unduh CSV</a></form>
<div class="kotak">Pemasukan<div class="angka">{{ pemasukan }}</div></div><div class="kotak">Pengeluaran<div class="angka">{{ pengeluaran }}</div></div>
<div class="kotak">Selisih<div class="angka">{{ selisih }}</div></div><div class="kotak">Rasio tabungan<div class="angka">{{ rasio }}%</div></div>
<p><i>{{ nasihat }}</i></p>
<h3>Anggaran</h3><table><tr><th>Kategori</th><th>Terpakai</th><th>Anggaran</th><th>%</th><th>Status</th></tr>
{% for a in anggaran %}<tr><td>{{ a.kategori }}</td><td>{{ a.terpakai }}</td><td>{{ a.anggaran }}</td><td>{{ a.persen }}</td><td class="{{ a.status }}">{{ a.status }}</td></tr>{% endfor %}</table>
<h3>Transaksi</h3><table>{% for t in transaksi %}<tr><td>{{ t.tanggal }}</td><td>{{ t.kategori }}</td><td>{{ t.catatan }}</td><td style="text-align:right">{{ t.tampil }}</td></tr>{% endfor %}</table>
<h3>Catat transaksi</h3><p style="color:#c00">{{ pesan }}</p>
<form method="post" action="/tambah">
<input type="date" name="tanggal" required> <select name="jenis"><option>pengeluaran</option><option>pemasukan</option></select>
<select name="kategori">{% for k in kategori %}<option>{{ k.nama }}</option>{% endfor %}</select>
<input type="number" name="jumlah" placeholder="jumlah"> <input name="catatan" placeholder="catatan"> <button>Simpan</button></form>
</body></html>"""


@app.route("/")
def index():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    bulan = request.args.get("bulan", datetime.date.today().strftime("%Y-%m"))
    transaksi = [t for t in data["transaksi"] if t["tanggal"][:7] == bulan]
    pemasukan = sum(t["jumlah"] for t in transaksi if t["jenis"] == "pemasukan")
    pengeluaran = sum(t["jumlah"] for t in transaksi if t["jenis"] == "pengeluaran")
    selisih = pemasukan - pengeluaran
    rasio = round(selisih / pemasukan * 100, 1) if pemasukan > 0 else 0
    if pemasukan == 0:
        nasihat = "Belum ada pemasukan bulan ini."
    elif rasio < 0:
        nasihat = "Pengeluaran melebihi pemasukan! Tinjau ulang kategori yang berstatus melebihi."
    elif rasio < 10:
        nasihat = "Rasio tabungan di bawah 10%. Coba sisihkan di awal bulan."
    elif rasio < 20:
        nasihat = "Cukup baik. Target ideal tabungan 20% dari pemasukan."
    else:
        nasihat = "Hebat! Tabungan Anda di atas 20%."
    anggaran = []
    for k in data["kategori"]:
        if k["jenis"] == "pengeluaran" and k["anggaran"] > 0:
            terpakai = sum(t["jumlah"] for t in transaksi if t["kategori"] == k["nama"] and t["jenis"] == "pengeluaran")
            persen = round(terpakai / k["anggaran"] * 100, 1)
            status = "melebihi" if persen > 100 else ("waspada" if persen >= 80 else "aman")
            anggaran.append({"kategori": k["nama"], "terpakai": "Rp {:,}".format(terpakai).replace(",", "."),
                             "anggaran": "Rp {:,}".format(k["anggaran"]).replace(",", "."), "persen": str(persen) + "%", "status": status})
    for t in transaksi:
        t["tampil"] = ("+" if t["jenis"] == "pemasukan" else "-") + "Rp {:,}".format(t["jumlah"]).replace(",", ".")
    return render_template_string(HALAMAN, bulan=bulan, transaksi=transaksi, kategori=data["kategori"], anggaran=anggaran, nasihat=nasihat,
                                  pemasukan="Rp {:,}".format(pemasukan).replace(",", "."), pengeluaran="Rp {:,}".format(pengeluaran).replace(",", "."),
                                  selisih="Rp {:,}".format(selisih).replace(",", "."), rasio=rasio, pesan=request.args.get("pesan", ""))


@app.route("/tambah", methods=["POST"])
def tambah():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    tanggal = request.form.get("tanggal", "")
    jenis = request.form.get("jenis", "")
    kategori = request.form.get("kategori", "")
    try:
        jumlah = int(request.form.get("jumlah", "0"))
    except ValueError:
        jumlah = 0
    kat = [k for k in data["kategori"] if k["nama"] == kategori]
    if jumlah <= 0:
        return redirect("/?pesan=Jumlah harus lebih dari 0")
    if len(kat) == 0 or kat[0]["jenis"] != jenis:
        return redirect("/?pesan=Kategori tidak sesuai jenis transaksi")
    nomor = max([int(t["id"][1:]) for t in data["transaksi"]] + [0]) + 1
    data["transaksi"].append({"id": "T" + str(nomor).zfill(3), "tanggal": tanggal, "jenis": jenis, "kategori": kategori, "jumlah": jumlah, "catatan": request.form.get("catatan", "")})
    f = open(DATA_FILE, "w", encoding="utf-8")
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.close()
    return redirect("/?bulan=" + tanggal[:7])


@app.route("/export.csv")
def export_csv():
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    bulan = request.args.get("bulan", datetime.date.today().strftime("%Y-%m"))
    isi = "id;tanggal;jenis;kategori;jumlah;catatan\n"
    for t in data["transaksi"]:
        if t["tanggal"][:7] == bulan:
            isi += ";".join([t["id"], t["tanggal"], t["jenis"], t["kategori"], str(t["jumlah"]), t["catatan"].replace(";", ",")]) + "\n"
    return Response(isi, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=dompet-" + bulan + ".csv"})


# ---------------- API JSON (satu pintu untuk semua aksi) ----------------

@app.route("/api/<aksi>", methods=["GET", "POST"])
def api(aksi):
    f = open(DATA_FILE, encoding="utf-8")
    data = json.load(f)
    f.close()
    bulan = request.args.get("bulan", datetime.date.today().strftime("%Y-%m"))
    if aksi == "transaksi" and request.method == "GET":
        return jsonify([t for t in data["transaksi"] if t["tanggal"][:7] == bulan])
    elif aksi == "transaksi" and request.method == "POST":
        b = request.get_json(silent=True) or {}
        try:
            datetime.date.fromisoformat(b.get("tanggal", ""))
        except ValueError:
            return jsonify({"error": "Tanggal tidak valid"}), 400
        if not isinstance(b.get("jumlah"), int) or b["jumlah"] <= 0:
            return jsonify({"error": "Jumlah harus bilangan bulat > 0"}), 400
        kat = None
        for k in data["kategori"]:
            if k["nama"] == b.get("kategori"):
                kat = k
        if kat is None:
            return jsonify({"error": "Kategori tidak dikenal"}), 400
        if kat["jenis"] != b.get("jenis"):
            return jsonify({"error": "Kategori " + kat["nama"] + " adalah " + kat["jenis"]}), 400
        nomor = max([int(t["id"][1:]) for t in data["transaksi"]] + [0]) + 1
        baru = {"id": "T" + str(nomor).zfill(3), "tanggal": b["tanggal"], "jenis": b["jenis"], "kategori": b["kategori"], "jumlah": b["jumlah"], "catatan": b.get("catatan", "")}
        data["transaksi"].append(baru)
        f = open(DATA_FILE, "w", encoding="utf-8")
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.close()
        return jsonify(baru), 201
    elif aksi == "hapus" and request.method == "POST":
        id_t = (request.get_json(silent=True) or {}).get("id")
        sisa = [t for t in data["transaksi"] if t["id"] != id_t]
        if len(sisa) == len(data["transaksi"]):
            return jsonify({"error": "Transaksi tidak ditemukan"}), 404
        data["transaksi"] = sisa
        f = open(DATA_FILE, "w", encoding="utf-8")
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.close()
        return jsonify({"dihapus": id_t})
    elif aksi == "ringkasan":
        transaksi = [t for t in data["transaksi"] if t["tanggal"][:7] == bulan]
        pemasukan = 0
        pengeluaran = 0
        for t in transaksi:
            if t["jenis"] == "pemasukan":
                pemasukan += t["jumlah"]
            else:
                pengeluaran += t["jumlah"]
        saldo = 0
        for t in data["transaksi"]:
            if t["jenis"] == "pemasukan":
                saldo += t["jumlah"]
            else:
                saldo -= t["jumlah"]
        rasio = round((pemasukan - pengeluaran) / pemasukan * 100, 1) if pemasukan > 0 else 0
        return jsonify({"bulan": bulan, "pemasukan": pemasukan, "pengeluaran": pengeluaran, "selisih": pemasukan - pengeluaran, "rasio_tabungan": rasio, "saldo_total": saldo})
    elif aksi == "kategori":
        transaksi = [t for t in data["transaksi"] if t["tanggal"][:7] == bulan and t["jenis"] == "pengeluaran"]
        total = sum(t["jumlah"] for t in transaksi)
        per = {}
        for t in transaksi:
            per[t["kategori"]] = per.get(t["kategori"], 0) + t["jumlah"]
        hasil = [{"kategori": k, "jumlah": v, "persen": round(v / total * 100, 1)} for k, v in per.items()]
        hasil.sort(key=lambda x: x["jumlah"], reverse=True)
        return jsonify(hasil)
    elif aksi == "anggaran":
        hasil = []
        for k in data["kategori"]:
            if k["jenis"] == "pengeluaran" and k["anggaran"] > 0:
                terpakai = 0
                for t in data["transaksi"]:
                    if t["tanggal"][:7] == bulan and t["kategori"] == k["nama"] and t["jenis"] == "pengeluaran":
                        terpakai += t["jumlah"]
                persen = round(terpakai / k["anggaran"] * 100, 1)
                if persen > 100:
                    status = "melebihi"
                elif persen >= 80:
                    status = "waspada"
                else:
                    status = "aman"
                hasil.append({"kategori": k["nama"], "anggaran": k["anggaran"], "terpakai": terpakai, "sisa": k["anggaran"] - terpakai, "persen": persen, "status": status})
        return jsonify(hasil)
    else:
        return jsonify({"error": "Aksi tidak dikenal: " + aksi}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
