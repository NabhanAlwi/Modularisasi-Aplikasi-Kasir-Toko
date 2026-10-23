# Kuis Online (e-learning) — aplikasi MONOLITIK: semua kode ada di satu file ini.
# Tugas mahasiswa: pecah menjadi modul tanpa mengubah perilakunya (lihat README.md).
from flask import Flask, request, jsonify, render_template_string
import json, os, datetime, re

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


@app.route("/")
def index():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return render_template_string("""<html><head><title>Kuis Online</title></head><body style="font-family:Tahoma;margin:30px;background:#fafaf5">
    <h1>📝 Kuis Online</h1>{% for k in kuis %}<div style="background:white;padding:12px;margin:10px 0;border:1px solid #ddd">
    <b>{{ k.judul }}</b> — {{ k.soal|length }} soal · lulus ≥ {{ k.nilai_lulus }} · maks {{ k.maks_percobaan }} percobaan<br>
    <a href="/kuis/{{ k.id }}">Kerjakan</a> · <a href="/kuis/{{ k.id }}/statistik">Statistik</a></div>{% endfor %}</body></html>""", kuis=data["kuis"])


@app.route("/kuis/<id_kuis>")
def kerjakan(id_kuis):
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    kuis = None
    for k in data["kuis"]:
        if k["id"] == id_kuis:
            kuis = k
    if kuis is None:
        return "Kuis tidak ditemukan", 404
    form = ""
    for s in kuis["soal"]:
        form += "<p><b>" + str(s["no"]) + ". " + s["pertanyaan"] + "</b> <small>(" + str(s["bobot"]) + " poin)</small><br>"
        if s["tipe"] == "pg":
            for p in s["pilihan"]:
                form += "<label><input type='radio' name='" + str(s["no"]) + "' value='" + p[0] + "'> " + p + "</label><br>"
        else:
            form += "<input name='" + str(s["no"]) + "'>"
        form += "</p>"
    return "<html><body style='font-family:Tahoma;margin:30px'><h1>" + kuis["judul"] + "</h1><form method='post' action='/kuis/" + id_kuis + "/jawab'>NIM <input name='nim'>" + form + "<button>Kirim jawaban</button></form></body></html>"


@app.route("/kuis/<id_kuis>/jawab", methods=["POST"])
def jawab(id_kuis):
    # dipakai oleh form web DAN oleh API (request JSON)
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    if request.is_json:
        nim = str(request.get_json().get("nim", ""))
        jawaban = {str(k): str(v) for k, v in request.get_json().get("jawaban", {}).items()}
    else:
        nim = request.form.get("nim", "")
        jawaban = {k: v for k, v in request.form.items() if k != "nim"}
    kuis = None
    for k in data["kuis"]:
        if k["id"] == id_kuis:
            kuis = k
    if kuis is None:
        return (jsonify({"error": "Kuis tidak ditemukan"}), 404) if request.is_json else ("Kuis tidak ditemukan", 404)
    if not re.fullmatch(r"\d{10}", nim):
        return (jsonify({"error": "NIM harus 10 digit angka"}), 400) if request.is_json else ("NIM harus 10 digit angka", 400)
    percobaan = len([h for h in data["hasil"] if h["kuis"] == id_kuis and h["nim"] == nim]) + 1
    if percobaan > kuis["maks_percobaan"]:
        pesan = "Batas percobaan (" + str(kuis["maks_percobaan"]) + "x) sudah habis"
        return (jsonify({"error": pesan}), 403) if request.is_json else (pesan, 403)
    poin = 0
    total_bobot = 0
    benar = 0
    for s in kuis["soal"]:
        total_bobot += s["bobot"]
        j = jawaban.get(str(s["no"]), "")
        if s["tipe"] == "pg":
            ok = j.strip().upper() == s["kunci"]
        else:
            ok = j.strip().lower() in [x.lower() for x in s["kunci"]]
        if ok:
            poin += s["bobot"]
            benar += 1
    skor = round(poin / total_bobot * 100, 1)
    if skor >= 85:
        huruf = "A"
    elif skor >= 70:
        huruf = "B"
    elif skor >= 55:
        huruf = "C"
    elif skor >= 40:
        huruf = "D"
    else:
        huruf = "E"
    hasil = {"id": "H" + str(len(data["hasil"]) + 1).zfill(3), "kuis": id_kuis, "nim": nim, "jawaban": jawaban, "skor": skor, "huruf": huruf,
             "lulus": skor >= kuis["nilai_lulus"], "percobaan": percobaan, "waktu": datetime.datetime.now().isoformat(timespec="seconds")}
    data["hasil"].append(hasil)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    if request.is_json:
        return jsonify({"id": hasil["id"], "skor": skor, "huruf": huruf, "lulus": hasil["lulus"], "benar": benar, "total_soal": len(kuis["soal"]), "percobaan": percobaan}), 201
    return "<html><body style='font-family:Tahoma;margin:30px'><h1>Hasil</h1><p>Skor: <b>" + str(skor) + "</b> (" + huruf + ") — " + ("LULUS" if hasil["lulus"] else "belum lulus") + "<br>Benar " + str(benar) + " dari " + str(len(kuis["soal"])) + " soal · percobaan ke-" + str(percobaan) + "</p><a href='/'>Kembali</a></body></html>"


