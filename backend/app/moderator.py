import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from connect import create_connection
from theme import app_theme


class ModeratorDashboard:
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

        view_users_btn = ttk.Button(
            buttons_frame,
            text="Управление пользователями",
            style='TButton',
            command=self.show_users_management
        )
        view_users_btn.pack(fill=tk.X, pady=10)

        reservations_btn = ttk.Button(
            buttons_frame,
            text="Управление бронированиями",
            style='TButton',
            command=self.show_reservations_management
        )
        reservations_btn.pack(fill=tk.X, pady=10)

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
                       a.position, a.created_at, c.name
                FROM users u
                LEFT JOIN administrators a ON u.id = a.user_id
                LEFT JOIN companies c ON a.company_id = c.id
                WHERE u.id = %s
            """, (self.user_id,))

            user_data = cursor.fetchone()

            ttk.Label(
                info_frame,
                text=f"Логин: {user_data[0]}",
                style='TLabel'
            ).pack(anchor='w', pady=5)

            user_type = "Обычный пользователь" if user_data[1] == 1 else "Модератор" if user_data[
                                                                                            1] == 2 else "Администратор"
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

                if user_data[5]:
                    ttk.Label(
                        info_frame,
                        text=f"Компания: {user_data[5]}",
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

    def show_users_management(self):
        """Окно управления пользователями и администраторами"""
        users_window = tk.Toplevel(self.root)
        users_window.title("Управление пользователями")
        users_window.geometry("1100x700")
        users_window.configure(bg=app_theme.colors['background'])
        app_theme.center_window(users_window)

        main_frame = tk.Frame(
            users_window,
            bg=app_theme.colors['background'],
            padx=20,
            pady=20
        )
        main_frame.pack(expand=True, fill=tk.BOTH)

        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill=tk.BOTH)

        users_tab = tk.Frame(notebook, bg=app_theme.colors['background'])
        notebook.add(users_tab, text="Пользователи")

        moderators_tab = tk.Frame(notebook, bg=app_theme.colors['background'])
        notebook.add(moderators_tab, text="Модераторы")

        admins_tab = tk.Frame(notebook, bg=app_theme.colors['background'])
        notebook.add(admins_tab, text="Администраторы")

        self.setup_users_tab(users_tab)
        self.setup_moderators_tab(moderators_tab)
        self.setup_admins_tab(admins_tab)

        ttk.Button(
            main_frame,
            text="Закрыть",
            style='Secondary.TButton',
            command=users_window.destroy
        ).pack(pady=10)

    def setup_users_tab(self, parent):
        """Настройка вкладки с пользователями"""
        control_frame = tk.Frame(parent, bg=app_theme.colors['background'])
        control_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            control_frame,
            text="Обновить",
            style='TButton',
            command=lambda: self.load_users_data(self.users_tree)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="Управление доступом",
            style='TButton',
            command=self.manage_admin_access
        ).pack(side=tk.LEFT, padx=5)

        tree_frame = tk.Frame(parent, bg=app_theme.colors['background'])
        tree_frame.pack(expand=True, fill=tk.BOTH, pady=10)

        columns = ("id", "login", "user_type", "reg_date", "is_admin", "is_moderator")
        self.users_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode='browse',
            style='Custom.Treeview'
        )

        col_widths = [40, 200, 150, 120, 100, 100]
        for col, text, width in zip(columns,
                                    ["ID", "Логин", "Тип", "Дата регистрации", "Админ", "Модератор"],
                                    col_widths):
            self.users_tree.heading(col, text=text)
            self.users_tree.column(col, width=width, anchor='center')

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.users_tree.pack(expand=True, fill=tk.BOTH)

        self.load_users_data(self.users_tree)

    def setup_moderators_tab(self, parent):
        """Настройка вкладки с модераторами"""
        control_frame = tk.Frame(parent, bg=app_theme.colors['background'])
        control_frame.pack(fill=tk.X, pady=10)

        tree_frame = tk.Frame(parent, bg=app_theme.colors['background'])
        tree_frame.pack(expand=True, fill=tk.BOTH, pady=10)

        columns = ("id", "user_id", "login", "created_at")
        self.moderators_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode='browse',
            style='Custom.Treeview'
        )

        col_widths = [50, 60, 200, 120]
        for col, text, width in zip(columns,
                                    ["ID", "User ID", "Логин", "Дата назначения"],
                                    col_widths):
            self.moderators_tree.heading(col, text=text)
            self.moderators_tree.column(col, width=width, anchor='center')

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.moderators_tree.yview)
        self.moderators_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.moderators_tree.pack(expand=True, fill=tk.BOTH)

        ttk.Button(
            control_frame,
            text="Обновить",
            style='TButton',
            command=lambda: self.load_moderators_data(self.moderators_tree)
        ).pack(side=tk.LEFT, padx=5)

        self.load_moderators_data(self.moderators_tree)

    def setup_admins_tab(self, parent):
        """Настройка вкладки с администраторами"""
        control_frame = tk.Frame(parent, bg=app_theme.colors['background'])
        control_frame.pack(fill=tk.X, pady=10)

        tree_frame = tk.Frame(parent, bg=app_theme.colors['background'])
        tree_frame.pack(expand=True, fill=tk.BOTH, pady=10)

        columns = ("id", "user_id", "login", "position", "company", "created_at")
        self.admins_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode='browse',
            style='Custom.Treeview'
        )

        col_widths = [50, 60, 200, 200, 150, 120]
        for col, text, width in zip(columns,
                                    ["ID", "User ID", "Логин", "Должность", "Компания", "Назначен"],
                                    col_widths):
            self.admins_tree.heading(col, text=text)
            self.admins_tree.column(col, width=width, anchor='center')

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.admins_tree.yview)
        self.admins_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.admins_tree.pack(expand=True, fill=tk.BOTH)

        ttk.Button(
            control_frame,
            text="Обновить",
            style='TButton',
            command=lambda: self.load_admins_data(self.admins_tree)
        ).pack(side=tk.LEFT, padx=5)

        self.load_admins_data(self.admins_tree)

    def load_users_data(self, tree):
        """Загрузка данных пользователей в таблицу"""
        try:
            conn = create_connection()
            cursor = conn.cursor()

            for item in tree.get_children():
                tree.delete(item)

            cursor.execute("""
                SELECT u.id, u.login, u.user_type, 
                       TO_CHAR(u.registration_date, 'DD.MM.YYYY'),
                       CASE WHEN a.id IS NOT NULL THEN 'Да' ELSE 'Нет' END,
                       CASE WHEN m.id IS NOT NULL THEN 'Да' ELSE 'Нет' END
                FROM users u
                LEFT JOIN administrators a ON u.id = a.user_id
                LEFT JOIN moderators m ON u.id = m.user_id
                ORDER BY u.id
            """)

            for row in cursor.fetchall():
                user_type = "Обычный пользователь" if row[2] == 1 else "Модератор" if row[2] == 2 else "Администратор"
                tree.insert("", "end", values=(
                    row[0], row[1], user_type, row[3], row[4], row[5]
                ))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки пользователей: {e}")
        finally:
            if conn:
                conn.close()

    def load_moderators_data(self, tree):
        """Загрузка данных модераторов в таблицу"""
        try:
            conn = create_connection()
            cursor = conn.cursor()

            for item in tree.get_children():
                tree.delete(item)

            cursor.execute("""
                SELECT m.id, m.user_id, m.login
                FROM moderators m
            """)

            for row in cursor.fetchall():
                tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки модераторов: {e}")
        finally:
            if conn:
                conn.close()

    def load_admins_data(self, tree):
        """Загрузка данных администраторов с информацией о компаниях"""
        try:
            conn = create_connection()
            cursor = conn.cursor()

            for item in tree.get_children():
                tree.delete(item)

            # Получаем всех администраторов и их компании
            cursor.execute("""
                SELECT a.id, a.user_id, a.login, a.position, 
                       COALESCE(
                           (SELECT string_agg(c.name, ', ') 
                            FROM companies c 
                            WHERE a.user_id = ANY(c.employee_ids)),
                           'Системный администратор'
                       ),
                       TO_CHAR(a.created_at, 'DD.MM.YYYY')
                FROM administrators a
                ORDER BY a.created_at DESC
            """)

            for row in cursor.fetchall():
                tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки администраторов: {e}")
        finally:
            if conn:
                conn.close()

    def manage_admin_access(self):
        """Управление доступом пользователя: изменение типа пользователя, назначение администратором/модератором, изменение должности или снятие с должности"""
        selected = self.users_tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите пользователя из списка")
            return

        user_data = self.users_tree.item(selected)['values']
        user_id = user_data[0]
        login = user_data[1]
        current_user_type = user_data[2]
        is_admin = user_data[4] == 'Да'
        is_moderator = user_data[5] == 'Да'

        if user_id == self.user_id:
            messagebox.showwarning("Ошибка", "Вы не можете изменить собственный уровень доступа")
            return

        action_window = tk.Toplevel(self.root)
        action_window.title("Управление доступом")
        action_window.geometry("400x400")
        action_window.configure(bg=app_theme.colors['background'])
        app_theme.center_window(action_window)

        main_frame = tk.Frame(action_window, bg=app_theme.colors['background'], padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(
            main_frame,
            text=f"Управление доступом для {login}",
            style='Title.TLabel'
        ).pack(pady=10)

        ttk.Label(
            main_frame,
            text="Изменить тип пользователя:",
            style='TLabel'
        ).pack(anchor='w', pady=5)

        user_type_var = tk.StringVar(value=current_user_type)
        ttk.Radiobutton(
            main_frame,
            text="Обычный пользователь",
            value="Обычный пользователь",
            variable=user_type_var,
            style='TRadiobutton'
        ).pack(anchor='w', padx=20)
        ttk.Radiobutton(
            main_frame,
            text="Модератор",
            value="Модератор",
            variable=user_type_var,
            style='TRadiobutton'
        ).pack(anchor='w', padx=20)
        ttk.Radiobutton(
            main_frame,
            text="Администратор",
            value="Администратор",
            variable=user_type_var,
            style='TRadiobutton'
        ).pack(anchor='w', padx=20)

        # Фрейм для выбора компании
        company_frame = tk.Frame(main_frame, bg=app_theme.colors['background'])

        ttk.Label(
            company_frame,
            text="Компания:",
            style='TLabel'
        ).pack(anchor='w', pady=5)

        company_var = tk.StringVar()
        company_combobox = ttk.Combobox(
            company_frame,
            textvariable=company_var,
            state='readonly'
        )
        company_combobox.pack(fill=tk.X, pady=5)

        # Загружаем список компаний
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM companies ORDER BY name")
            companies = cursor.fetchall()
            company_combobox['values'] = [f"{name} (ID: {id})" for id, name in companies]
            if companies:
                company_combobox.current(0)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить список компаний: {e}")
        finally:
            if conn:
                conn.close()

        def toggle_admin_fields():
            new_type = user_type_var.get()
            if new_type == "Администратор":
                admin_frame.pack(pady=10)
                company_frame.pack(pady=10)
            else:
                admin_frame.pack_forget()
                company_frame.pack_forget()

        user_type_var.trace("w", lambda *args: toggle_admin_fields())

        admin_frame = tk.Frame(main_frame, bg=app_theme.colors['background'])
        if is_admin:
            admin_frame.pack(pady=10)
            company_frame.pack(pady=10)

        ttk.Label(
            admin_frame,
            text="Администраторские права:",
            style='TLabel'
        ).pack(anchor='w', pady=5)

        admin_action_var = tk.StringVar(value="keep")
        ttk.Radiobutton(
            admin_frame,
            text="Оставить права",
            value="keep",
            variable=admin_action_var,
            style='TRadiobutton'
        ).pack(anchor='w', padx=20)
        ttk.Radiobutton(
            admin_frame,
            text="Изменить должность",
            value="change",
            variable=admin_action_var,
            style='TRadiobutton'
        ).pack(anchor='w', padx=20)
        ttk.Radiobutton(
            admin_frame,
            text="Снять права",
            value="remove",
            variable=admin_action_var,
            style='TRadiobutton'
        ).pack(anchor='w', padx=20)

        def apply_changes():
            new_user_type = user_type_var.get()
            admin_action = admin_action_var.get()

            user_type_map = {
                "Обычный пользователь": 1,
                "Модератор": 2,
                "Администратор": 3
            }
            new_user_type_id = user_type_map[new_user_type]

            try:
                conn = create_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE users 
                    SET user_type = %s
                    WHERE id = %s
                """, (new_user_type_id, user_id))
                conn.commit()

                if new_user_type != "Модератор" and is_moderator:
                    cursor.execute("DELETE FROM moderators WHERE user_id = %s", (user_id,))
                    conn.commit()
                    messagebox.showinfo("Успех", "Пользователь удалён из модераторов")

                if new_user_type != "Администратор" and is_admin:
                    cursor.execute("DELETE FROM administrators WHERE user_id = %s", (user_id,))
                    conn.commit()
                    messagebox.showinfo("Успех", "Права администратора сняты")

                if new_user_type == "Модератор" and not is_moderator:
                    cursor.execute("""
                        INSERT INTO moderators (user_id, login)
                        VALUES (%s, %s)
                    """, (user_id, login))
                    conn.commit()
                    messagebox.showinfo("Успех", "Пользователь успешно назначен модератором")

                if new_user_type == "Администратор":
                    if is_admin:
                        if admin_action == "change":
                            new_position = simpledialog.askstring(
                                "Изменение должности",
                                f"Введите новую должность для {login}:",
                                parent=self.root
                            )
                            if not new_position:
                                return

                            # Обновляем должность
                            cursor.execute("""
                                       UPDATE administrators 
                                       SET position = %s
                                       WHERE user_id = %s
                                   """, (new_position, user_id))
                            # Если выбрана компания - обновляем привязку
                            selected_company = company_var.get()
                            if selected_company and not selected_company.startswith("Системный"):
                                company_id = int(selected_company.split("(ID: ")[1].rstrip(")"))

                                # Добавляем в выбранную компанию
                                cursor.execute("""
                                           UPDATE companies 
                                           SET employee_ids = array_append(employee_ids, %s)
                                           WHERE id = %s
                                       """, (user_id, company_id))

                        elif admin_action == "remove":
                            # Удаляем из administrators и из всех компаний
                            cursor.execute("DELETE FROM administrators WHERE user_id = %s", (user_id,))
                            cursor.execute("""
                                       UPDATE companies 
                                       SET employee_ids = array_remove(employee_ids, %s)
                                   """, (user_id,))

                    else:  # Назначение нового администратора
                        position = simpledialog.askstring(
                            "Назначение администратора",
                            f"Введите должность для {login}:",
                            parent=self.root
                        )
                        if not position:
                            return

                        # Добавляем в таблицу администраторов
                        cursor.execute("""
                                   INSERT INTO administrators (user_id, login, position)
                                   VALUES (%s, %s, %s)
                               """, (user_id, login, position))

                        # Если выбрана компания - добавляем в employee_ids
                        selected_company = company_var.get()
                        if selected_company and not selected_company.startswith("Системный"):
                            company_id = int(selected_company.split("(ID: ")[1].rstrip(")"))
                            cursor.execute("""
                                       UPDATE companies 
                                       SET employee_ids = array_append(COALESCE(employee_ids, '{}'::int[]), %s)
                                       WHERE id = %s
                                   """, (user_id, company_id))

                        conn.commit()
                        messagebox.showinfo("Успех", "Пользователь успешно назначен администратором")

                conn.commit()
                self.load_users_data(self.users_tree)
                self.load_moderators_data(self.moderators_tree)
                self.load_admins_data(self.admins_tree)
                action_window.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка управления доступом: {e}")
            finally:
                if conn:
                    conn.close()

        ttk.Button(
            main_frame,
            text="Применить",
            style='TButton',
            command=apply_changes
        ).pack(pady=10)

        ttk.Button(
            main_frame,
            text="Отмена",
            style='Secondary.TButton',
            command=action_window.destroy
        ).pack(pady=5)

    def show_reservations_management(self):
        """Окно управления бронированиями"""
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
            text="ID пользователя:",
            style='TLabel'
        ).pack(side=tk.LEFT, padx=5)

        self.user_id_entry = ttk.Entry(control_frame, width=10)
        self.user_id_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="Показать бронирования",
            style='TButton',
            command=self.load_user_reservations
        ).pack(side=tk.LEFT, padx=5)

        tree_frame = tk.Frame(main_frame, bg=app_theme.colors['background'])
        tree_frame.pack(expand=True, fill=tk.BOTH, pady=10)

        columns = ("id", "restaurant", "table", "date", "time", "guests", "status")
        self.reservations_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style='Custom.Treeview'
        )

        col_widths = [50, 200, 100, 100, 150, 70, 100]
        for col, text, width in zip(columns,
                                    ["ID", "Ресторан", "Стол", "Дата", "Время", "Гости", "Статус"],
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

    def load_user_reservations(self):
        """Загрузка бронирований выбранного пользователя"""
        user_id = self.user_id_entry.get()
        if not user_id.isdigit():
            messagebox.showwarning("Ошибка", "Введите корректный ID пользователя")
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()

            for item in self.reservations_tree.get_children():
                self.reservations_tree.delete(item)

            cursor.execute("""
                SELECT r.id, res.name, t.name,
                       TO_CHAR(r.start_time, 'DD.MM.YYYY'),
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
            """, (int(user_id),))

            for row in cursor.fetchall():
                self.reservations_tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки бронирований: {e}")
        finally:
            if conn:
                conn.close()

    def logout(self):
        """Выход из системы"""
        self.root.destroy()


def run_moderator_dashboard(username):
    root = tk.Tk()
    app_theme.init_fonts(root)
    ModeratorDashboard(root, username)
    root.mainloop()