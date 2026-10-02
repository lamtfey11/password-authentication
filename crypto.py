"""
Шифрование файла учётных данных (лабораторная работа №3, вариант 13).

Вариант 13: блочный шифр, режим ECB (Электронная кодовая книга),
к ключу добавляется случайное значение (соль), хеш-функция — MD5.

Функции CryptoAPI (CryptCreateHash, CryptHashData, CryptDeriveKey,
CryptEncrypt, CryptDecrypt) заменены стандартными средствами Python:
hashlib (MD5) для хеширования и библиотекой cryptography (AES) как
блочным шифром, поскольку CryptoAPI — интерфейс, специфичный для Windows.

Зависимость: pip install cryptography
"""

import hashlib
import os

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SALT_SIZE = 16     # размер соли в байтах
BLOCK_BITS = 128   # размер блока AES в битах (16 байт)


def generate_salt() -> bytes:
    """Случайное значение, добавляемое к ключу (аналог CRYPT_CREATE_SALT)."""
    return os.urandom(SALT_SIZE)


def derive_key(passphrase: str, salt: bytes) -> bytes:
    """
    Формирование ключа шифрования из парольной фразы и соли
    (аналог CryptCreateHash + CryptHashData + CryptDeriveKey).
    Хеш-функция — MD5. Длина MD5-хеша (16 байт) совпадает с длиной
    ключа AES-128, поэтому хеш используется как ключ напрямую.
    """
    data = passphrase.encode("utf-8") + salt
    return hashlib.md5(data).digest()


def encrypt_bytes(data: bytes, key: bytes) -> bytes:
    """Шифрование блочным шифром в режиме ECB (аналог CryptEncrypt)."""
    padder = padding.PKCS7(BLOCK_BITS).padder()
    padded = padder.update(data) + padder.finalize()
    encryptor = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    return encryptor.update(padded) + encryptor.finalize()


def decrypt_bytes(data: bytes, key: bytes) -> bytes:
    """
    Расшифрование (аналог CryptDecrypt).
    При неверном ключе дополнение почти всегда не пройдёт проверку,
    и будет выброшено ValueError — вызывающий код трактует это как
    неверную парольную фразу (дополнительно проверяется п. 4 задания:
    наличие записи ADMIN в расшифрованных данных, см. secure_file.py).
    """
    decryptor = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
    padded = decryptor.update(data) + decryptor.finalize()
    unpadder = padding.PKCS7(BLOCK_BITS).unpadder()
    return unpadder.update(padded) + unpadder.finalize()