import os
import struct
from dataclasses import dataclass

from config import ADMIN, MAXNAME, MAXPASS

# Запись файла: имя | длина пароля | пароль | блокировка | ограничения
_REC = struct.Struct("<%dsi%ds??" % (MAXNAME * 4, MAXPASS * 4))
REC_SIZE = _REC.size


@dataclass
class Account:
    name: str
    password: str = ""      # пустой пароль = пользователь ещё не входил
    block: bool = False     # учётная запись заблокирована администратором
    restrict: bool = True   # включены ограничения на выбираемый пароль


class AccountFile:
    def __init__(self, path):
        self.path = path

    @staticmethod
    def _pack(acc: Account) -> bytes:
        return _REC.pack(acc.name.encode("utf-8"), len(acc.password),
                         acc.password.encode("utf-8"), acc.block, acc.restrict)

    @staticmethod
    def _unpack(chunk: bytes) -> Account:
        name_b, passlen, pass_b, block, restrict = _REC.unpack(chunk)
        name = name_b.rstrip(b"\0").decode("utf-8", "replace")
        password = pass_b.rstrip(b"\0").decode("utf-8", "replace")[:passlen]
        return Account(name, password, block, restrict)

    def ensure_exists(self):
        # При первом запуске создаёт файл с одним ADMIN и пустым паролем
        if not os.path.exists(self.path):
            with open(self.path, "wb") as f:
                f.write(self._pack(Account(ADMIN, "", False, True)))

    def read_all(self):
        with open(self.path, "rb") as f:
            data = f.read()
        if len(data) % REC_SIZE:
            raise ValueError("Файл учётных записей повреждён.")
        return [self._unpack(data[i:i + REC_SIZE])
                for i in range(0, len(data), REC_SIZE)]

    def find(self, name):
        """Возвращает (номер, запись) или None."""
        for i, acc in enumerate(self.read_all()):
            if acc.name == name:
                return i, acc
        return None

    def write(self, index, acc):
        with open(self.path, "r+b") as f:
            f.seek(index * REC_SIZE)
            f.write(self._pack(acc))

    def append(self, acc):
        with open(self.path, "ab") as f:
            f.write(self._pack(acc))