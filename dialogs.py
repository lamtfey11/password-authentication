import tkinter as tk
from tkinter import messagebox

from config import ADMIN, MAXNAME, MAXPASS
from password_rules import REQUIREMENTS, check_password


class Dialog(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.result = None
        self.initial_focus = None

        body = tk.Frame(self, padx=20, pady=12)
        body.pack(fill="both", expand=True)
        self.build(body)
        self.make_buttons()

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.on_cancel())

        # по центру родительского окна
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_reqwidth()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_reqheight()) // 3
        self.geometry("+%d+%d" % (max(x, 0), max(y, 0)))

        self.wait_visibility()
        self.grab_set()
        (self.initial_focus or self).focus_set()

    # переопределяются в наследниках
    def build(self, body):
        pass

    def validate(self):
        return True

    def apply(self):
        pass

    def make_buttons(self):
        f = tk.Frame(self, pady=10)
        f.pack()
        tk.Button(f, text="OK", width=10, command=self.on_ok).pack(side="left", padx=8)
        tk.Button(f, text="Отмена", width=10, command=self.on_cancel).pack(side="left", padx=8)

    def on_ok(self):
        if not self.validate():
            return
        self.apply()
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

    def show(self):
        self.wait_window(self)
        return self.result


class LoginDialog(Dialog):
    def __init__(self, parent, name=""):
        self.init_name = name
        super().__init__(parent, "Вход в систему")

    def build(self, body):
        tk.Label(body, text="Введите имя:").grid(row=0, column=0, sticky="w")
        self.e_name = tk.Entry(body, width=32)
        self.e_name.grid(row=1, column=0, pady=(0, 8))
        tk.Label(body, text="Введите пароль:").grid(row=2, column=0, sticky="w")
        self.e_pass = tk.Entry(body, width=32, show="*")   # символы заменяются на '*'
        self.e_pass.grid(row=3, column=0)
        self.e_name.insert(0, self.init_name)
        self.initial_focus = self.e_pass if self.init_name else self.e_name

    def validate(self):
        if not self.e_name.get().strip():
            messagebox.showwarning("Вход в систему", "Введите имя пользователя.", parent=self)
            self.e_name.focus_set()
            return False
        return True

    def apply(self):
        self.result = (self.e_name.get().strip(), self.e_pass.get())


