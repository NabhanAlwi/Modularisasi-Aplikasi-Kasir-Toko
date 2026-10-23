"""Alur nota: validasi pesanan, membuat nota, dan memajukan status."""
import re
from datetime import date

from config import BERAT_MAKSIMAL, POLA_HP, TARIF_PER_KG, URUTAN_STATUS
from layanan.galat import GalatValidasi, TidakDitemukan
from layanan.harga import rincian_harga
from layanan.jadwal import biaya_simpan, estimasi_selesai


def validasi_pesanan(nama: str, hp: str, layanan: str, berat) -> None:
    if layanan not in TARIF_PER_KG:
        raise GalatValidasi("Layanan tidak dikenal")
    if not isinstance(berat, (int, float)) or berat <= 0 or berat > BERAT_MAKSIMAL:
        raise GalatValidasi("Berat harus lebih dari 0 dan maksimal 50 kg")
    if nama == "":
        raise GalatValidasi("Nama wajib diisi")
    if not re.match(POLA_HP, hp):
        raise GalatValidasi("Nomor HP tidak valid")


def adalah_member(daftar_pelanggan: list[dict], hp: str) -> bool:
    return any(p["hp"] == hp and p["member"] for p in daftar_pelanggan)


def nomor_nota(tgl: date, daftar_nota: list[dict]) -> str:
    """LDY-YYMMDD-NN, NN = urutan nota pada tanggal itu."""
    urut = sum(1 for n in daftar_nota if n["tanggal"] == tgl.isoformat()) + 1
    return "LDY-" + tgl.strftime("%y%m%d") + "-" + str(urut).zfill(2)


def buat_nota(repo, nama: str, hp: str, layanan: str, berat, express: bool, tgl: date) -> dict:
    data = repo.muat()
    nama, hp = str(nama).strip(), str(hp).strip()
    validasi_pesanan(nama, hp, layanan, berat)
    nota = {"no": nomor_nota(tgl, data["nota"]), "tanggal": tgl.isoformat(), "hp": hp, "nama": nama, "layanan": layanan, "berat": berat,
            "express": express, **rincian_harga(layanan, berat, express, adalah_member(data["pelanggan"], hp)),
            "estimasi_selesai": estimasi_selesai(tgl, express).isoformat(), "status": URUTAN_STATUS[0], "tgl_diambil": None, "biaya_simpan": 0}
    data["nota"].append(nota)
    repo.simpan(data)
    return nota


def status_berikutnya(status: str) -> str:
    """'diterima' -> 'dicuci' -> 'siap' -> 'diambil'; status terakhir tidak bisa maju lagi."""
    i = URUTAN_STATUS.index(status)
    if i == len(URUTAN_STATUS) - 1:
        raise GalatValidasi("Nota sudah diambil")
    return URUTAN_STATUS[i + 1]


def lanjutkan_status(repo, no: str, tgl: date) -> dict:
    """Memajukan status satu langkah; saat diambil, catat tanggal dan biaya simpan."""
    data = repo.muat()
    nota = next((n for n in data["nota"] if n["no"] == no), None)
    if nota is None:
        raise TidakDitemukan("Nota tidak ditemukan")
    nota["status"] = status_berikutnya(nota["status"])
    if nota["status"] == "diambil":
        nota["tgl_diambil"] = tgl.isoformat()
        nota["biaya_simpan"] = biaya_simpan(date.fromisoformat(nota["estimasi_selesai"]), tgl)
    repo.simpan(data)
    return nota
