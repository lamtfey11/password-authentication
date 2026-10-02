"""
Чтение и сохранение зашифрованного файла учётных данных.

Формат файла на диске: первые SALT_SIZE байт — соль, остальное —
шифротекст (AES, режим ECB). Соль нужна при каждой расшифровке,
чтобы по той же парольной фразе получить тот же ключ, поэтому она
хранится рядом с шифротекстом в открытом виде — сама по себе соль
ключом не является и не раскрывает учётные данные.
"""

from config import ADMIN
from crypto import SALT_SIZE, decrypt_bytes, derive_key, encrypt_bytes, generate_salt
from storage import parse_accounts


def load(path: str, passphrase: str):
    """
    Расшифровывает файл path парольной фразой passphrase.
    Возвращает bytes расшифрованного содержимого, если парольная фраза
    верна, иначе None.

    Правильность парольной фразы определяется по наличию в расшифрованных
    данных записи администратора (п. 4 задания лабы №3): если данные не
    расшифровались, повреждены или среди записей нет ADMIN — фраза неверна.
    """
    with open(path, "rb") as f:
        blob = f.read()
    if len(blob) <= SALT_SIZE:
        return None
    salt, ciphertext = blob[:SALT_SIZE], blob[SALT_SIZE:]
    key = derive_key(passphrase, salt)
    try:
        plain = decrypt_bytes(ciphertext, key)
        accounts = parse_accounts(plain)
    except ValueError:
        return None
    if not any(a.name == ADMIN for a in accounts):
        return None
    return plain


def save(path: str, passphrase: str, plain_data: bytes):
    """
    Шифрует plain_data на новой случайной соли и сохраняет в path.
    Старое содержимое файла стирается (п. 3 задания: запись поверх).
    """
    salt = generate_salt()
    key = derive_key(passphrase, salt)
    ciphertext = encrypt_bytes(plain_data, key)
    with open(path, "wb") as f:
        f.write(salt + ciphertext)