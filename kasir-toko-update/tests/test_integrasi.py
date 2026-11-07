
import unittest
import json
import tempfile
import os
from unittest.mock import patch

from config import Config
from layanan.transaksi_service import (
    proses_transaksi_web,
    proses_transaksi_api
)


class TestIntegrasiTransaksi(unittest.TestCase):

    def setUp(self):
        # Membuat file JSON sementara untuk pengujian
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.temp_dir.name, "data.json")

        self.data_awal = {
            "produk": [
                {
                    "kode": "P001",
                    "nama": "Beras",
                    "harga": 10000,
                    "stok": 10
                }
            ],
            "member": [],
            "transaksi": []
        }

        with open(self.data_file, "w", encoding="utf-8") as file:
            json.dump(self.data_awal, file)

        self.patch_data = patch.object(
            Config, "DATA_FILE", self.data_file
        )
        self.patch_data.start()

    def tearDown(self):
        self.patch_data.stop()
        self.temp_dir.cleanup()

    def baca_data(self):
        with open(self.data_file, encoding="utf-8") as file:
            return json.load(file)

    def test_integrasi_transaksi_web_berhasil(self):
        # Menjalankan transaksi melalui service web
        struk, error = proses_transaksi_web(
            "", 100000, "P001,2"
        )

        data = self.baca_data()

        # Memastikan transaksi berhasil
        self.assertIsNone(error)
        self.assertIsNotNone(struk)

        # Memastikan stok berkurang
        self.assertEqual(data["produk"][0]["stok"], 8)

        # Memastikan transaksi tersimpan
        self.assertEqual(len(data["transaksi"]), 1)
        self.assertEqual(data["transaksi"][0]["items"][0]["qty"], 2)

    def test_integrasi_transaksi_api_berhasil(self):
        body = {
            "member": "",
            "items": [
                {"kode": "P001", "qty": 3}
            ],
            "bayar": 100000,
            "tanggal": "2026-11-07"
        }

        struk, error, status = proses_transaksi_api(body)

        data = self.baca_data()

        # Memastikan API mengembalikan status berhasil
        self.assertEqual(status, 201)
        self.assertIsNone(error)
        self.assertIsNotNone(struk)

        # Memastikan stok dan data transaksi diperbarui
        self.assertEqual(data["produk"][0]["stok"], 7)
        self.assertEqual(len(data["transaksi"]), 1)

    def test_integrasi_transaksi_gagal_stok_kurang(self):
        # Jumlah pembelian melebihi stok tersedia
        struk, error = proses_transaksi_web(
            "", 100000, "P001,20"
        )

        data = self.baca_data()

        # Memastikan transaksi ditolak
        self.assertIsNone(struk)
        self.assertIsNotNone(error)

        # Memastikan stok dan transaksi tidak berubah
        self.assertEqual(data["produk"][0]["stok"], 10)
        self.assertEqual(len(data["transaksi"]), 0)


if __name__ == "__main__":
    unittest.main()
