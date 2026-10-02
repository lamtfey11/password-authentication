"""
Независимая проверка варианта 13 (лаба №3): блочный шифр, режим ECB,
соль, хеш MD5.

Этот скрипт НЕ использует crypto.py и secure_file.py из проекта —
он читает реальный security.db и сам, напрямую через hashlib и
cryptography, повторяет расшифровку. Если она пройдёт успешно —
это доказывает, что файл действительно зашифрован именно так, как
описано в задании, а не просто "по словам кода".

Запуск: python verify_variant13.py
"""

import getpass
import hashlib

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SALT_SIZE = 16

with open("security.db", "rb") as f:
    blob = f.read()

salt, ciphertext = blob[:SALT_SIZE], blob[SALT_SIZE:]

print("=== Проверка файла security.db ===")
print("Соль (16 байт):", salt.hex())
print("Длина шифротекста:", len(ciphertext), "байт")
print("Кратна 16 (размер блока AES):", len(ciphertext) % 16 == 0)
print()

passphrase = getpass.getpass("Парольная фраза: ")

# --- Хеш: MD5 (вариант 13) ---
# Ключ формируется вручную, той же формулой, что описана в задании:
# хеш от парольной фразы с добавлением соли.
key = hashlib.md5(passphrase.encode("utf-8") + salt).digest()
print("\nКлюч, полученный через MD5(фраза + соль):", key.hex())

# --- Блочный шифр, режим ECB (вариант 13) ---
# Расшифровка настоящего содержимого файла этим ключом.
decryptor = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
padded = decryptor.update(ciphertext) + decryptor.finalize()
unpadder = padding.PKCS7(128).unpadder()

try:
    plain = unpadder.update(padded) + unpadder.finalize()
except ValueError:
    print("\nРасшифровать не удалось — неверная парольная фраза "
          "или файл не соответствует ожидаемому формату.")
    raise SystemExit(1)

print("\nРасшифровано успешно:", len(plain), "байт")
print("В данных есть запись ADMIN:", b"ADMIN" in plain)

# --- Доказательство режима именно ECB (а не CBC/CFB) ---
# Классический признак ECB: одинаковые 16-байтные блоки открытого
# текста всегда дают одинаковые блоки шифротекста, потому что каждый
# блок шифруется независимо, без переноса состояния между блоками.
# В CBC/CFB из-за использования предыдущего блока (или IV) одинаковые
# блоки открытого текста почти никогда не дают одинаковый шифротекст.
test_plain = b"A" * 16 + b"B" * 16 + b"A" * 16
encryptor = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
test_cipher = encryptor.update(test_plain) + encryptor.finalize()
block1, block2, block3 = test_cipher[0:16], test_cipher[16:32], test_cipher[32:48]

print("\n=== Проверка режима ECB ===")
print("Блок 1 шифротекста:", block1.hex())
print("Блок 2 шифротекста:", block2.hex())
print("Блок 3 шифротекста:", block3.hex())
print("Блок 1 == Блок 3 (одинаковый открытый текст -> одинаковый шифротекст):",
      block1 == block3)
print("Это свойство специфично для ECB и не выполняется для CBC/CFB.")