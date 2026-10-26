import json
from config import Config


def ambil_semua_data():
    """Membaca seluruh data toko dari file JSON."""
    with open(Config.DATA_FILE, encoding="utf-8") as file:
        return json.load(file)


def simpan_semua_data(data):
    """Menyimpan seluruh data toko ke file JSON."""
    with open(Config.DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def ambil_semua_produk():
    return ambil_semua_data()["produk"]


def ambil_semua_member():
    return ambil_semua_data()["member"]
