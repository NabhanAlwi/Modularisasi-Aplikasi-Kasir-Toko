
## Dokumentasi Pengujian

Pengujian aplikasi Kasir Toko dilakukan menggunakan
library unittest pada Python. Pengujian terdiri dari
Unit Testing dan Integration Testing.

### 1. Unit Testing

#### A. Produk Service

Pengujian dilakukan untuk memastikan fungsi pengelolaan
produk berjalan dengan baik, meliputi daftar produk,
filter kategori, dan pemeriksaan stok menipis.

![Produk Service](test-produk-service.png)

#### B. Transaksi Service

Pengujian dilakukan terhadap proses pencarian produk,
perhitungan diskon, pembuatan nomor transaksi,
validasi pembayaran, dan pemrosesan transaksi web maupun API.

![Transaksi Service](test-transaksi-service.png)

#### C. Laporan Service

Pengujian dilakukan untuk memastikan laporan harian,
omzet, jumlah transaksi, dan produk terlaris
dapat dihitung dengan benar.

![Laporan Service](test-laporan-service.png)

#### D. Repository

Pengujian dilakukan terhadap fungsi pengambilan
dan penyimpanan data produk, member, dan transaksi
pada file JSON.

![Repository](test-repository.png)

### 2. Integration Testing

Pengujian integrasi dilakukan untuk memastikan
modul service dan repository dapat bekerja sama
dalam proses transaksi web dan API, termasuk
penanganan transaksi yang gagal karena stok kurang.

![Integration Testing](test-integrasi.png)

### 3. Hasil Pengujian Keseluruhan

Seluruh pengujian dijalankan menggunakan perintah:

```bash
python3 -m unittest discover -s tests -v
```

Hasil pengujian menunjukkan bahwa 31 test berhasil
dijalankan tanpa kegagalan.

![Hasil Pengujian Keseluruhan](test-keseluruhan.png)

### 4. diagram testing

![flowchart Testing](mermaid-diagram.png)

### 5. contoh pengujian gagal

Pengujian gagal disebabkan oleh ketidaksesuaian antara jumlah produk aktual dengan jumlah produk yang diharapkan. Data pengujian menyediakan tiga produk, sedangkan nilai ekspektasi sengaja diubah menjadi empat. Akibatnya, pengujian menghasilkan status FAIL. Skenario ini digunakan untuk membuktikan bahwa unit testing mampu mendeteksi kesalahan atau ketidaksesuaian hasil.

![Pengujian gagal](Pengujian gagal.png) 