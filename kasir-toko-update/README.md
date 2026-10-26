# Kasir Toko — Modular

Versi ini memisahkan aplikasi ke rute, layanan, repositori, konfigurasi, dan template HTML.

## Menjalankan lokal
```bash
pip install -r requirements.txt
python app.py
```
Buka http://localhost:5000.

## Menjalankan dengan Docker
```bash
docker compose up --build
```
Buka http://localhost:5001.

## Struktur
- `app.py`: membuat Flask dan mendaftarkan Blueprint.
- `config.py`: konfigurasi aplikasi.
- `repositori/`: akses baca/tulis JSON.
- `layanan/`: aturan bisnis produk, transaksi, dan laporan.
- `rute/`: endpoint web dan API.
- `templates/`: halaman HTML.
