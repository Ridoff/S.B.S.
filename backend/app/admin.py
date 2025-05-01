import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from connect import create_connection
from theme import app_theme

class AdminDashboard:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.user_id = self.get_user_id()
        self.setup_ui()

    def get_user_id(self):
        """Получает ID текущего пользователя по логину"""
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE login = %s", (self.username,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить ID пользователя: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def setup_ui(self):
        self.root.title(f"Панель администратора - {self.username}")
        self.root.geometry("600x750")
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

        create_company_btn = ttk.Button(
            buttons_frame,
            text="Создать компанию",
            style='TButton',
            command=self.create_company
        )
        create_company_btn.pack(fill=tk.X, pady=10)

        create_restaurant_btn = ttk.Button(
            buttons_frame,
            text="Создать ресторан",
            style='TButton',
            command=self.create_restaurant
        )
        create_restaurant_btn.pack(fill=tk.X, pady=10)

        create_hall_btn = ttk.Button(
            buttons_frame,
            text="Создать зал",
            style='TButton',
            command=self.create_hall
        )
        create_hall_btn.pack(fill=tk.X, pady=10)

        manage_reservations_btn = ttk.Button(
            buttons_frame,
            text="Управление бронированиями",
            style='TButton',
            command=self.show_manage_reservations
        )
        manage_reservations_btn.pack(fill=tk.X, pady=10)

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

    def show_profile(self):
        """Показывает профиль текущего пользователя"""
        profile_window = tk.Toplevel(self.root)
        profile_window.title(f"Мой профиль")
        profile_window.geometry("500x400")
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
            text="Мой профиль",
            style='Title.TLabel'
        ).pack(pady=10)

        tk.Frame(
            main_frame,
            height=2,
            bg=app_theme.colors['primary']
        ).pack(fill=tk.X, pady=10)

        info_frame = tk.Frame(main_frame, bg=app_theme.colors['background'])
        info_frame.pack(pady=15)

        try:
            conn = create_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT u.login, u.user_type, u.registration_date, 
                       a.position, a.created_at
                FROM users u
                LEFT JOIN administrators a ON u.id = a.user_id
                WHERE u.id = %s
            """, (self.user_id,))

            user_data = cursor.fetchone()

            ttk.Label(
                info_frame,
                text=f"Логин: {user_data[0]}",
                style='TLabel'
            ).pack(anchor='w', pady=5)

            user_type = "Обычный пользователь" if user_data[1] == 1 else "Модератор" if user_data[1] == 2 else "Администратор"
            ttk.Label(
                info_frame,
                text=f"Тип пользователя: {user_type}",
                style='TLabel'
            ).pack(anchor='w', pady=5)

            reg_date = user_data[2].strftime('%d.%m.%Y') if user_data[2] else "не указана"
            ttk.Label(
                info_frame,
                text=f"Дата регистрации: {reg_date}",
                style='TLabel'
            ).pack(anchor='w', pady=5)

            if user_data[3]:
                ttk.Label(
                    info_frame,
                    text=f"Должность: {user_data[3]}",
                    style='TLabel'
                ).pack(anchor='w', pady=5)

                admin_since = user_data[4].strftime('%d.%m.%Y') if user_data[4] else "не указана"
                ttk.Label(
                    info_frame,
                    text=f"Администратор с: {admin_since}",
                    style='TLabel'
                ).pack(anchor='w', pady=5)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные профиля: {e}")
        finally:
            if conn:
                conn.close()

        ttk.Button(
            main_frame,
            text="Закрыть",
            style='Secondary.TButton',
            command=profile_window.destroy
        ).pack(pady=10)

    def create_company(self):
        """Создание компании"""
        company_window = tk.Toplevel(self.root)
        company_window.title("Создать компанию")
        company_window.geometry("400x300")
        company_window.configure(bg=app_theme.colors['background'])
        app_theme.center_window(company_window)

        main_frame = tk.Frame(
            company_window,
            bg=app_theme.colors['background'],
            padx=20,
            pady=20
        )
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(
            main_frame,
            text="Создать компанию",
            style='Title.TLabel'
        ).pack(pady=10)

        tk.Frame(
            main_frame,
            height=2,
            bg=app_theme.colors['primary']
        ).pack(fill=tk.X, pady=10)

        form_frame = tk.Frame(main_frame, bg=app_theme.colors['background'])
        form_frame.pack(pady=15)

        ttk.Label(
            form_frame,
            text="Название компании:",
            style='TLabel'
        ).pack(anchor='w', pady=5)
        company_name_entry = ttk.Entry(form_frame, width=30)
        company_name_entry.pack(anchor='w', pady=5)

        def submit_company():
            company_name = company_name_entry.get()

            if not company_name:
                messagebox.showwarning("Ошибка", "Введите название компании")
                return

            try:
                conn = create_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO companies (name)
                    VALUES (%s)
                """, (company_name,))
                conn.commit()

                messagebox.showinfo("Успех", "Компания успешно создана")
                company_window.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при создании компании: {e}")
            finally:
                if conn:
                    conn.close()

        ttk.Button(
            main_frame,
            text="Создать",
            style='TButton',
            command=submit_company
        ).pack(pady=10)

        ttk.Button(
            main_frame,
            text="Отмена",
            style='Secondary.TButton',
            command=company_window.destroy
        ).pack(pady=5)

    def create_restaurant(self):
        """Создание ресторана"""
        restaurant_window = tk.Toplevel(self.root)
        restaurant_window.title("Создать ресторан")
        restaurant_window.geometry("500x600")
        restaurant_window.configure(bg=app_theme.colors['background'])
        app_theme.center_window(restaurant_window)

        main_frame = tk.Frame(
            restaurant_window,
            bg=app_theme.colors['background'],
            padx=20,
            pady=20
        )
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(
            main_frame,
            text="Создать ресторан",
            style='Title.TLabel'
        ).pack(pady=10)

        tk.Frame(
            main_frame,
            height=2,
            bg=app_theme.colors['primary']
        ).pack(fill=tk.X, pady=10)

        form_frame = tk.Frame(main_frame, bg=app_theme.colors['background'])
        form_frame.pack(pady=15)

        ttk.Label(
            form_frame,
            text="ID компании:",
            style='TLabel'
        ).pack(anchor='w', pady=5)
        company_id_entry = ttk.Entry(form_frame, width=30)
        company_id_entry.pack(anchor='w', pady=5)

        ttk.Label(
            form_frame,
            text="Название ресторана:",
            style='TLabel'
        ).pack(anchor='w', pady=5)
        restaurant_name_entry = ttk.Entry(form_frame, width=30)
        restaurant_name_entry.pack(anchor='w', pady=5)

        ttk.Label(
            form_frame,
            text="Телефон ресторана:",
            style='TLabel'
        ).pack(anchor='w', pady=5)
        restaurant_phone_entry = ttk.Entry(form_frame, width=30)
        restaurant_phone_entry.pack(anchor='w', pady=5)

        ttk.Label(
            form_frame,
            text="Описание ресторана:",
            style='TLabel'
        ).pack(anchor='w', pady=5)
        restaurant_desc_entry = tk.Text(form_frame, height=3, width=30)
        restaurant_desc_entry.pack(anchor='w', pady=5)

        def submit_restaurant():
            company_id = company_id_entry.get()
            restaurant_name = restaurant_name_entry.get()
            restaurant_phone = restaurant_phone_entry.get()
            restaurant_desc = restaurant_desc_entry.get("1.0", tk.END).strip()

            if not company_id or not restaurant_name:
                messagebox.showwarning("Ошибка", "Заполните все обязательные поля")
                return

            if not company_id.isdigit():
                messagebox.showwarning("Ошибка", "ID компании должен быть числом")
                return

            try:
                conn = create_connection()
                cursor = conn.cursor()

                cursor.execute("SELECT id FROM companies WHERE id = %s", (int(company_id),))
                if not cursor.fetchone():
                    messagebox.showwarning("Ошибка", "Компания с таким ID не существует")
                    return

                cursor.execute("""
                    INSERT INTO restaurants (company_id, name, phone, description)
                    VALUES (%s, %s, %s, %s)
                """, (int(company_id), restaurant_name, restaurant_phone, restaurant_desc))
                conn.commit()

                messagebox.showinfo("Успех", "Ресторан успешно создан")
                restaurant_window.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при создании ресторана: {e}")
            finally:
                if conn:
                    conn.close()

        ttk.Button(
            main_frame,
            text="Создать",
            style='TButton',
            command=submit_restaurant
        ).pack(pady=10)

        ttk.Button(
            main_frame,
            text="Отмена",
            style='Secondary.TButton',
            command=restaurant_window.destroy
        ).pack(pady=5)

    def create_hall(self):
        """Создание зала"""
        hall_window = tk.Toplevel(self.root)
        hall_window.title("Создать зал")
        hall_window.geometry("400x500")
        hall_window.configure(bg=app_theme.colors['background'])
        app_theme.center_window(hall_window)

        main_frame = tk.Frame(
            hall_window,
            bg=app_theme.colors['background'],
            padx=20,
            pady=20
        )
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(
            main_frame,
            text="Создать зал",
            style='Title.TLabel'
        ).pack(pady=10)

        tk.Frame(
            main_frame,
            height=2,
            bg=app_theme.colors['primary']
        ).pack(fill=tk.X, pady=10)

        form_frame = tk.Frame(main_frame, bg=app_theme.colors['background'])
        form_frame.pack(pady=15)

        ttk.Label(
            form_frame,
            text="ID ресторана:",
            style='TLabel'
        ).pack(anchor='w', pady=5)
        restaurant_id_entry = ttk.Entry(form_frame, width=30)
        restaurant_id_entry.pack(anchor='w', pady=5)

        ttk.Label(
            form_frame,
            text="Название зала:",
            style='TLabel'
        ).pack(anchor='w', pady=5)
        hall_name_entry = ttk.Entry(form_frame, width=30)
        hall_name_entry.pack(anchor='w', pady=5)

        ttk.Label(
            form_frame,
            text="Максимальная вместимость:",
            style='TLabel'
        ).pack(anchor='w', pady=5)
        hall_capacity_entry = ttk.Entry(form_frame, width=30)
        hall_capacity_entry.pack(anchor='w', pady=5)

        def submit_hall():
            restaurant_id = restaurant_id_entry.get()
            hall_name = hall_name_entry.get()
            hall_capacity = hall_capacity_entry.get()

            if not restaurant_id or not hall_name or not hall_capacity:
                messagebox.showwarning("Ошибка", "Заполните все обязательные поля")
                return

            if not restaurant_id.isdigit() or not hall_capacity.isdigit():
                messagebox.showwarning("Ошибка", "ID ресторана и вместимость должны быть числами")
                return

            if int(hall_capacity) <= 0:
                messagebox.showwarning("Ошибка", "Вместимость должна быть положительным числом")
                return

            try:
                conn = create_connection()
                cursor = conn.cursor()

                cursor.execute("SELECT id FROM restaurants WHERE id = %s", (int(restaurant_id),))
                if not cursor.fetchone():
                    messagebox.showwarning("Ошибка", "Ресторан с таким ID не существует")
                    return

                cursor.execute("""
                    INSERT INTO halls (restaurant_id, name, max_capacity)
                    VALUES (%s, %s, %s)
                """, (int(restaurant_id), hall_name, int(hall_capacity)))
                conn.commit()

                messagebox.showinfo("Успех", "Зал успешно создан")
                hall_window.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при создании зала: {e}")
            finally:
                if conn:
                    conn.close()

        ttk.Button(
            main_frame,
            text="Создать",
            style='TButton',
            command=submit_hall
        ).pack(pady=10)

        ttk.Button(
            main_frame,
            text="Отмена",
            style='Secondary.TButton',
            command=hall_window.destroy
        ).pack(pady=5)

    def show_manage_reservations(self):
        """Окно для управления бронированиями"""
        reservations_window = tk.Toplevel(self.root)
        reservations_window.title("Управление бронированиями")
        reservations_window.geometry("1000x700")
        reservations_window.configure(bg=app_theme.colors['background'])
        app_theme.center_window(reservations_window)

        main_frame = tk.Frame(
            reservations_window,
            bg=app_theme.colors['background'],
            padx=20,
            pady=20
        )
        main_frame.pack(expand=True, fill=tk.BOTH)

        control_frame = tk.Frame(main_frame, bg=app_theme.colors['background'])
        control_frame.pack(fill=tk.X, pady=10)

        ttk.Label(
            control_frame,
            text="ID ресторана:",
            style='TLabel'
        ).pack(side=tk.LEFT, padx=5)

        self.restaurant_id_entry = ttk.Entry(control_frame, width=10)
        self.restaurant_id_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="Показать бронирования",
            style='TButton',
            command=self.load_restaurant_reservations
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="Отменить бронирование",
            style='TButton',
            command=self.cancel_reservation
        ).pack(side=tk.LEFT, padx=5)

        tree_frame = tk.Frame(main_frame, bg=app_theme.colors['background'])
        tree_frame.pack(expand=True, fill=tk.BOTH, pady=10)

        columns = ("id", "restaurant", "table", "date", "time", "guests", "status", "user_id")
        self.reservations_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style='Custom.Treeview'
        )

        col_widths = [50, 200, 100, 100, 150, 70, 100, 70]
        for col, text, width in zip(columns,
                                    ["ID", "Ресторан", "Стол", "Дата", "Время", "Гости", "Статус", "User ID"],
                                    col_widths):
            self.reservations_tree.heading(col, text=text)
            self.reservations_tree.column(col, width=width, anchor='center')

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.reservations_tree.yview)
        self.reservations_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.reservations_tree.pack(expand=True, fill=tk.BOTH)

        ttk.Button(
            main_frame,
            text="Закрыть",
            style='Secondary.TButton',
            command=reservations_window.destroy
        ).pack(pady=10)

    def load_restaurant_reservations(self):
        """Загрузка бронирований для указанного ресторана, где пользователь является сотрудником"""
        restaurant_id = self.restaurant_id_entry.get()
        if not restaurant_id.isdigit():
            messagebox.showwarning("Ошибка", "Введите корректный ID ресторана")
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT e.id
                FROM employees e
                WHERE e.user_id = %s AND e.restaurant_id = %s
            """, (self.user_id, int(restaurant_id)))
            if not cursor.fetchone():
                messagebox.showwarning("Ошибка", "Вы не являетесь сотрудником этого ресторана")
                return

            for item in self.reservations_tree.get_children():
                self.reservations_tree.delete(item)

            cursor.execute("""
                SELECT r.id, res.name, t.name,
                       TO_CHAR(r.start_time, 'DD.MM.YYYY'),
                       CONCAT(
                           TO_CHAR(r.start_time, 'HH24:MI'), ' - ',
                           TO_CHAR(r.end_time, 'HH24:MI')
                       ),
                       r.guests_count, r.status, r.user_id
                FROM reservations r
                JOIN restaurants res ON r.restaurant_id = res.id
                JOIN tables t ON r.table_id = t.id
                WHERE r.restaurant_id = %s
                ORDER BY r.start_time DESC
            """, (int(restaurant_id),))

            for row in cursor.fetchall():
                self.reservations_tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки бронирований: {e}")
        finally:
            if conn:
                conn.close()

    def cancel_reservation(self):
        """Отмена выбранного бронирования"""
        selected = self.reservations_tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите бронирование из списка")
            return

        reservation_data = self.reservations_tree.item(selected)['values']
        reservation_id = reservation_data[0]
        status = reservation_data[6]

        if status.lower() == "отменено":
            messagebox.showwarning("Ошибка", "Это бронирование уже отменено")
            return

        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите отменить это бронирование?")
        if not confirm:
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE reservations 
                SET status = 'отменено'
                WHERE id = %s
            """, (reservation_id,))
            conn.commit()

            messagebox.showinfo("Успех", "Бронирование успешно отменено")
            self.load_restaurant_reservations()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при отмене бронирования: {e}")
        finally:
            if conn:
                conn.close()

    def logout(self):
        """Выход из системы"""
        self.root.destroy()

def run_admin_dashboard(username):
    root = tk.Tk()
    app_theme.init_fonts(root)
    AdminDashboard(root, username)
    root.mainloop()