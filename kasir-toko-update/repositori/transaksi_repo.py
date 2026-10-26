from repositori.produk_repo import ambil_semua_data, simpan_semua_data


def ambil_semua_transaksi():
    return ambil_semua_data()["transaksi"]


def simpan_data_transaksi(data):
    """Menyimpan perubahan transaksi dan stok ke data JSON."""
    simpan_semua_data(data)
