
import unittest
from unittest.mock import patch

from layanan.laporan_service import laporan_harian


class TestLaporanService(unittest.TestCase):

    def setUp(self):
        self.data_dummy = {
            "transaksi": [
                {
                    "tanggal": "2026-11-07",
                    "total": 50000,
                    "items": [
                        {"nama": "Beras", "qty": 2},
                        {"nama": "Minyak", "qty": 1}
                    ]
                },
                {
                    "tanggal": "2026-11-07",
                    "total": 30000,
                    "items": [
                        {"nama": "Beras", "qty": 1},
                        {"nama": "Sabun", "qty": 3}
                    ]
                },
                {
                    "tanggal": "2026-11-06",
                    "total": 40000,
                    "items": [
                        {"nama": "Minyak", "qty": 2}
                    ]
                }
            ]
        }

    @patch("layanan.laporan_service.ambil_semua_data")
    def test_laporan_harian_berhasil(self, mock_data):
        mock_data.return_value = self.data_dummy

        hasil = laporan_harian("2026-11-07")

        self.assertEqual(hasil["jumlah_transaksi"], 2)
        self.assertEqual(hasil["omzet"], 80000)
        self.assertEqual(hasil["tanggal"], "2026-11-07")

    @patch("layanan.laporan_service.ambil_semua_data")
    def test_laporan_tanggal_tanpa_transaksi(self, mock_data):
        mock_data.return_value = self.data_dummy

        hasil = laporan_harian("2026-11-05")

        self.assertEqual(hasil["jumlah_transaksi"], 0)
        self.assertEqual(hasil["omzet"], 0)
        self.assertEqual(hasil["terlaris"], [])

    @patch("layanan.laporan_service.ambil_semua_data")
    def test_produk_terlaris(self, mock_data):
        mock_data.return_value = self.data_dummy

        hasil = laporan_harian("2026-11-07")

        self.assertIn(("Beras", 3), hasil["terlaris"])
        self.assertIn(("Sabun", 3), hasil["terlaris"])
        self.assertIn(("Minyak", 1), hasil["terlaris"])

    @patch("layanan.laporan_service.ambil_semua_data")
    def test_tanggal_default_hari_ini(self, mock_data):
        mock_data.return_value = self.data_dummy

        hasil = laporan_harian()

        self.assertEqual(
            hasil["tanggal"],
            __import__("datetime").date.today().isoformat()
        )


if __name__ == "__main__":
    unittest.main()
