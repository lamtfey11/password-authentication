import struct

REC = struct.Struct("<80si128s??")   # имя | длина пароля | пароль | блокировка | ограничения

data = open("security.db", "rb").read()
print("Размер: %d байт, записей: %d\n" % (len(data), len(data) // REC.size))

for i in range(0, len(data), REC.size):
    name, passlen, pw, block, restrict = REC.unpack(data[i:i + REC.size])
    print("Запись %d:" % (i // REC.size + 1))
    print("  имя:         ", name.rstrip(b"\0").decode("utf-8"))
    print("  длина пароля:", passlen)
    print("  пароль:      ", pw.rstrip(b"\0").decode("utf-8"))
    print("  блокировка:  ", block)
    print("  ограничения: ", restrict)