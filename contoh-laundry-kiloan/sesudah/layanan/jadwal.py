"""Aturan waktu: estimasi selesai dan biaya penyimpanan."""
from datetime import date, timedelta

from config import BIAYA_SIMPAN_PER_HARI, HARI_TUTUP, LAMA_PROSES_HARI, MASA_SIMPAN_GRATIS_HARI


def estimasi_selesai(tgl_masuk: date, express: bool) -> date:
    """Express 1 hari, reguler 2 hari; bila jatuh pada hari tutup (Minggu) digeser ke esok harinya."""
    selesai = tgl_masuk + timedelta(days=LAMA_PROSES_HARI["express" if express else "reguler"])
    if selesai.weekday() == HARI_TUTUP:
        selesai += timedelta(days=1)
    return selesai


def biaya_simpan(estimasi: date, tgl_diambil: date) -> int:
    """Gratis sampai MASA_SIMPAN_GRATIS_HARI setelah estimasi selesai; lewat dari itu dikenai biaya per hari."""
    lewat = (tgl_diambil - estimasi).days - MASA_SIMPAN_GRATIS_HARI
    return max(lewat, 0) * BIAYA_SIMPAN_PER_HARI
