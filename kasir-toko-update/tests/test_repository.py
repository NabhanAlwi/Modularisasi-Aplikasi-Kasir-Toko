
import unittest
import json
import tempfile
import os
from unittest.mock import patch

from repositori import produk_repo, transaksi_repo


class TestProdukRepository(unittest.TestCase):

    def setUp(self):
        self.data = {
            "produk": [
                {"kode": "P001", "nama": "Beras", "stok": 10},
                {"kode": "P002", "nama": "Minyak", "stok": 5}
            ],
            "member": [
                {"id": "M001", "nama": "Andi"}
            ],
            "transaksi": []
        }

    @patch("repositori.produk_repo.Config.DATA_FILE")
    def test_ambil_semua_data(self, mock_file):
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as file:
            json.dump(self.data, file)
            nama_file = file.name

        try:
            with patch("repositori.produk_repo.Config.DATA_FILE", nama_file):
                hasil = produk_repo.ambil_semua_data()

            self.assertEqual(hasil, self.data)
        finally:
            os.remove(nama_file)

    @patch("repositori.produk_repo.Config.DATA_FILE")
    def test_simpan_semua_data(self, mock_file):
        with tempfile.NamedTemporaryFile(delete=False) as file:
            nama_file = file.name

        try:
            with patch("repositori.produk_repo.Config.DATA_FILE", nama_file):
                produk_repo.simpan_semua_data(self.data)

                with open(nama_file, encoding="utf-8") as file:
                    hasil = json.load(file)

            self.assertEqual(hasil, self.data)
        finally:
            os.remove(nama_file)

    @patch("repositori.produk_repo.ambil_semua_data")
    def test_ambil_semua_produk(self, mock_ambil):
        mock_ambil.return_value = self.data

        hasil = produk_repo.ambil_semua_produk()

        self.assertEqual(hasil, self.data["produk"])

    @patch("repositori.produk_repo.ambil_semua_data")
    def test_ambil_semua_member(self, mock_ambil):
        mock_ambil.return_value = self.data

        hasil = produk_repo.ambil_semua_member()

        self.assertEqual(hasil, self.data["member"])


class TestTransaksiRepository(unittest.TestCase):

    def setUp(self):
        self.data = {
            "produk": [],
            "member": [],
            "transaksi": [
                {"no": "TRX001", "total": 50000}
            ]
        }

    @patch("repositori.transaksi_repo.ambil_semua_data")
    def test_ambil_semua_transaksi(self, mock_ambil):
        mock_ambil.return_value = self.data

        hasil = transaksi_repo.ambil_semua_transaksi()

        self.assertEqual(hasil, self.data["transaksi"])

    @patch("repositori.transaksi_repo.simpan_semua_data")
    def test_simpan_data_transaksi(self, mock_simpan):
        transaksi_repo.simpan_data_transaksi(self.data)

        mock_simpan.assert_called_once_with(self.data)


if __name__ == "__main__":
    unittest.main()
