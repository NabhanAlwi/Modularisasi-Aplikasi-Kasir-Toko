"""API JSON. Memanggil fungsi layanan yang SAMA dengan halaman web."""
from datetime import date

from flask import Blueprint, current_app, jsonify, request

from layanan.galat import GalatLayanan
from layanan.laporan import laporan_harian
from layanan.nota import buat_nota, lanjutkan_status

api = Blueprint("api", __name__)


def _repo():
    return current_app.config["REPO"]


def _tanggal(teks: str | None) -> date:
    return date.fromisoformat(teks) if teks else date.today()


@api.errorhandler(GalatLayanan)
def tangani_galat(e: GalatLayanan):
    return jsonify({"error": e.pesan, **e.data}), e.status


@api.route("/nota")
def daftar():
    status = request.args.get("status")
    return jsonify([n for n in _repo().muat()["nota"] if status is None or n["status"] == status])


@api.route("/nota", methods=["POST"])
def buat():
    b = request.get_json(silent=True) or {}
    n = buat_nota(_repo(), b.get("nama", ""), b.get("hp", ""), b.get("layanan"), b.get("berat", 0), bool(b.get("express", False)), _tanggal(b.get("tanggal")))
    return jsonify(n), 201


@api.route("/nota/<no>/status", methods=["POST"])
def status(no):
    b = request.get_json(silent=True) or {}
    return jsonify(lanjutkan_status(_repo(), no, _tanggal(b.get("tanggal"))))


@api.route("/laporan")
def laporan():
    return jsonify(laporan_harian(_repo().muat()["nota"], request.args.get("tanggal", date.today().isoformat())))
