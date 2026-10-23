import json


class RepositoriJson:
    """Membaca dan menyimpan seluruh data aplikasi dari/ke satu file JSON."""

    def __init__(self, path: str):
        self.path = path

    def muat(self) -> dict:
        with open(self.path, encoding="utf-8") as f:
            return json.load(f)

    def simpan(self, data: dict) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
