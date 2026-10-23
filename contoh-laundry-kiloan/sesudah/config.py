"""Lokasi data dan SEMUA angka aturan bisnis. Ubah aturan cukup di sini."""
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

TARIF_PER_KG = {"cuci_kering": 7000, "cuci_setrika": 9000, "setrika": 6000}
BERAT_MINIMAL_DITAGIH = 3       # kg; cucian lebih ringan tetap ditagih 3 kg
BERAT_MAKSIMAL = 50             # kg per nota
BIAYA_EXPRESS_PERSEN = 50       # dari harga dasar
DISKON_MEMBER_PERSEN = 10       # dari (harga dasar + biaya express)

LAMA_PROSES_HARI = {"express": 1, "reguler": 2}
HARI_TUTUP = 6                  # date.weekday(): 6 = Minggu; selesai digeser ke Senin
MASA_SIMPAN_GRATIS_HARI = 7     # setelah estimasi selesai
BIAYA_SIMPAN_PER_HARI = 2000

URUTAN_STATUS = ["diterima", "dicuci", "siap", "diambil"]
POLA_HP = r"^08\d{8,11}$"
