"""Aturan harga: tarif per kg, berat minimal, express, dan diskon member."""
from config import BERAT_MINIMAL_DITAGIH, BIAYA_EXPRESS_PERSEN, DISKON_MEMBER_PERSEN, TARIF_PER_KG


def berat_ditagih(berat: float) -> float:
    """Cucian di bawah berat minimal tetap ditagih berat minimal."""
    return max(berat, BERAT_MINIMAL_DITAGIH)


def harga_dasar(layanan: str, berat: float) -> int:
    return round(berat_ditagih(berat) * TARIF_PER_KG[layanan])


def biaya_express(harga: int, express: bool) -> int:
    return harga * BIAYA_EXPRESS_PERSEN // 100 if express else 0


def diskon_member(subtotal: int, member: bool) -> int:
    return subtotal * DISKON_MEMBER_PERSEN // 100 if member else 0


def rincian_harga(layanan: str, berat: float, express: bool, member: bool) -> dict:
    """Menggabungkan semua aturan harga menjadi rincian nota."""
    dasar = harga_dasar(layanan, berat)
    express_rp = biaya_express(dasar, express)
    diskon = diskon_member(dasar + express_rp, member)
    return {"berat_ditagih": berat_ditagih(berat), "harga_dasar": dasar, "biaya_express": express_rp, "diskon": diskon,
            "total": dasar + express_rp - diskon}
