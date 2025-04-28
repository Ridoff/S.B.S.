from tkinter import font as tkfont, ttk
import tkinter as tk
import os
import ctypes
import platform


class GothicTheme:
    def __init__(self):
        self.colors = {
            'primary': '#8B0000',  # Темно-красный для кнопки "Регистрация" и текста
            'primary_active': '#660000',
            'secondary': '#4A4A4A',  # Темно-серый для кнопки "Вход"
            'secondary_active': '#3A3A3A',
            'background': '#1A1A1A',  # Почти черный фон
            'text': '#E0E0E0',  # Светло-серый текст
            'text_light': '#FFFFFF',  # Белый текст для кнопок
            'footer': '#8B0000',  # Темно-красный для футера
            'highlight': '#A52A2A'  # Кирпичный
        }

        self.fonts = {}
        self.sizes = {
            'window': '600x550',
            'button_width': 25,
            'button_height': 2,
            'padding_y': 25,
            'button_padding': 12,
            'border_width': 3
        }

    def init_fonts(self, root):
        try:
            font_path = os.path.abspath("NotoSansGothic-Regular.ttf")

            if not os.path.exists(font_path):
                self._use_fallback_fonts()
                self.configure_styles(root)
                return

            # Временно используем Arial, чтобы избежать проблем с установкой шрифта
            self._use_fallback_fonts()
            self.configure_styles(root)
            return

            # Код для установки шрифта (для будущего использования)
            if platform.system() == "Windows":
                self._install_font_windows(font_path)

            available_fonts = list(tkfont.families())
            font_name = "Noto Sans Gothic"

            if font_name not in available_fonts:
                self._use_fallback_fonts()
            else:
                self.fonts = {
                    'title': (font_name, 24, "bold"),
                    'button': (font_name, 16),
                    'default': (font_name, 14),
                    'footer': (font_name, 12)
                }

        except Exception as e:
            print(f"Ошибка при загрузке шрифта: {e}")
            print("Используем Arial")
            self._use_fallback_fonts()

        self.configure_styles(root)

    def _install_font_windows(self, font_path):
        """Установка шрифта в Windows"""
        try:
            FR_PRIVATE = 0x10
            if not ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0):
                raise RuntimeError("Ошибка AddFontResourceExW")
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x001D, 0, 0)
        except Exception as e:
            print(f"Ошибка установки шрифта в Windows: {e}")
            raise

    def _use_fallback_fonts(self):
        """Использование резервных шрифтов"""
        self.fonts = {
            'title': ("Arial", 24, "bold"),
            'button': ("Arial", 16),
            'default': ("Arial", 14),
            'footer': ("Arial", 12)
        }

    def configure_styles(self, root):
        """Конфигурация стилей виджетов"""
        style = ttk.Style(root)
        style.theme_use('clam')

        style.configure('.',
                        background=self.colors['background'],
                        foreground=self.colors['text'],
                        font=self.fonts['default'])

        # Стиль для кнопки "Зарегистрироваться"
        style.configure('TButton',
                        font=self.fonts['button'],
                        borderwidth=self.sizes['border_width'],
                        relief='raised',
                        padding=10,
                        foreground=self.colors['text_light'],
                        background=self.colors['primary'])

        style.map('TButton',
                  foreground=[('active', self.colors['text_light'])],
                  background=[('active', self.colors['primary_active']),
                              ('!active', self.colors['primary'])],
                  highlightcolor=[('active', self.colors['highlight'])])

        # В методе configure_styles() класса GothicTheme добавьте:
        style.configure('Custom.Treeview',
                        background=app_theme.colors['background'],
                        foreground=app_theme.colors['text'],
                        fieldbackground=app_theme.colors['background'],
                        rowheight=25,
                        font=self.fonts['default'])

        style.configure('Custom.Treeview.Heading',
                        background=app_theme.colors['primary'],
                        foreground=app_theme.colors['text_light'],
                        font=app_theme.fonts['default'])

        # Стиль для кнопки "Назад"
        style.configure('Secondary.TButton',
                        font=self.fonts['button'],
                        borderwidth=self.sizes['border_width'],
                        relief='raised',
                        padding=10,
                        foreground=self.colors['text_light'],
                        background=self.colors['secondary'])

        style.map('Secondary.TButton',
                  foreground=[('active', self.colors['text_light'])],
                  background=[('active', self.colors['secondary_active']),
                              ('!active', self.colors['secondary'])],
                  highlightcolor=[('active', self.colors['highlight'])])

        # Стиль для радиокнопок
        style.configure('Role.TRadiobutton',
                        font=self.fonts['default'],
                        foreground=self.colors['text_light'],
                        background=self.colors['background'],
                        padding=5)

        style.map('Role.TRadiobutton',
                  foreground=[('selected', self.colors['primary']),
                             ('!selected', self.colors['text_light'])],
                  background=[('selected', self.colors['background']),
                              ('!selected', self.colors['background'])],
                  indicatorcolor=[('selected', self.colors['primary']),
                                  ('!selected', self.colors['text_light'])])

        style.configure('TLabel',
                        font=self.fonts['default'],
                        background=self.colors['background'],
                        foreground=self.colors['text'])

        style.configure('Title.TLabel',
                        font=self.fonts['title'],
                        foreground=self.colors['primary'])

        style.configure('Footer.TLabel',
                        font=self.fonts['footer'],
                        foreground=self.colors['footer'],
                        background=self.colors['background'])


    def center_window(self, window):
        """Центрирование окна на экране"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'+{x}+{y}')


app_theme = GothicTheme()