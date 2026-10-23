# Donasi ZIS & Wakaf

**Tipe aplikasi:** Filantropi / kalkulator · **Port:** http://localhost:5007

Penghimpunan zakat, infaq, sedekah, dan wakaf: progres program, donasi dengan biaya admin per metode, kalkulator zakat, laporan bulanan.

> ⚠️ Aplikasi ini **sengaja dibuat monolitik**: seluruh kode (akses data JSON, aturan bisnis, validasi, HTML, dan API) bercampur di satu file `app.py`. Tugas Anda adalah memecahnya menjadi modul **tanpa mengubah perilakunya**. Panduan lengkap: [`../README.md`](../README.md).

## Menjalankan

Aplikasi ini punya `docker-compose.yml` sendiri. Jalankan dari **folder ini**:

```bash
docker compose up --build
# buka http://localhost:5007
```

Tanpa Docker: `pip install -r requirements.txt`, lalu `python app.py` (port 5000).

## Cek Cepat Sebelum & Sesudah Dimodularisasi

Jalankan perintah berikut **sebelum** mengubah kode, catat hasilnya, lalu ulangi **sesudah** modularisasi. Hasilnya harus sama.

```bash
curl -s 'localhost:5007/api/laporan?bulan=2026-10'
```
Hasil: `total` 13250000, `total_biaya_admin` 9250, `jumlah_donasi` 4

```bash
curl -s -X POST localhost:5007/api/zakat/maal -H 'Content-Type: application/json' \
  -d '{"tabungan":100000000,"emas":40000000,"utang":10000000,"haul":true}'
```
Hasil: `harta_bersih` 130000000, `wajib` true, `zakat` 3250000

Data contoh ikut berubah setiap ada transaksi. Kembalikan dengan `git checkout -- data.json` sebelum mengecek ulang.

## Aturan Bisnis

Semua aturan ini saat ini tertulis **langsung di dalam fungsi route** (sebagian tertulis lebih dari sekali).

1. Progres program = Σ dana diterima (donasi berhasil) ÷ target × 100
2. Donasi **minimal Rp 10.000**; nama wajib kecuali memilih anonim
3. Biaya admin: **QRIS 0,7%** (dibulatkan), **virtual account Rp 4.000**, **transfer Rp 0**; dana diterima = jumlah − biaya admin
4. Nomor kuitansi `ZIS/YYYY/MM/nnnn`
5. Donatur anonim ditampilkan sebagai **Hamba Allah**
6. **Zakat penghasilan**: nisab bulanan = 85 gram emas ÷ 12; wajib jika penghasilan ≥ nisab; zakat **2,5%**
7. **Zakat maal**: harta bersih = harta − utang jatuh tempo; wajib jika ≥ nisab 85 gram emas **dan** sudah haul (1 tahun); zakat **2,5%**
8. Harga emas per gram dapat diubah (memengaruhi nisab)
9. Laporan bulanan: total per jenis (zakat/infaq/sedekah/wakaf), biaya admin, jumlah donasi

## Daftar Route

| Method | URL | Keterangan |
|--------|-----|------------|
| GET | `/` | Daftar program + progres |
| GET, POST | `/donasi/<id>` | Form donasi + donatur terbaru |
| GET, POST | `/kalkulator` | Kalkulator zakat |
| GET | `/laporan?bulan=` | Laporan (web) |
| GET | `/api/program` | Program + progres (JSON) |
| POST | `/api/donasi` | `{program, nama, anonim?, jumlah, metode, tanggal?}` |
| GET | `/api/program/<id>/donatur` | Donatur terbaru |
| POST | `/api/zakat/penghasilan` | `{gaji, pendapatan_lain?}` |
| POST | `/api/zakat/maal` | `{tabungan, emas, investasi?, utang, haul}` |
| POST | `/api/pengaturan/emas` | `{harga_emas_per_gram}` |
| GET | `/api/laporan?bulan=` | Laporan bulanan (JSON) |

## File

| File | Isi |
|------|-----|
| `app.py` | Seluruh aplikasi (monolitik) |
| `data.json` | Data contoh (berubah setiap ada transaksi) |
| `Dockerfile`, `requirements.txt` | Image Python 3.12 + Flask |
| `docker-compose.yml` | Menjalankan aplikasi ini di port 5007; folder di-mount ke container sehingga perubahan kode langsung terbaca |
