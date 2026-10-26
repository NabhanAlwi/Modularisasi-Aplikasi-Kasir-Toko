from flask import Blueprint, request, jsonify
from layanan.produk_service import daftar_produk, daftar_stok_menipis
from layanan.transaksi_service import proses_transaksi_api
from layanan.laporan_service import laporan_harian

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/produk")
def api_produk():
    kategori = request.args.get("kategori")
    return jsonify(daftar_produk(kategori))


@api_bp.route("/transaksi", methods=["POST"])
def api_transaksi():
    body = request.get_json(silent=True) or {}
    struk, error, status = proses_transaksi_api(body)
    if error:
        return jsonify(error), status
    return jsonify(struk), status


@api_bp.route("/laporan")
def api_laporan():
    tanggal = request.args.get("tanggal")
    data = laporan_harian(tanggal)
    return jsonify({
        "tanggal": data["tanggal"],
        "jumlah_transaksi": data["jumlah_transaksi"],
        "omzet": data["omzet"],
        "terlaris": [{"nama": nama, "qty": qty} for nama, qty in data["terlaris"]]
    })


@api_bp.route("/stok-menipis")
def api_stok_menipis():
    return jsonify(daftar_stok_menipis())
