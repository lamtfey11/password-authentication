"""
Точка входа (лаба №3). Перед запуском главного окна программа запрашивает
парольную фразу и расшифровывает файл учётных данных во временный файл на
диске. После завершения работы программы временный файл шифруется обратно
и удаляется — старое содержимое зашифрованного файла при этом стирается.
"""

import os
import tempfile
import tkinter as tk
from tkinter import messagebox

import secure_file
import storage
from app import App
from config import ENCFILE
from dialogs import PassphraseDialog


def _ask_passphrase(root, prompt, confirm=False):
    return PassphraseDialog(root, prompt, confirm=confirm).show()


def main():
    root = tk.Tk()
    # Не используем withdraw(): на некоторых оконных менеджерах (в т.ч. под WSLg)
    # диалог, подчинённый (transient) полностью скрытому окну, не показывается
    # вовсе, и программа зависает на wait_visibility(). Вместо этого делаем
    # родительское окно маленьким и примерно по центру экрана.
    w, h = 300, 150
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 3
    root.geometry("%dx%d+%d+%d" % (w, h, x, y))

    if os.path.exists(ENCFILE):
        passphrase = _ask_passphrase(
            root, "Введите парольную фразу для доступа к учётным данным:")
        if passphrase is None:
            messagebox.showerror(
                "Парольная фраза",
                "Отказ от ввода парольной фразы.\nРабота программы завершена.")
            root.destroy()
            return

        plain = secure_file.load(ENCFILE, passphrase)
        if plain is None:
            messagebox.showerror(
                "Парольная фраза",
                "Неверная парольная фраза!\nРабота программы завершена.")
            root.destroy()
            return
    else:
        passphrase = _ask_passphrase(
            root,
            "Файл учётных данных не найден.\n"
            "Придумайте парольную фразу для его защиты:",
            confirm=True)
        if passphrase is None:
            messagebox.showerror(
                "Парольная фраза",
                "Отказ от ввода парольной фразы.\nРабота программы завершена.")
            root.destroy()
            return
        plain = storage.default_data()   # запись только ADMIN с пустым паролем

    # расшифрованные данные временно сохраняются в отдельном файле на диске
    fd, temp_path = tempfile.mkstemp(prefix="security_", suffix=".tmp")
    with os.fdopen(fd, "wb") as f:
        f.write(plain)

    root.destroy()   # скрытое окно больше не нужно — у App своё главное окно

    try:
        app = App(temp_path)
        app.mainloop()

        # повторное шифрование изменений
        with open(temp_path, "rb") as f:
            new_plain = f.read()
        secure_file.save(ENCFILE, passphrase, new_plain)
    finally:
        # временный файл с расшифрованными данными удаляется в любом случае
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    main()