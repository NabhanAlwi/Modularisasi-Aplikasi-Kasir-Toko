# Kasir Toko

**Tipe aplikasi:** Point of Sale (ritel) · **Port:** http://localhost:5001

Kasir minimarket: daftar produk, transaksi dengan diskon member dan PPN, struk, laporan harian, peringatan stok.

> ⚠️ Aplikasi ini **sengaja dibuat monolitik**: seluruh kode (akses data JSON, aturan bisnis, validasi, HTML, dan API) bercampur di satu file `app.py`. Tugas Anda adalah memecahnya menjadi modul **tanpa mengubah perilakunya**. Panduan lengkap: [`../README.md`](../README.md).

## Menjalankan

Aplikasi ini punya `docker-compose.yml` sendiri. Jalankan dari **folder ini**:

```bash
docker compose up --build
# buka http://localhost:5001
```

Tanpa Docker: `pip install -r requirements.txt`, lalu `python app.py` (port 5000).

## Cek Cepat Sebelum & Sesudah Dimodularisasi

Jalankan perintah berikut **sebelum** mengubah kode, catat hasilnya, lalu ulangi **sesudah** modularisasi. Hasilnya harus sama.

```bash
curl -s 'localhost:5001/api/laporan?tanggal=2026-10-01'
```
Hasil: `jumlah_transaksi` 2, `omzet` 230824, terlaris Mi Instan (10)

```bash
curl -s -X POST localhost:5001/api/transaksi -H 'Content-Type: application/json' \
  -d '{"member":"M001","items":[{"kode":"P001","qty":2}],"bayar":200000,"tanggal":"2026-10-02"}'
```
Hasil: `subtotal` 156000, `diskon` 15600, `ppn` 15444, `total` 155844, `kembali` 44156

Data contoh ikut berubah setiap ada transaksi. Kembalikan dengan `git checkout -- data.json` sebelum mengecek ulang.

## Aturan Bisnis

Semua aturan ini saat ini tertulis **langsung di dalam fungsi route** (sebagian tertulis lebih dari sekali).

1. Diskon member **gold 10%**, **silver 5%**; belanja ≥ Rp 1.000.000 mendapat tambahan **5%**; total diskon **maksimal 15%**
2. **PPN 11%** dihitung dari (subtotal − diskon)
3. Validasi item: kode produk harus ada, jumlah > 0, stok mencukupi
4. Stok produk berkurang setelah transaksi berhasil
5. Uang bayar harus ≥ total; kembalian = bayar − total
6. Nomor struk `TRX-YYYYMMDD-NNN`, urut per hari
7. Laporan harian: jumlah transaksi, omzet, 3 produk terlaris
8. Produk dengan stok < 5 ditandai **stok menipis**
9. Semua uang ditampilkan dalam format `Rp 1.234.567`

## Daftar Route

| Method | URL | Keterangan |
|--------|-----|------------|
| GET | `/` | Daftar produk + peringatan stok menipis |
| GET, POST | `/transaksi` | Form transaksi (item ditulis `KODE,JUMLAH` per baris) |
| GET | `/laporan?tanggal=` | Laporan harian |
| GET | `/api/produk?kategori=` | Daftar produk (filter kategori) |
| POST | `/api/transaksi` | `{member, items:[{kode, qty}], bayar, tanggal?}` |
| GET | `/api/laporan?tanggal=` | Laporan harian (JSON) |
| GET | `/api/stok-menipis` | Produk dengan stok < 5 |

## File

| File | Isi |
|------|-----|
| `app.py` | Seluruh aplikasi (monolitik) |
| `data.json` | Data contoh (berubah setiap ada transaksi) |
| `Dockerfile`, `requirements.txt` | Image Python 3.12 + Flask |
| `docker-compose.yml` | Menjalankan aplikasi ini di port 5001; folder di-mount ke container sehingga perubahan kode langsung terbaca |
