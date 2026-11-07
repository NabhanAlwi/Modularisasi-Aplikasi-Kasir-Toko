
import unittest
from unittest.mock import patch

from layanan.produk_service import (
    daftar_produk,
    daftar_produk_dan_stok_menipis,
    daftar_stok_menipis
)


class TestProdukService(unittest.TestCase):

    def setUp(self):
        self.data_dummy = {
            "produk": [
                {
                    "id": 1,
                    "nama": "Beras",
                    "kategori": "Sembako",
                    "stok": 3
                },
                {
                    "id": 2,
                    "nama": "Minyak",
                    "kategori": "Sembako",
                    "stok": 10
                },
                {
                    "id": 3,
                    "nama": "Sabun",
                    "kategori": "Kebersihan",
                    "stok": 2
                }
            ]
        }

    @patch("layanan.produk_service.ambil_semua_data")
    def test_daftar_produk_semua(self, mock_data):
        mock_data.return_value = self.data_dummy

        hasil = daftar_produk()

        self.assertEqual(len(hasil), 3)

    @patch("layanan.produk_service.ambil_semua_data")
    def test_daftar_produk_berdasarkan_kategori(self, mock_data):
        mock_data.return_value = self.data_dummy

        hasil = daftar_produk("Sembako")

        self.assertEqual(len(hasil), 2)
        self.assertTrue(
            all(p["kategori"] == "Sembako" for p in hasil)
        )

    @patch("layanan.produk_service.ambil_semua_data")
    def test_daftar_produk_dan_stok_menipis(self, mock_data):
        mock_data.return_value = self.data_dummy

        semua, menipis = daftar_produk_dan_stok_menipis()

        self.assertEqual(len(semua), 3)
        self.assertEqual(
            len(menipis),
            sum(
                p["stok"] < __import__(
                    "config"
                ).Config.BATAS_STOK_MENIPIS
                for p in self.data_dummy["produk"]
            )
        )

    @patch("layanan.produk_service.ambil_semua_data")
    def test_daftar_stok_menipis(self, mock_data):
        mock_data.return_value = self.data_dummy

        hasil = daftar_stok_menipis()

        self.assertTrue(
            all(
                p["stok"] < __import__(
                    "config"
                ).Config.BATAS_STOK_MENIPIS
                for p in hasil
            )
        )


if __name__ == "__main__":
    unittest.main()
