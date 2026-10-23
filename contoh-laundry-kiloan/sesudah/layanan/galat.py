"""Exception domain. Rute API memetakannya ke status HTTP; rute web menampilkan pesannya."""


class GalatLayanan(Exception):
    status = 400

    def __init__(self, pesan: str, **data):
        super().__init__(pesan)
        self.pesan = pesan
        self.data = data  # informasi tambahan yang ikut dikirim di respons API


class GalatValidasi(GalatLayanan):
    status = 400


class TidakDitemukan(GalatLayanan):
    status = 404


class Konflik(GalatLayanan):
    status = 409


class Ditolak(GalatLayanan):
    status = 403
