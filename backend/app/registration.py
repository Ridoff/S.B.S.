import tkinter as tk
from tkinter import messagebox, Frame
from connect import create_connection
from datetime import datetime
import hashlib
from theme import app_theme
from tkinter import ttk


class RegistrationApp:
    def __init__(self, root):
        self.root = root
        self.user_type = tk.IntVar(value=1)  # По умолчанию клиент
        self.setup_ui()

    def setup_ui(self):
        print("Настройка UI для регистрации...")
        self.root.title("Регистрация")
        self.root.geometry(app_theme.sizes['window'])
        self.root.resizable(False, False)
        self.root.configure(bg=app_theme.colors['background'])
        app_theme.center_window(self.root)

        main_frame = Frame(self.root,
                           bg=app_theme.colors['background'],
                           highlightbackground=app_theme.colors['primary'],
                           highlightthickness=2,
                           padx=20,
                           pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        title_label = ttk.Label(main_frame,
                                text="Регистрация",
                                style='Title.TLabel')
        title_label.pack(pady=app_theme.sizes['padding_y'])

        separator = Frame(main_frame,
                          height=2,
                          bg=app_theme.colors['primary'])
        separator.pack(fill=tk.X, pady=10)

        role_frame = Frame(main_frame,
                           bg=app_theme.colors['background'])
        role_frame.pack(pady=5)

        client_radio = ttk.Radiobutton(role_frame,
                                       text="Клиент",
                                       value=1,
                                       variable=self.user_type,
                                       style='Role.TRadiobutton')
        client_radio.pack(side=tk.LEFT, padx=10)

        admin_radio = ttk.Radiobutton(role_frame,
                                      text="Администратор",
                                      value=2,
                                      variable=self.user_type,
                                      style='Role.TRadiobutton')
        admin_radio.pack(side=tk.LEFT, padx=10)

        mod_radio = ttk.Radiobutton(role_frame,
                                    text="Модератор",
                                    value=3,
                                    variable=self.user_type,
                                    style='Role.TRadiobutton')
        mod_radio.pack(side=tk.LEFT, padx=10)

        input_frame = Frame(main_frame,
                            bg=app_theme.colors['background'])
        input_frame.pack(pady=10)

        login_label = ttk.Label(input_frame,
                                text="Логин:",
                                style='TLabel')
        login_label.pack(pady=5)
        self.login_entry = ttk.Entry(input_frame)
        self.login_entry.pack(pady=5)

        password_label = ttk.Label(input_frame,
                                   text="Пароль:",
                                   style='TLabel')
        password_label.pack(pady=5)
        self.password_entry = ttk.Entry(input_frame, show="*")
        self.password_entry.pack(pady=5)

        register_button = ttk.Button(input_frame,
                                     text="Зарегистрироваться",
                                     style='TButton',
                                     command=self.register_user)
        register_button.pack(pady=10)

        back_button = ttk.Button(input_frame,
                                 text="Назад",
                                 style='Secondary.TButton',
                                 command=self.back_to_main)
        back_button.pack(pady=5)

        footer_label = ttk.Label(main_frame,
                                 text="Разное меню Регистрация",
                                 style='Footer.TLabel')
        footer_label.pack(side=tk.BOTTOM, pady=10)

    def back_to_main(self):
        self.root.destroy()
        from main import show_main_menu
        show_main_menu()

    def register_user(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        user_type = self.user_type.get()

        if not login or not password:
            messagebox.showerror("Ошибка", "Все поля обязательны")
            return

        try:
            conn = create_connection()
            if not conn:
                raise Exception("Нет подключения к БД")

            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE login = %s", (login,))
            if cursor.fetchone():
                messagebox.showerror("Ошибка", "Попробуйте другой логин и пароль")
                return

            hashed_pw = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute(
                "INSERT INTO users (user_type, login, password, registration_date) VALUES (%s, %s, %s, %s)",
                (user_type, login, hashed_pw, datetime.now())
            )
            conn.commit()
            messagebox.showinfo("Успех", "Пользователь зарегистрирован")
            self.back_to_main()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка регистрации: {str(e)}")
        finally:
            if conn:
                conn.close()

def run_registration():
    root = tk.Tk()
    app_theme.init_fonts(root)
    app = RegistrationApp(root)
    root.mainloop()