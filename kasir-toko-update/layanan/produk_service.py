from config import Config
from repositori.produk_repo import ambil_semua_data


def daftar_produk(kategori=None):
    data = ambil_semua_data()
    produk = data["produk"]
    if kategori is not None:
        produk = [p for p in produk if p["kategori"] == kategori]
    return produk


def daftar_produk_dan_stok_menipis():
    data = ambil_semua_data()
    produk = data["produk"]
    menipis = [p for p in produk if p["stok"] < Config.BATAS_STOK_MENIPIS]
    return produk, menipis


def daftar_stok_menipis():
    data = ambil_semua_data()
    return [p for p in data["produk"] if p["stok"] < Config.BATAS_STOK_MENIPIS]
