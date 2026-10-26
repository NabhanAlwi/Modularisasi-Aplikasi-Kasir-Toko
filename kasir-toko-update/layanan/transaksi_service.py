import datetime
from config import Config
from repositori.produk_repo import ambil_semua_data
from repositori.transaksi_repo import simpan_data_transaksi


def _cari_produk(data, kode):
    produk = None
    for item in data["produk"]:
        if item["kode"] == kode:
            produk = item
    return produk


def _hitung_diskon(subtotal, member_id, data):
    persen = 0
    for member in data["member"]:
        if member["id"] == member_id:
            if member["level"] == "gold":
                persen = Config.DISKON_GOLD
            elif member["level"] == "silver":
                persen = Config.DISKON_SILVER
    if subtotal >= Config.BATAS_DISKON_TRANSAKSI:
        persen += Config.DISKON_TRANSAKSI_BESAR
    if persen > Config.DISKON_MAKSIMUM:
        persen = Config.DISKON_MAKSIMUM
    return persen


def _buat_nomor_transaksi(data, tanggal):
    urut = 1
    for transaksi in data["transaksi"]:
        if transaksi["tanggal"] == tanggal:
            urut += 1
    return "TRX-" + tanggal.replace("-", "") + "-" + str(urut).zfill(3)


def proses_transaksi_web(member_id, bayar, teks_items):
    """Memvalidasi dan memproses transaksi yang dikirim melalui form web."""
    data = ambil_semua_data()
    items = []
    error = None

    for line in teks_items.strip().splitlines():
        if line.strip() == "":
            continue
        bagian = line.split(",")
        if len(bagian) != 2:
            error = "Format item salah: " + line
            break
        kode = bagian[0].strip().upper()
        try:
            qty = int(bagian[1].strip())
        except ValueError:
            error = "Jumlah harus angka: " + line
            break
        produk = _cari_produk(data, kode)
        if produk is None:
            error = "Produk tidak ditemukan: " + kode
            break
        if qty <= 0:
            error = "Jumlah harus lebih dari 0: " + kode
            break
        if produk["stok"] < qty:
            error = "Stok " + produk["nama"] + " tidak cukup (sisa " + str(produk["stok"]) + ")"
            break
        items.append({"kode": kode, "nama": produk["nama"], "qty": qty, "harga": produk["harga"]})

    if error is None and len(items) == 0:
        error = "Keranjang kosong"
    if error is not None:
        return None, error

    subtotal = 0
    for item in items:
        subtotal += item["qty"] * item["harga"]
    persen = _hitung_diskon(subtotal, member_id, data)
    diskon = round(subtotal * persen / 100)
    ppn = round((subtotal - diskon) * Config.TARIF_PPN)
    total = subtotal - diskon + ppn

    try:
        bayar = int(bayar)
    except (ValueError, TypeError):
        bayar = 0
    if bayar < total:
        return None, "Uang bayar kurang. Total " + "Rp {:,.0f}".format(total).replace(",", ".")

    tanggal = datetime.date.today().isoformat()
    no = _buat_nomor_transaksi(data, tanggal)
    for item in items:
        for produk in data["produk"]:
            if produk["kode"] == item["kode"]:
                produk["stok"] -= item["qty"]

    struk = {
        "no": no, "tanggal": tanggal, "member": member_id, "items": items,
        "subtotal": subtotal, "diskon": diskon, "ppn": ppn, "total": total,
        "bayar": bayar, "kembali": bayar - total
    }
    data["transaksi"].append(struk)
    simpan_data_transaksi(data)
    return struk, None


def proses_transaksi_api(body):
    """Memproses transaksi dari JSON API; mengembalikan struk, error, dan status HTTP."""
    data = ambil_semua_data()
    member_id = body.get("member", "")
    items = []

    for item in body.get("items", []):
        kode = str(item.get("kode", "")).upper()
        qty = item.get("qty", 0)
        produk = _cari_produk(data, kode)
        if produk is None:
            return None, {"error": "Produk tidak ditemukan: " + kode}, 404
        if not isinstance(qty, int) or qty <= 0:
            return None, {"error": "Jumlah harus lebih dari 0: " + kode}, 400
        if produk["stok"] < qty:
            return None, {"error": "Stok " + produk["nama"] + " tidak cukup (sisa " + str(produk["stok"]) + ")"}, 400
        items.append({"kode": kode, "nama": produk["nama"], "qty": qty, "harga": produk["harga"]})

    if len(items) == 0:
        return None, {"error": "Keranjang kosong"}, 400

    subtotal = sum(item["qty"] * item["harga"] for item in items)
    persen = _hitung_diskon(subtotal, member_id, data)
    diskon = round(subtotal * persen / 100)
    ppn = round((subtotal - diskon) * Config.TARIF_PPN)
    total = subtotal - diskon + ppn
    bayar = body.get("bayar", 0)
    if bayar < total:
        return None, {"error": "Uang bayar kurang", "total": total}, 400

    tanggal = body.get("tanggal") or datetime.date.today().isoformat()
    no = _buat_nomor_transaksi(data, tanggal)
    for item in items:
        for produk in data["produk"]:
            if produk["kode"] == item["kode"]:
                produk["stok"] -= item["qty"]

    struk = {
        "no": no, "tanggal": tanggal, "member": member_id, "items": items,
        "subtotal": subtotal, "diskon": diskon, "ppn": ppn, "total": total,
        "bayar": bayar, "kembali": bayar - total
    }
    data["transaksi"].append(struk)
    simpan_data_transaksi(data)
    return struk, None, 201
