import sys
sys.path.insert(0, ".")  # запускать из папки проекта
import getpass

import secure_file
import storage
from config import ENCFILE

passphrase = getpass.getpass("Парольная фраза: ")
plain = secure_file.load(ENCFILE, passphrase)

if plain is None:
    print("Неверная парольная фраза или файл повреждён.")
else:
    accounts = storage.parse_accounts(plain)
    print("Записей: %d\n" % len(accounts))
    for i, a in enumerate(accounts, 1):
        print("Запись %d:" % i)
        print("  имя:         ", a.name)
        print("  пароль:      ", a.password)
        print("  блокировка:  ", a.block)
        print("  ограничения: ", a.restrict)