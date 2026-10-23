def format_rupiah(nilai: int) -> str:
    """36450 -> 'Rp 36.450'"""
    return "Rp {:,.0f}".format(nilai).replace(",", ".")