class PasswordDialog(Dialog):
    def __init__(self, parent, account, ask_old, first=False):
        self.account = account
        self.ask_old = ask_old
        self.first = first
        super().__init__(parent, "Установка пароля" if first else "Смена пароля")

    def build(self, body):
        row = 0
        if self.first:
            tk.Label(body, text="Это ваш первый вход. Задайте пароль.").grid(
                row=row, column=0, columnspan=2, sticky="w", pady=(0, 8))
            row += 1
        self.e_old = None
        if self.ask_old:
            tk.Label(body, text="Старый пароль").grid(row=row, column=0, sticky="w", pady=4)
            self.e_old = tk.Entry(body, width=24, show="*")
            self.e_old.grid(row=row, column=1, padx=(10, 0))
            row += 1
        tk.Label(body, text="Новый пароль").grid(row=row, column=0, sticky="w", pady=4)
        self.e_new = tk.Entry(body, width=24, show="*")
        self.e_new.grid(row=row, column=1, padx=(10, 0))
        row += 1
        tk.Label(body, text="Подтверждение").grid(row=row, column=0, sticky="w", pady=4)
        self.e_conf = tk.Entry(body, width=24, show="*")
        self.e_conf.grid(row=row, column=1, padx=(10, 0))
        row += 1
        if self.account.restrict:
            tk.Label(body, text=REQUIREMENTS, wraplength=300, justify="left", fg="#555").grid(
                row=row, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.initial_focus = self.e_old or self.e_new

    def _error(self, text, widget):
        messagebox.showerror("Смена пароля", text, parent=self)
        widget.focus_set()
        return False

    def validate(self):
        new, conf = self.e_new.get(), self.e_conf.get()
        if self.ask_old and self.e_old.get() != self.account.password:
            self.e_old.delete(0, "end")
            return self._error("Неверный старый пароль!", self.e_old)
        if new != conf:
            self.e_conf.delete(0, "end")
            return self._error("Пароли должны совпадать!", self.e_new)
        if not new:
            return self._error("Пароль не может быть пустым!", self.e_new)
        if len(new) > MAXPASS:
            return self._error("Пароль слишком длинный (максимум %d символов)." % MAXPASS,
                               self.e_new)
        if self.account.restrict and not check_password(new):
            self.e_conf.delete(0, "end")
            return self._error("Пароль не соответствует ограничениям!\n" + REQUIREMENTS,
                               self.e_new)
        return True

    def apply(self):
        self.result = self.e_new.get()


class AddUserDialog(Dialog):
    def __init__(self, parent, store):
        self.store = store
        super().__init__(parent, "Добавление пользователя")

    def build(self, body):
        tk.Label(body, text="Имя нового пользователя").grid(row=0, column=0, sticky="w", pady=4)
        self.e_name = tk.Entry(body, width=24)
        self.e_name.grid(row=0, column=1, padx=(10, 0))
        self.v_block = tk.BooleanVar(value=False)
        self.v_restrict = tk.BooleanVar(value=True)
        tk.Checkbutton(body, text="Блокировка", variable=self.v_block).grid(
            row=1, column=0, columnspan=2, sticky="w")
        tk.Checkbutton(body, text="Парольное ограничение", variable=self.v_restrict).grid(
            row=2, column=0, columnspan=2, sticky="w")
        self.initial_focus = self.e_name

    def validate(self):
        name = self.e_name.get().strip()
        if not name:
            messagebox.showwarning("Добавление пользователя", "Введите имя пользователя.", parent=self)
            self.e_name.focus_set()
            return False
        if len(name) > MAXNAME:
            messagebox.showerror("Добавление пользователя",
                                 "Имя слишком длинное (максимум %d символов)." % MAXNAME, parent=self)
            return False
        if any(a.name.lower() == name.lower() for a in self.store.read_all()):
            messagebox.showerror("Добавление пользователя",
                                 "Пользователь %s\nуже зарегистрирован!" % name, parent=self)
            self.e_name.focus_set()
            return False
        return True

    def apply(self):
        self.result = (self.e_name.get().strip(), self.v_block.get(), self.v_restrict.get())


class UsersDialog(Dialog):
    def __init__(self, parent, store):
        self.store = store
        self.accounts = store.read_all()
        self.cur = 0
        super().__init__(parent, "Список пользователей")

    def build(self, body):
        self.v_name = tk.StringVar()
        self.v_block = tk.BooleanVar()
        self.v_restrict = tk.BooleanVar()
        tk.Label(body, text="Имя пользователя:").grid(row=0, column=0, sticky="w", pady=4)
        tk.Entry(body, textvariable=self.v_name, state="readonly", width=24).grid(
            row=0, column=1, padx=(10, 0))
        self.c_block = tk.Checkbutton(body, text="Блокировка", variable=self.v_block)
        self.c_block.grid(row=1, column=0, columnspan=2, sticky="w")
        tk.Checkbutton(body, text="Парольное ограничение", variable=self.v_restrict).grid(
            row=2, column=0, columnspan=2, sticky="w")
        self.lbl_pos = tk.Label(body, fg="#555")
        self.lbl_pos.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))

    def make_buttons(self):
        f = tk.Frame(self, pady=8)
        f.pack()
        self.btn_prev = tk.Button(f, text="Предыдущий", width=12, command=self.go_prev)
        self.btn_next = tk.Button(f, text="Следующий", width=12, command=self.go_next)
        self.btn_prev.grid(row=0, column=0, padx=6, pady=3)
        self.btn_next.grid(row=0, column=1, padx=6, pady=3)
        tk.Button(f, text="Сохранить", width=12, command=self.save).grid(
            row=1, column=0, columnspan=2, pady=3)
        tk.Button(f, text="Ok", width=12, command=self.on_ok).grid(row=2, column=0, padx=6, pady=3)
        tk.Button(f, text="Отмена", width=12, command=self.on_cancel).grid(
            row=2, column=1, padx=6, pady=3)
        self._load(0)

    def _load(self, i):
        self.cur = i
        a = self.accounts[i]
        self.v_name.set(a.name)
        self.v_block.set(a.block)
        self.v_restrict.set(a.restrict)
        # администратора заблокировать нельзя (иначе некому будет управлять)
        self.c_block.config(state="disabled" if a.name == ADMIN else "normal")
        self.btn_prev.config(state="normal" if i > 0 else "disabled")
        self.btn_next.config(state="normal" if i < len(self.accounts) - 1 else "disabled")
        self.lbl_pos.config(text="Запись %d из %d" % (i + 1, len(self.accounts)))

    def _dirty(self):
        a = self.accounts[self.cur]
        return self.v_block.get() != a.block or self.v_restrict.get() != a.restrict

    def save(self):
        a = self.accounts[self.cur]
        a.block = self.v_block.get()
        a.restrict = self.v_restrict.get()
        self.store.write(self.cur, a)

    def _confirm_leave(self):
        if not self._dirty():
            return True
        ans = messagebox.askyesnocancel(
            "Список пользователей",
            "Сохранить изменения для «%s»?" % self.accounts[self.cur].name, parent=self)
        if ans is None:
            return False
        if ans:
            self.save()
        else:
            self._load(self.cur)
        return True

    def go_prev(self):
        if self.cur > 0 and self._confirm_leave():
            self._load(self.cur - 1)

    def go_next(self):
        if self.cur < len(self.accounts) - 1 and self._confirm_leave():
            self._load(self.cur + 1)

    def on_ok(self):
        if self._confirm_leave():
            self.destroy()