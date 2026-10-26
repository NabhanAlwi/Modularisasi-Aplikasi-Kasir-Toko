import os


class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_FILE = os.path.join(BASE_DIR, "data.json")
    BATAS_STOK_MENIPIS = 5
    TARIF_PPN = 0.11
    BATAS_DISKON_TRANSAKSI = 1_000_000
    DISKON_GOLD = 10
    DISKON_SILVER = 5
    DISKON_TRANSAKSI_BESAR = 5
    DISKON_MAKSIMUM = 15
    JUMLAH_PRODUK_TERLARIS = 3
