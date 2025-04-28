from tkinter import Tk, Button, Label, Frame
from registration import run_registration
from login import run_login
from theme import app_theme
from connect import create_connection
from tkinter import messagebox
import tkinter as tk
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

def show_main_menu():
    root = Tk()
    root.title("Главное меню")

    app_theme.init_fonts(root)

    root.geometry(app_theme.sizes['window'])
    root.resizable(False, False)
    root.configure(bg=app_theme.colors['background'])

    main_frame = Frame(root,
                       bg=app_theme.colors['background'],
                       highlightbackground=app_theme.colors['primary'],
                       highlightthickness=2,
                       padx=20,
                       pady=20)
    main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    Label(main_frame,
          text="Главное меню",
          font=app_theme.fonts['title'],
          bg=app_theme.colors['background'],
          fg=app_theme.colors['primary'],
          pady=app_theme.sizes['padding_y']).pack()

    separator = Frame(main_frame,
                      height=2,
                      bg=app_theme.colors['primary'])
    separator.pack(fill=tk.X, pady=10)

    button_frame = Frame(main_frame,
                         bg=app_theme.colors['background'])
    button_frame.pack(pady=app_theme.sizes['button_padding'])

    Button(button_frame,
           text="Регистрация",
           command=lambda: [root.destroy(), run_registration()],
           width=app_theme.sizes['button_width'],
           height=app_theme.sizes['button_height'],
           bg=app_theme.colors['primary'],
           fg=app_theme.colors['text_light'],
           activebackground=app_theme.colors['primary_active'],
           activeforeground=app_theme.colors['text_light'],
           font=app_theme.fonts['button'],
           relief=tk.RAISED,
           bd=3,
           highlightbackground=app_theme.colors['highlight'],
           highlightthickness=1).pack(pady=app_theme.sizes['button_padding'])

    Button(button_frame,
           text="Вход",
           command=lambda: [root.destroy(), run_login()],
           width=app_theme.sizes['button_width'],
           height=app_theme.sizes['button_height'],
           bg=app_theme.colors['secondary'],
           fg=app_theme.colors['text_light'],
           activebackground=app_theme.colors['secondary_active'],
           activeforeground=app_theme.colors['text_light'],
           font=app_theme.fonts['button'],
           relief=tk.RAISED,
           bd=3,
           highlightbackground=app_theme.colors['highlight'],
           highlightthickness=1).pack(pady=app_theme.sizes['button_padding'])

    app_theme.center_window(root)

    root.mainloop()

def main():
    conn = create_connection()
    if not conn:
        messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
        return

    messagebox.showinfo("Успех", "Подключение к БД установлено")
    conn.close()

    show_main_menu()

if __name__ == "__main__":
    main()

