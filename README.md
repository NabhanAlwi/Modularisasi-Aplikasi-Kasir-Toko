
## Dokumentasi Pengujian

Pengujian aplikasi Kasir Toko dilakukan menggunakan
library unittest pada Python. Pengujian terdiri dari
Unit Testing dan Integration Testing.

### 1. Unit Testing

#### A. Produk Service

Pengujian dilakukan untuk memastikan fungsi pengelolaan
produk berjalan dengan baik, meliputi daftar produk,
filter kategori, dan pemeriksaan stok menipis.

![Produk Service](docs/screenshots/test-produk-service.png)

#### B. Transaksi Service

Pengujian dilakukan terhadap proses pencarian produk,
perhitungan diskon, pembuatan nomor transaksi,
validasi pembayaran, dan pemrosesan transaksi web maupun API.

![Transaksi Service](docs/screenshots/test-transaksi-service.png)

#### C. Laporan Service

Pengujian dilakukan untuk memastikan laporan harian,
omzet, jumlah transaksi, dan produk terlaris
dapat dihitung dengan benar.

![Laporan Service](docs/screenshots/test-laporan-service.png)

#### D. Repository

Pengujian dilakukan terhadap fungsi pengambilan
dan penyimpanan data produk, member, dan transaksi
pada file JSON.

![Repository](docs/screenshots/test-repository.png)

### 2. Integration Testing

Pengujian integrasi dilakukan untuk memastikan
modul service dan repository dapat bekerja sama
dalam proses transaksi web dan API, termasuk
penanganan transaksi yang gagal karena stok kurang.

![Integration Testing](docs/screenshots/test-integrasi.png)

### 3. Hasil Pengujian Keseluruhan

Seluruh pengujian dijalankan menggunakan perintah:

```bash
python3 -m unittest discover -s tests -v
```

Hasil pengujian menunjukkan bahwa 31 test berhasil
dijalankan tanpa kegagalan.

![Hasil Pengujian Keseluruhan](docs/screenshots/test-keseluruhan.png)
