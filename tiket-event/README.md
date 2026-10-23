# Tiket Event Kampus

**Tipe aplikasi:** E-ticketing / pemesanan · **Port:** http://localhost:5005

Pemesanan tiket seminar, konser, dan workshop: kuota per kategori, early bird, kode promo, pembatalan dengan refund, laporan penjualan.

> ⚠️ Aplikasi ini **sengaja dibuat monolitik**: seluruh kode (akses data JSON, aturan bisnis, validasi, HTML, dan API) bercampur di satu file `app.py`. Tugas Anda adalah memecahnya menjadi modul **tanpa mengubah perilakunya**. Panduan lengkap: [`../README.md`](../README.md).

## Menjalankan

Aplikasi ini punya `docker-compose.yml` sendiri. Jalankan dari **folder ini**:

```bash
docker compose up --build
# buka http://localhost:5005
```

Tanpa Docker: `pip install -r requirements.txt`, lalu `python app.py` (port 5000).

## Cek Cepat Sebelum & Sesudah Dimodularisasi

Jalankan perintah berikut **sebelum** mengubah kode, catat hasilnya, lalu ulangi **sesudah** modularisasi. Hasilnya harus sama.

```bash
curl -s localhost:5005/api/laporan/E03
```
Hasil: `pendapatan` 785000, `pesanan_batal` 1, `okupansi_persen` 16.7

```bash
curl -s -X POST localhost:5005/api/pesan -H 'Content-Type: application/json' \
  -d '{"event":"E01","kategori":"VIP","jumlah":2,"nama":"Uji","email":"uji@mail.com","promo":"MHS10","tanggal":"2026-10-20"}'
```
Hasil: `diskon_early` 75000, `diskon_promo` 30000, `total` 405000

Data contoh ikut berubah setiap ada transaksi. Kembalikan dengan `git checkout -- data.json` sebelum mengecek ulang.

## Aturan Bisnis

Semua aturan ini saat ini tertulis **langsung di dalam fungsi route** (sebagian tertulis lebih dari sekali).

1. Sisa kuota = kuota − tiket dari pesanan berstatus lunas
2. Validasi pemesan: nama wajib, email valid, jumlah **1–5 tiket** per pesanan
3. **Early bird**: dipesan ≥ 30 hari sebelum event → diskon **15%** dari harga dasar
4. **Kode promo**: berlaku jika kuota promo belum habis dan belum lewat masa berlaku; diskon persen dari harga setelah early bird, **dibatasi nilai maksimal**
5. **Biaya layanan Rp 5.000 per tiket**
6. Kode pesanan `TIX-<event>-nnnn`
7. Refund: ≥ 7 hari sebelum event **100%**, 1–6 hari **50%** (biaya layanan tidak dikembalikan); hari H tidak bisa batal
8. Laporan per event: terjual & sisa per kategori, pendapatan, pesanan batal, okupansi
9. Tanggal ditampilkan dalam format Indonesia (5 Des 2026)

## Daftar Route

| Method | URL | Keterangan |
|--------|-----|------------|
| GET | `/` | Daftar event |
| GET, POST | `/event/<id>` | Detail & form pesan |
| GET | `/cek?kode=` | Cek pesanan |
| GET | `/api/event` | Daftar event + sisa kuota |
| GET | `/api/promo/<kode>?tanggal=` | Cek kode promo |
| POST | `/api/pesan` | `{event, kategori, jumlah, nama, email, promo?, tanggal?}` |
| POST | `/api/batal` | `{kode, tanggal?}` |
| GET | `/api/laporan/<id>` | Laporan penjualan event |

## File

| File | Isi |
|------|-----|
| `app.py` | Seluruh aplikasi (monolitik) |
| `data.json` | Data contoh (berubah setiap ada transaksi) |
| `Dockerfile`, `requirements.txt` | Image Python 3.12 + Flask |
| `docker-compose.yml` | Menjalankan aplikasi ini di port 5005; folder di-mount ke container sehingga perubahan kode langsung terbaca |
