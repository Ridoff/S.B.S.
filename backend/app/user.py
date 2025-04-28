import tkinter as tk
from tkinter import ttk, messagebox
from connect import create_connection
from theme import app_theme

def fix_encoding(text):
    """Исправляет неправильную кодировку текста"""
    if isinstance(text, str):
        try:
            return text.encode('latin1').decode('cp1251')
        except Exception:
            return text
    return text

class UserDashboard:
    def __init__(self, root, user_id, username):
        self.root = root
        self.user_id = user_id
        self.username = username
        self.setup_ui()

    def setup_ui(self):
        self.root.title(f"Личный кабинет - {self.username}")
        self.root.geometry(app_theme.sizes['window'])
        self.root.resizable(False, False)
        self.root.configure(bg=app_theme.colors['background'])
        app_theme.center_window(self.root)

        main_frame = tk.Frame(
            self.root,
            bg=app_theme.colors['background'],
            highlightbackground=app_theme.colors['primary'],
            highlightthickness=2,
            padx=20,
            pady=20
        )
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        title_label = ttk.Label(
            main_frame,
            text=f"Добро пожаловать, {self.username}",
            style='Title.TLabel'
        )
        title_label.pack(pady=app_theme.sizes['padding_y'])

        separator = tk.Frame(
            main_frame,
            height=2,
            bg=app_theme.colors['primary']
        )
        separator.pack(fill=tk.X, pady=10)

        buttons_frame = tk.Frame(
            main_frame,
            bg=app_theme.colors['background']
        )
        buttons_frame.pack(pady=20)

        profile_btn = ttk.Button(
            buttons_frame,
            text="Мой профиль",
            style='TButton',
            command=self.show_profile
        )
        profile_btn.pack(fill=tk.X, pady=10)

        orders_btn = ttk.Button(
            buttons_frame,
            text="Мои бронирования",
            style='TButton',
            command=self.show_user_reservations
        )
        orders_btn.pack(fill=tk.X, pady=10)

        new_order_btn = ttk.Button(
            buttons_frame,
            text="Сделать бронь",
            style='TButton',
            command=self.make_reservation
        )
        new_order_btn.pack(fill=tk.X, pady=10)

        logout_btn = ttk.Button(
            buttons_frame,
            text="Выйти",
            style='Secondary.TButton',
            command=self.logout
        )
        logout_btn.pack(fill=tk.X, pady=10)

        footer_label = ttk.Label(
            main_frame,
            text="© 2025 Smart Booking System for Restaurants and Cafés",
            style='Footer.TLabel'
        )
        footer_label.pack(side=tk.BOTTOM, pady=10)

    def fetch_reservations(self):
        """Получает бронирования пользователя из БД"""
        try:
            conn = create_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT r.id, res.name, t.name,
                    r.start_time::date,
                    CONCAT(
                        TO_CHAR(r.start_time, 'HH24:MI'), ' - ',
                        TO_CHAR(r.end_time, 'HH24:MI')
                    ),
                    r.guests_count, r.status
                FROM reservations r
                JOIN restaurants res ON r.restaurant_id = res.id
                JOIN tables t ON r.table_id = t.id
                WHERE r.user_id = %s
                ORDER BY r.start_time DESC
            """, (self.user_id,))

            rows = cursor.fetchall()

            fixed_rows = []
            for row in rows:
                fixed_row = tuple(fix_encoding(value) if isinstance(value, str) else value for value in row)
                fixed_rows.append(fixed_row)

            return fixed_rows

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки бронирований: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def make_reservation(self):
        print("функция для брони")

    def show_user_reservations(self):
        """Окно всех бронирований пользователя"""
        self.reservations_window = tk.Toplevel(self.root)
        self.reservations_window.title("Мои бронирования")
        self.reservations_window.geometry("850x650")
        self.reservations_window.configure(bg=app_theme.colors['background'])
        app_theme.center_window(self.reservations_window)

        main_frame = tk.Frame(
            self.reservations_window,
            bg=app_theme.colors['background'],
            padx=20,
            pady=20
        )
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(
            main_frame,
            text="Мои бронирования",
            style='Title.TLabel'
        ).pack(pady=10)

        tk.Frame(
            main_frame,
            height=2,
            bg=app_theme.colors['primary']
        ).pack(fill=tk.X, pady=10)

        tree_frame = tk.Frame(main_frame, bg=app_theme.colors['background'])
        tree_frame.pack(expand=True, fill=tk.BOTH, pady=10)

        columns = ("id", "restaurant", "table", "date", "time", "guests", "status")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style='Custom.Treeview'
        )

        for col, text in zip(columns, ["ID", "Ресторан", "Стол", "Дата", "Время", "Гости", "Статус"]):
            self.tree.heading(col, text=text)

        self.tree.column("id", width=50, anchor='center')
        self.tree.column("restaurant", width=200)
        self.tree.column("table", width=100, anchor='center')
        self.tree.column("date", width=110, anchor='center')
        self.tree.column("time", width=150, anchor='center')
        self.tree.column("guests", width=60, anchor='center')
        self.tree.column("status", width=100, anchor='center')

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill=tk.BOTH)

        self.load_reservations()

        ttk.Button(
            main_frame,
            text="Обновить",
            style='Secondary.TButton',
            command=self.load_reservations
        ).pack(pady=10)

        ttk.Button(
            main_frame,
            text="Закрыть",
            style='Secondary.TButton',
            command=self.reservations_window.destroy
        ).pack(pady=10)

    def load_reservations(self):
        """Загружает и обновляет бронирования в таблице"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        reservations = self.fetch_reservations()
        if not reservations:
            messagebox.showinfo("Информация", "У вас нет активных бронирований.")
            return

        for res in reservations:
            self.tree.insert("", "end", values=res)

    def show_profile(self):
        """Профиль пользователя"""
        profile_window = tk.Toplevel(self.root)
        profile_window.title(f"Профиль пользователя #{self.user_id}")
        profile_window.geometry("500x400")
        profile_window.resizable(False, False)
        profile_window.configure(bg=app_theme.colors['background'])
        app_theme.center_window(profile_window)

        main_frame = tk.Frame(
            profile_window,
            bg=app_theme.colors['background'],
            padx=20,
            pady=20
        )
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(
            main_frame,
            text="Профиль пользователя",
            style='Title.TLabel'
        ).pack(pady=10)

        tk.Frame(
            main_frame,
            height=2,
            bg=app_theme.colors['primary']
        ).pack(fill=tk.X, pady=10)

        data_frame = tk.Frame(main_frame, bg=app_theme.colors['background'])
        data_frame.pack(pady=15)

        ttk.Label(
            data_frame,
            text=f"Логин: {self.username}",
            style='TLabel'
        ).pack(anchor='w', pady=5)

        try:
            conn = create_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT registration_date FROM users WHERE id = %s", (self.user_id,))
            reg_date = cursor.fetchone()

            if reg_date and reg_date[0]:
                date_str = reg_date[0].strftime('%d.%m.%Y')
            else:
                date_str = "не указана"

            ttk.Label(
                data_frame,
                text=f"Дата регистрации: {date_str}",
                style='TLabel'
            ).pack(anchor='w', pady=5)

        except Exception as e:
            ttk.Label(
                data_frame,
                text=f"Ошибка загрузки даты: {str(e)}",
                style='TLabel',
                foreground='red'
            ).pack(anchor='w', pady=5)
        finally:
            if conn:
                conn.close()

        ttk.Button(
            main_frame,
            text="Закрыть",
            style='Secondary.TButton',
            command=profile_window.destroy
        ).pack(pady=10)

    def logout(self):
        """Выход из личного кабинета"""
        self.root.destroy()

def run_user_dashboard(user_id, username):
    root = tk.Tk()
    app_theme.init_fonts(root)
    UserDashboard(root, user_id, username)
    root.mainloop()
