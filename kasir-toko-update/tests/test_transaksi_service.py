
import unittest
from unittest.mock import patch

from layanan.transaksi_service import (
    _cari_produk,
    _hitung_diskon,
    _buat_nomor_transaksi,
    proses_transaksi_web,
    proses_transaksi_api
)


class TestTransaksiService(unittest.TestCase):

    def setUp(self):
        self.data = {
            "produk": [
                {
                    "kode": "BR001",
                    "nama": "Beras",
                    "harga": 15000,
                    "stok": 10
                },
                {
                    "kode": "MY001",
                    "nama": "Minyak",
                    "harga": 20000,
                    "stok": 5
                }
            ],
            "member": [
                {"id": "M001", "level": "gold"},
                {"id": "M002", "level": "silver"}
            ],
            "transaksi": []
        }

    # 1. Pengujian pencarian produk
    def test_cari_produk_ditemukan(self):
        hasil = _cari_produk(self.data, "BR001")
        self.assertEqual(hasil["nama"], "Beras")

    def test_cari_produk_tidak_ditemukan(self):
        hasil = _cari_produk(self.data, "XX001")
        self.assertIsNone(hasil)

    # 2. Pengujian perhitungan diskon
    def test_hitung_diskon_member_gold(self):
        hasil = _hitung_diskon(10000, "M001", self.data)
        self.assertEqual(hasil, __import__("config").Config.DISKON_GOLD)

    def test_hitung_diskon_member_silver(self):
        hasil = _hitung_diskon(10000, "M002", self.data)
        self.assertEqual(hasil, __import__("config").Config.DISKON_SILVER)

    def test_hitung_diskon_tanpa_member(self):
        hasil = _hitung_diskon(10000, "", self.data)
        self.assertEqual(hasil, 0)

    # 3. Pengujian nomor transaksi
    def test_buat_nomor_transaksi(self):
        hasil = _buat_nomor_transaksi(self.data, "2026-11-07")
        self.assertEqual(hasil, "TRX-20261107-001")

    def test_nomor_transaksi_berikutnya(self):
        self.data["transaksi"].append({
            "tanggal": "2026-11-07"
        })

        hasil = _buat_nomor_transaksi(self.data, "2026-11-07")
        self.assertEqual(hasil, "TRX-20261107-002")

    # 4. Pengujian transaksi web
    @patch("layanan.transaksi_service.simpan_data_transaksi")
    @patch("layanan.transaksi_service.ambil_semua_data")
    def test_transaksi_web_berhasil(self, mock_data, mock_simpan):
        mock_data.return_value = self.data

        struk, error = proses_transaksi_web(
            "", 100000, "BR001,2"
        )

        self.assertIsNone(error)
        self.assertIsNotNone(struk)
        self.assertEqual(self.data["produk"][0]["stok"], 8)
        mock_simpan.assert_called_once()

    @patch("layanan.transaksi_service.ambil_semua_data")
    def test_transaksi_web_produk_tidak_ditemukan(self, mock_data):
        mock_data.return_value = self.data

        struk, error = proses_transaksi_web(
            "", 100000, "XX001,1"
        )

        self.assertIsNone(struk)
        self.assertIn("Produk tidak ditemukan", error)

    @patch("layanan.transaksi_service.ambil_semua_data")
    def test_transaksi_web_stok_tidak_cukup(self, mock_data):
        mock_data.return_value = self.data

        struk, error = proses_transaksi_web(
            "", 100000, "BR001,20"
        )

        self.assertIsNone(struk)
        self.assertIn("tidak cukup", error)

    @patch("layanan.transaksi_service.ambil_semua_data")
    def test_transaksi_web_uang_kurang(self, mock_data):
        mock_data.return_value = self.data

        struk, error = proses_transaksi_web(
            "", 1, "BR001,2"
        )

        self.assertIsNone(struk)
        self.assertIn("Uang bayar kurang", error)

    # 5. Pengujian transaksi API
    @patch("layanan.transaksi_service.simpan_data_transaksi")
    @patch("layanan.transaksi_service.ambil_semua_data")
    def test_transaksi_api_berhasil(self, mock_data, mock_simpan):
        mock_data.return_value = self.data

        struk, error, status = proses_transaksi_api({
            "member": "",
            "items": [{"kode": "BR001", "qty": 2}],
            "bayar": 100000,
            "tanggal": "2026-11-07"
        })

        self.assertEqual(status, 201)
        self.assertIsNone(error)
        self.assertIsNotNone(struk)
        self.assertEqual(self.data["produk"][0]["stok"], 8)
        mock_simpan.assert_called_once()

    @patch("layanan.transaksi_service.ambil_semua_data")
    def test_transaksi_api_produk_tidak_ditemukan(self, mock_data):
        mock_data.return_value = self.data

        struk, error, status = proses_transaksi_api({
            "items": [{"kode": "XX001", "qty": 1}],
            "bayar": 100000
        })

        self.assertEqual(status, 404)
        self.assertIsNone(struk)
        self.assertIn("Produk tidak ditemukan", error["error"])

    @patch("layanan.transaksi_service.ambil_semua_data")
    def test_transaksi_api_jumlah_tidak_valid(self, mock_data):
        mock_data.return_value = self.data

        struk, error, status = proses_transaksi_api({
            "items": [{"kode": "BR001", "qty": 0}],
            "bayar": 100000
        })

        self.assertEqual(status, 400)
        self.assertIsNone(struk)
        self.assertIn("Jumlah harus lebih dari 0", error["error"])


if __name__ == "__main__":
    unittest.main()
