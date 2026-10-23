# Kuis Online

**Tipe aplikasi:** E-learning / penilaian · **Port:** http://localhost:5006

Kuis daring: mengerjakan soal pilihan ganda dan isian, koreksi otomatis berbobot, nilai huruf, statistik kelas, analisis butir soal.

> ⚠️ Aplikasi ini **sengaja dibuat monolitik**: seluruh kode (akses data JSON, aturan bisnis, validasi, HTML, dan API) bercampur di satu file `app.py`. Tugas Anda adalah memecahnya menjadi modul **tanpa mengubah perilakunya**. Panduan lengkap: [`../README.md`](../README.md).

## Menjalankan

Aplikasi ini punya `docker-compose.yml` sendiri. Jalankan dari **folder ini**:

```bash
docker compose up --build
# buka http://localhost:5006
```

Tanpa Docker: `pip install -r requirements.txt`, lalu `python app.py` (port 5000).

## Cek Cepat Sebelum & Sesudah Dimodularisasi

Jalankan perintah berikut **sebelum** mengubah kode, catat hasilnya, lalu ulangi **sesudah** modularisasi. Hasilnya harus sama.

```bash
curl -s localhost:5006/api/kuis/K01/statistik
```
Hasil: `rata_rata` 81.7, `tertinggi` 100, `terendah` 55, `persen_lulus` 66.7

```bash
curl -s -X POST localhost:5006/kuis/K01/jawab -H 'Content-Type: application/json' \
  -d '{"nim":"2310100004","jawaban":{"1":"B","2":"C","3":"D","4":"print","5":"len","6":"B"}}'
```
Hasil: `skor` 70.0, `huruf` B, `lulus` true, `benar` 5

Data contoh ikut berubah setiap ada transaksi. Kembalikan dengan `git checkout -- data.json` sebelum mengecek ulang.

## Aturan Bisnis

Semua aturan ini saat ini tertulis **langsung di dalam fungsi route** (sebagian tertulis lebih dari sekali).

1. Soal dikirim ke peserta **tanpa kunci jawaban**
2. NIM harus **10 digit angka**
3. Jumlah percobaan dibatasi per kuis (`maks_percobaan`)
4. Koreksi pilihan ganda: huruf jawaban, tidak peka huruf besar/kecil
5. Koreksi isian: spasi di tepi diabaikan, tidak peka huruf besar/kecil, boleh lebih dari satu kunci
6. **Skor berbobot** = poin benar ÷ total bobot × 100 (1 desimal); soal kosong = salah
7. Nilai huruf: **A ≥ 85, B ≥ 70, C ≥ 55, D ≥ 40, E**; lulus jika skor ≥ `nilai_lulus`
8. Statistik memakai **nilai terbaik per NIM**: rata-rata, tertinggi, terendah, % lulus, distribusi huruf
9. Analisis butir: % benar per soal → **mudah** (≥ 80%), **sedang** (≥ 40%), **sulit**
10. Peringkat 5 besar dengan NIM disamarkan (`2310****01`)

## Daftar Route

| Method | URL | Keterangan |
|--------|-----|------------|
| GET | `/` | Daftar kuis |
| GET | `/kuis/<id>` | Form mengerjakan |
| POST | `/kuis/<id>/jawab` | Kirim jawaban (form **atau** JSON `{nim, jawaban:{no: jawab}}`) |
| GET | `/kuis/<id>/statistik` | Statistik (web) |
| GET | `/api/kuis` | Daftar kuis (JSON) |
| GET | `/api/kuis/<id>` | Soal tanpa kunci |
| GET | `/api/kuis/<id>/statistik` | Statistik (JSON) |
| GET | `/api/kuis/<id>/analisis` | Analisis butir |
| GET | `/api/kuis/<id>/peringkat` | Peringkat |

## File

| File | Isi |
|------|-----|
| `app.py` | Seluruh aplikasi (monolitik) |
| `data.json` | Data contoh (berubah setiap ada transaksi) |
| `Dockerfile`, `requirements.txt` | Image Python 3.12 + Flask |
| `docker-compose.yml` | Menjalankan aplikasi ini di port 5006; folder di-mount ke container sehingga perubahan kode langsung terbaca |
