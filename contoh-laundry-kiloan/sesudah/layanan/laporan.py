def laporan_harian(daftar_nota: list[dict], tanggal: str) -> dict:
    """Jumlah nota, total kg, pendapatan, dan jumlah nota per layanan pada tanggal masuk tertentu."""
    harian = [n for n in daftar_nota if n["tanggal"] == tanggal]
    per_layanan = {}
    for n in harian:
        per_layanan[n["layanan"]] = per_layanan.get(n["layanan"], 0) + 1
    return {"tanggal": tanggal, "jumlah_nota": len(harian), "total_kg": round(sum(n["berat"] for n in harian), 1),
            "pendapatan": sum(n["total"] for n in harian), "per_layanan": per_layanan}