@app.route("/kuis/<id_kuis>/statistik")
def statistik_web(id_kuis):
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    terbaik = {}
    for h in data["hasil"]:
        if h["kuis"] == id_kuis:
            if h["nim"] not in terbaik or h["skor"] > terbaik[h["nim"]]["skor"]:
                terbaik[h["nim"]] = h
    nilai = [h["skor"] for h in terbaik.values()]
    if len(nilai) == 0:
        return "<html><body style='font-family:Tahoma;margin:30px'><h1>Statistik</h1><p>Belum ada peserta.</p></body></html>"
    rata = round(sum(nilai) / len(nilai), 1)
    lulus = len([h for h in terbaik.values() if h["lulus"]])
    baris = ""
    for i, h in enumerate(sorted(terbaik.values(), key=lambda x: (-x["skor"], x["nim"]))[:5]):
        baris += "<tr><td>" + str(i + 1) + "</td><td>" + h["nim"][:4] + "****" + h["nim"][-2:] + "</td><td>" + str(h["skor"]) + "</td><td>" + h["huruf"] + "</td></tr>"
    return ("<html><body style='font-family:Tahoma;margin:30px'><h1>Statistik " + id_kuis + "</h1><p>Peserta: " + str(len(nilai)) + " · rata-rata " + str(rata)
            + " · tertinggi " + str(max(nilai)) + " · terendah " + str(min(nilai)) + " · lulus " + str(round(lulus / len(nilai) * 100, 1)) + "%</p>"
            + "<h3>5 besar</h3><table border='1' cellpadding='5'>" + baris + "</table></body></html>")


# ---------------- API JSON ----------------

@app.route("/api/kuis")
def api_daftar():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return jsonify([{"id": k["id"], "judul": k["judul"], "jumlah_soal": len(k["soal"]), "nilai_lulus": k["nilai_lulus"]} for k in data["kuis"]])


@app.route("/api/kuis/<id_kuis>")
def api_soal(id_kuis):
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    for k in data["kuis"]:
        if k["id"] == id_kuis:
            soal = []
            for s in k["soal"]:
                tanpa_kunci = dict(s)
                del tanpa_kunci["kunci"]
                soal.append(tanpa_kunci)
            return jsonify({"id": k["id"], "judul": k["judul"], "maks_percobaan": k["maks_percobaan"], "soal": soal})
    return jsonify({"error": "Kuis tidak ditemukan"}), 404


@app.route("/api/kuis/<id_kuis>/statistik")
def api_statistik(id_kuis):
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    terbaik = {}
    for h in data["hasil"]:
        if h["kuis"] == id_kuis:
            if h["nim"] not in terbaik or h["skor"] > terbaik[h["nim"]]["skor"]:
                terbaik[h["nim"]] = h
    nilai = [h["skor"] for h in terbaik.values()]
    if not nilai:
        return jsonify({"peserta": 0})
    distribusi = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
    for h in terbaik.values():
        distribusi[h["huruf"]] += 1
    return jsonify({"peserta": len(nilai), "rata_rata": round(sum(nilai) / len(nilai), 1), "tertinggi": max(nilai), "terendah": min(nilai),
                    "persen_lulus": round(len([h for h in terbaik.values() if h["lulus"]]) / len(nilai) * 100, 1), "distribusi": distribusi})


@app.route("/api/kuis/<id_kuis>/analisis")
def api_analisis(id_kuis):
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    kuis = next((k for k in data["kuis"] if k["id"] == id_kuis), None)
    if kuis is None:
        return jsonify({"error": "Kuis tidak ditemukan"}), 404
    semua = [h for h in data["hasil"] if h["kuis"] == id_kuis]
    hasil = []
    for s in kuis["soal"]:
        benar = 0
        for h in semua:
            j = h["jawaban"].get(str(s["no"]), "")
            if s["tipe"] == "pg":
                if j.strip().upper() == s["kunci"]:
                    benar += 1
            else:
                if j.strip().lower() in [x.lower() for x in s["kunci"]]:
                    benar += 1
        persen = round(benar / len(semua) * 100, 1) if semua else 0
        if persen >= 80:
            tingkat = "mudah"
        elif persen >= 40:
            tingkat = "sedang"
        else:
            tingkat = "sulit"
        hasil.append({"no": s["no"], "persen_benar": persen, "tingkat": tingkat})
    return jsonify(hasil)


@app.route("/api/kuis/<id_kuis>/peringkat")
def api_peringkat(id_kuis):
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    terbaik = {}
    for h in data["hasil"]:
        if h["kuis"] == id_kuis:
            if h["nim"] not in terbaik or h["skor"] > terbaik[h["nim"]]["skor"]:
                terbaik[h["nim"]] = h
    urut = sorted(terbaik.values(), key=lambda x: (-x["skor"], x["nim"]))[:5]
    return jsonify([{"peringkat": i + 1, "nim": h["nim"][:4] + "****" + h["nim"][-2:], "skor": h["skor"]} for i, h in enumerate(urut)])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
