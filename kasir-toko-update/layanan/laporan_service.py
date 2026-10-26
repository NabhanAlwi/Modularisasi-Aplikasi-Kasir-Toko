import datetime
from config import Config
from repositori.produk_repo import ambil_semua_data


def laporan_harian(tanggal=None):
    if tanggal is None:
        tanggal = datetime.date.today().isoformat()
    data = ambil_semua_data()
    omzet = 0
    jumlah = 0
    terjual = {}
    for transaksi in data["transaksi"]:
        if transaksi["tanggal"] == tanggal:
            omzet += transaksi["total"]
            jumlah += 1
            for item in transaksi["items"]:
                terjual[item["nama"]] = terjual.get(item["nama"], 0) + item["qty"]
    terlaris = sorted(terjual.items(), key=lambda item: item[1], reverse=True)[:Config.JUMLAH_PRODUK_TERLARIS]
    return {
        "tanggal": tanggal,
        "jumlah_transaksi": jumlah,
        "omzet": omzet,
        "terlaris": terlaris,
    }
