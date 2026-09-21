import tkinter as tk
from tkinter import messagebox

from config import ADMIN, AUTHOR, MAX_ATTEMPTS, SECFILE, VARIANT, VARIANT_TEXT
from dialogs import AddUserDialog, LoginDialog, PasswordDialog, UsersDialog
from storage import Account, AccountFile


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Работы №1")
        self.geometry("640x480")
        self.store = AccountFile(SECFILE)
        try:
            self.store.ensure_exists()
        except OSError as e:
            messagebox.showerror("Ошибка", "Не удалось создать файл учётных записей:\n%s" % e)
            self.destroy()
            raise SystemExit(1)

        self.current = None    # имя вошедшего пользователя
        self.attempts = 0      # число неверных вводов пароля

        # меню
        menubar = tk.Menu(self)
        self.menu_users = tk.Menu(menubar, tearoff=0)
        self.menu_users.add_command(label="Смена пароля", command=self.change_password, state="disabled")
        self.menu_users.add_command(label="Новый пользователь", command=self.new_user, state="disabled")
        self.menu_users.add_command(label="Все пользователи", command=self.all_users, state="disabled")
        self.menu_users.add_separator()
        self.menu_users.add_command(label="Выход", command=self.destroy)
        menubar.add_cascade(label="Пользователи", menu=self.menu_users)

        menu_help = tk.Menu(menubar, tearoff=0)
        menu_help.add_command(label="О программе", command=self.about)
        menubar.add_cascade(label="Справка", menu=menu_help)
        self.config(menu=menubar)

        # строка состояния и кнопка входа
        self.status = tk.Label(self, text="Вход не выполнен", bd=1, relief="sunken", anchor="w")
        self.status.pack(side="bottom", fill="x")
        self.btn_login = tk.Button(self, text="Вход в систему", command=self.login)
        self.btn_login.place(relx=0.5, rely=0.4, anchor="center")

    # вход
    def login(self):
        self._end_session() 
        name = ""
        while True:
            res = LoginDialog(self, name).show()
            if res is None:  # «Отмена» — просто закрыть окно входа
                return
            name, pw = res

            found = self.store.find(name)
            if found is None:
                if messagebox.askretrycancel(
                        "Вход в систему",
                        "Вы не зарегистрированы!\n\nПовторить — ввести имя ещё раз,\n"
                        "Отмена — завершить работу программы.", parent=self):
                    name = ""
                    continue
                self.destroy()
                return
            idx, acc = found

            if acc.password == "":
                # первый вход: пароль задаётся (с подтверждением) пользователем
                if acc.block:
                    messagebox.showerror("Вход в систему", "Вы заблокированы!", parent=self)
                    return
                new = PasswordDialog(self, acc, ask_old=False, first=True).show()
                if new is None:  # отказ от ввода пароля — завершение работы
                    self.destroy()
                    return
                acc.password = new
                self.store.write(idx, acc)
            elif pw != acc.password:
                self.attempts += 1
                if self.attempts >= MAX_ATTEMPTS:
                    messagebox.showerror("Вход в систему", "Вход в программу невозможен!", parent=self)
                    self.destroy()
                    return
                messagebox.showerror(
                    "Вход в систему",
                    "Неверный пароль!\nОсталось попыток: %d" % (MAX_ATTEMPTS - self.attempts),
                    parent=self)
                continue

            if acc.block:
                messagebox.showerror("Вход в систему", "Вы заблокированы!", parent=self)
                return

            self._start_session(acc)
            return

    def _end_session(self):
        self.current = None
        for label in ("Смена пароля", "Новый пользователь", "Все пользователи"):
            self.menu_users.entryconfig(label, state="disabled")
        self.status.config(text="Вход не выполнен")

    def _start_session(self, acc):
        self.current = acc.name
        self.attempts = 0
        is_admin = acc.name == ADMIN
        self.menu_users.entryconfig("Смена пароля", state="normal")
        state = "normal" if is_admin else "disabled"
        self.menu_users.entryconfig("Новый пользователь", state=state)
        self.menu_users.entryconfig("Все пользователи", state=state)
        self.status.config(text="Пользователь: %s (%s)" % (
            acc.name, "администратор" if is_admin else "обычный пользователь"))

    # команды меню
    def change_password(self):
        found = self.store.find(self.current)
        if found is None:
            messagebox.showerror("Смена пароля", "Учётная запись не найдена.", parent=self)
            return
        idx, acc = found
        new = PasswordDialog(self, acc, ask_old=True).show()
        if new is not None:
            acc.password = new
            self.store.write(idx, acc)
            messagebox.showinfo("Смена пароля", "Пароль успешно изменён.", parent=self)

    def new_user(self):
        res = AddUserDialog(self, self.store).show()
        if res is not None:
            name, block, restrict = res
            self.store.append(Account(name, "", block, restrict))   # пустой пароль
            messagebox.showinfo("Новый пользователь",
                                "Пользователь %s добавлен.\nПароль он задаст при первом входе." % name,
                                parent=self)

    def all_users(self):
        UsersDialog(self, self.store).show()

    def about(self):
        messagebox.showinfo(
            "О программе",
            "Лабораторная работа №1\n"
            "Разграничение полномочий пользователей на основе парольной аутентификации\n\n"
            "Автор: %s\nВариант задания: %d\n%s" % (AUTHOR, VARIANT, VARIANT_TEXT),
            parent=self)

    def report_callback_exception(self, exc, val, tb):
        messagebox.showerror("Ошибка", str(val), parent=self)