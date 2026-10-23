# Reservasi Klinik

**Tipe aplikasi:** Booking / penjadwalan · **Port:** http://localhost:5003

Pemesanan jadwal dokter: daftar dokter per poli, slot praktik, reservasi dengan nomor antrian dan biaya, pembatalan, rekap harian.

> ⚠️ Aplikasi ini **sengaja dibuat monolitik**: seluruh kode (akses data JSON, aturan bisnis, validasi, HTML, dan API) bercampur di satu file `app.py`. Tugas Anda adalah memecahnya menjadi modul **tanpa mengubah perilakunya**. Panduan lengkap: [`../README.md`](../README.md).

## Menjalankan

Aplikasi ini punya `docker-compose.yml` sendiri. Jalankan dari **folder ini**:

```bash
docker compose up --build
# buka http://localhost:5003
```

Tanpa Docker: `pip install -r requirements.txt`, lalu `python app.py` (port 5000).

## Cek Cepat Sebelum & Sesudah Dimodularisasi

Jalankan perintah berikut **sebelum** mengubah kode, catat hasilnya, lalu ulangi **sesudah** modularisasi. Hasilnya harus sama.

```bash
curl -s 'localhost:5003/api/slot?dokter=D01&tanggal=2026-10-26'
```
Hasil: hari `senin`, 11 slot kosong dimulai `08:20`

```bash
curl -s -X POST localhost:5003/api/reservasi -H 'Content-Type: application/json' \
  -d '{"no_rm":"RM0004","dokter":"D01","tanggal":"2026-10-26","jam":"10:00"}'
```
Hasil: `umur` 60, `biaya` 65000, `antrian` 3

Data contoh ikut berubah setiap ada transaksi. Kembalikan dengan `git checkout -- data.json` sebelum mengecek ulang.

## Aturan Bisnis

Semua aturan ini saat ini tertulis **langsung di dalam fungsi route** (sebagian tertulis lebih dari sekali).

1. Nama hari (senin … minggu) ditentukan dari tanggal; dokter hanya bisa dipesan pada hari praktiknya
2. Jadwal praktik dibagi menjadi **slot 20 menit**; slot terisi hanya dihitung dari reservasi berstatus aktif
3. Satu pasien hanya boleh punya satu reservasi aktif per dokter per tanggal
4. Umur pasien dihitung pada tanggal kunjungan
5. Biaya: pasien **BPJS gratis**; non-BPJS = tarif dokter, **lansia (≥ 60 th) diskon 20%**, ditambah **admin Rp 5.000**
6. Nomor antrian = jumlah reservasi dokter pada tanggal itu + 1
7. Kode reservasi `RSV-<dokter>-<YYYYMMDD>-<antrian>`
8. Pembatalan paling lambat **H-1**
9. Rekap harian per poli: jumlah pasien dan pendapatan

## Daftar Route

| Method | URL | Keterangan |
|--------|-----|------------|
| GET | `/?poli=` | Daftar dokter |
| GET, POST | `/reservasi` | Form reservasi |
| GET | `/rekap?tanggal=` | Rekap harian |
| GET | `/api/dokter?poli=` | Daftar dokter (JSON) |
| GET | `/api/slot?dokter=&tanggal=` | Slot kosong |
| POST | `/api/reservasi` | `{no_rm, dokter, tanggal, jam}` |
| POST | `/api/batal` | `{kode, hari_ini?}` |
| GET | `/api/rekap?tanggal=` | Rekap per poli (JSON) |

## File

| File | Isi |
|------|-----|
| `app.py` | Seluruh aplikasi (monolitik) |
| `data.json` | Data contoh (berubah setiap ada transaksi) |
| `Dockerfile`, `requirements.txt` | Image Python 3.12 + Flask |
| `docker-compose.yml` | Menjalankan aplikasi ini di port 5003; folder di-mount ke container sehingga perubahan kode langsung terbaca |
