"""Halaman HTML. Tipis: ambil input form → panggil layanan → tampilkan hasil."""
from datetime import date

from flask import Blueprint, current_app, redirect, render_template, request

from layanan.galat import GalatLayanan
from layanan.laporan import laporan_harian
from layanan.nota import buat_nota, lanjutkan_status

web = Blueprint("web", __name__)


def _repo():
    return current_app.config["REPO"]


@web.route("/")
def index():
    status = request.args.get("status", "")
    nota = [n for n in _repo().muat()["nota"] if status == "" or n["status"] == status]
    return render_template("index.html", nota=nota, pesan=request.args.get("pesan", ""))


@web.route("/nota", methods=["POST"])
def form_nota():
    try:
        berat = float(request.form.get("berat", "0").replace(",", "."))
    except ValueError:
        berat = 0
    try:
        n = buat_nota(_repo(), request.form.get("nama", ""), request.form.get("hp", ""), request.form.get("layanan", ""), berat,
                      request.form.get("express") == "on", date.today())
    except GalatLayanan as e:
        return redirect("/?pesan=" + e.pesan)
    return redirect("/?pesan=Nota " + n["no"] + " dibuat, selesai " + date.fromisoformat(n["estimasi_selesai"]).strftime("%d-%m-%Y"))


@web.route("/nota/<no>/status", methods=["POST"])
def form_status(no):
    try:
        n = lanjutkan_status(_repo(), no, date.today())
    except GalatLayanan as e:
        return redirect("/?pesan=" + e.pesan)
    return redirect("/?pesan=" + no + " sekarang " + n["status"])


@web.route("/laporan")
def laporan():
    tanggal = request.args.get("tanggal", date.today().isoformat())
    return render_template("laporan.html", lap=laporan_harian(_repo().muat()["nota"], tanggal))
