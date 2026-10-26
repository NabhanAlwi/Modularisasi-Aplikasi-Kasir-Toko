from flask import Blueprint, request, render_template
from layanan.produk_service import daftar_produk_dan_stok_menipis
from layanan.transaksi_service import proses_transaksi_web
from layanan.laporan_service import laporan_harian

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def index():
    produk, menipis = daftar_produk_dan_stok_menipis()
    return render_template("produk.html", produk=produk, menipis=menipis)


@web_bp.route("/transaksi", methods=["GET", "POST"])
def transaksi():
    pesan = ""
    struk = None
    if request.method == "POST":
        member_id = request.form.get("member", "").strip()
        bayar = request.form.get("bayar", "0").strip()
        teks_items = request.form.get("items", "")
        struk, error = proses_transaksi_web(member_id, bayar, teks_items)
        if error:
            pesan = error
    return render_template("transaksi.html", pesan=pesan, struk=struk)


@web_bp.route("/laporan")
def laporan():
    tanggal = request.args.get("tanggal")
    data = laporan_harian(tanggal)
    omzet = "Rp {:,.0f}".format(data["omzet"]).replace(",", ".")
    return render_template(
        "laporan.html", tanggal=data["tanggal"], jumlah=data["jumlah_transaksi"],
        omzet=omzet, terlaris=data["terlaris"]
    )
