import sys
import os
from connect import create_connection
from datetime import datetime

def get_user_id(username):
    """Получает ID текущего пользователя по логину"""
    try:
        conn = create_connection()
        if not conn:
            raise RuntimeError("Не удалось подключиться к базе данных")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE login = %s", (username,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Ошибка получения ID пользователя: {e}")
        return None
    finally:
        if conn:
            conn.close()

def show_profile(username, user_id):
    """Показывает профиль текущего пользователя"""
    try:
        conn = create_connection()
        if not conn:
            raise RuntimeError("Не удалось подключиться к базе данных")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.login, u.user_type, u.registration_date, 
                   a.position, a.created_at
            FROM users u
            LEFT JOIN administrators a ON u.id = a.user_id
            WHERE u.id = %s
        """, (user_id,))
        user_data = cursor.fetchone()

        if user_data:
            print(f"\nПрофиль пользователя: {user_data[0]}")
            user_type = "Обычный пользователь" if user_data[1] == 1 else "Модератор" if user_data[1] == 2 else "Администратор"
            reg_date = user_data[2].strftime('%d.%m.%Y') if user_data[2] else "не указана"
            print(f"Тип пользователя: {user_type}")
            print(f"Дата регистрации: {reg_date}")
            if user_data[3]:
                print(f"Должность: {user_data[3]}")
                print(f"Администратор с: {user_data[4].strftime('%d.%m.%Y') if user_data[4] else 'не указана'}")
        else:
            print("Данные пользователя не найдены.")
    except Exception as e:
        print(f"Ошибка загрузки профиля: {e}")
    finally:
        if conn:
            conn.close()

def create_company():
    """Создание компании"""
    try:
        conn = create_connection()
        if not conn:
            raise RuntimeError("Не удалось подключиться к базе данных")
        company_name = input("Введите название компании: ").strip()

        if not company_name:
            print("Ошибка: Введите название компании.")
            return

        cursor = conn.cursor()
        cursor.execute("INSERT INTO companies (name) VALUES (%s)", (company_name,))
        conn.commit()
        print("Компания успешно создана.")
    except Exception as e:
        print(f"Ошибка при создании компании: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

def create_restaurant():
    """Создание ресторана"""
    try:
        conn = create_connection()
        if not conn:
            raise RuntimeError("Не удалось подключиться к базе данных")
        company_id = input("Введите ID компании: ").strip()
        restaurant_name = input("Введите название ресторана: ").strip()
        restaurant_phone = input("Введите телефон ресторана: ").strip()
        restaurant_desc = input("Введите описание ресторана: ").strip()

        if not company_id or not restaurant_name:
            print("Ошибка: Заполните все обязательные поля.")
            return

        if not company_id.isdigit():
            print("Ошибка: ID компании должен быть числом.")
            return

        company_id = int(company_id)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM companies WHERE id = %s", (company_id,))
        if not cursor.fetchone():
            print("Ошибка: Компания с таким ID не существует.")
            return

        cursor.execute("""
            INSERT INTO restaurants (company_id, name, phone, description)
            VALUES (%s, %s, %s, %s)
        """, (company_id, restaurant_name, restaurant_phone, restaurant_desc))
        conn.commit()
        print("Ресторан успешно создан.")
    except Exception as e:
        print(f"Ошибка при создании ресторана: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

def create_hall():
    """Создание зала"""
    try:
        conn = create_connection()
        if not conn:
            raise RuntimeError("Не удалось подключиться к базе данных")
        restaurant_id = input("Введите ID ресторана: ").strip()
        hall_name = input("Введите название зала: ").strip()
        hall_capacity = input("Введите максимальную вместимость: ").strip()

        if not restaurant_id or not hall_name or not hall_capacity:
            print("Ошибка: Заполните все обязательные поля.")
            return

        if not restaurant_id.isdigit() or not hall_capacity.isdigit():
            print("Ошибка: ID ресторана и вместимость должны быть числами.")
            return

        restaurant_id = int(restaurant_id)
        hall_capacity = int(hall_capacity)
        if hall_capacity <= 0:
            print("Ошибка: Вместимость должна быть положительным числом.")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT id FROM restaurants WHERE id = %s", (restaurant_id,))
        if not cursor.fetchone():
            print("Ошибка: Ресторан с таким ID не существует.")
            return

        cursor.execute("""
            INSERT INTO halls (restaurant_id, name, max_capacity)
            VALUES (%s, %s, %s)
        """, (restaurant_id, hall_name, hall_capacity))
        conn.commit()
        print("Зал успешно создан.")
    except Exception as e:
        print(f"Ошибка при создании зала: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

def show_manage_reservations(user_id):
    """Управление бронированиями"""
    try:
        conn = create_connection()
        if not conn:
            raise RuntimeError("Не удалось подключиться к базе данных")
        restaurant_id = input("Введите ID ресторана: ").strip()

        if not restaurant_id.isdigit():
            print("Ошибка: Введите корректный ID ресторана.")
            return

        restaurant_id = int(restaurant_id)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT e.id
            FROM employees e
            WHERE e.user_id = %s AND e.restaurant_id = %s
        """, (user_id, restaurant_id))
        if not cursor.fetchone():
            print("Ошибка: Вы не являетесь сотрудником этого ресторана.")
            return

        cursor.execute("""
            SELECT r.id, res.name, t.name,
                   TO_CHAR(r.start_time, 'DD.MM.YYYY'),
                   CONCAT(TO_CHAR(r.start_time, 'HH24:MI'), ' - ', TO_CHAR(r.end_time, 'HH24:MI')),
                   r.guests_count, r.status, r.user_id
            FROM reservations r
            JOIN restaurants res ON r.restaurant_id = res.id
            JOIN tables t ON r.table_id = t.id
            WHERE r.restaurant_id = %s
            ORDER BY r.start_time DESC
        """, (restaurant_id,))
        reservations = cursor.fetchall()

        print("\nБронирования:")
        print("ID | Ресторан | Стол | Дата | Время | Гости | Статус | User ID")
        print("-" * 90)
        for row in reservations:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]}")

        cancel_reservation(conn, reservations)

    except Exception as e:
        print(f"Ошибка загрузки бронирований: {e}")
    finally:
        if conn:
            conn.close()

def cancel_reservation(conn, reservations):
    """Отмена выбранного бронирования"""
    try:
        reservation_id = input("Введите ID бронирования для отмены (или 'q' для выхода): ").strip()
        if reservation_id.lower() == 'q':
            return

        if not reservation_id.isdigit():
            print("Ошибка: ID должен быть числом.")
            return

        reservation_id = int(reservation_id)
        reservation = next((r for r in reservations if r[0] == reservation_id), None)
        if not reservation:
            print("Бронирование с таким ID не найдено.")
            return

        status = reservation[6]
        if status.lower() == "отменено":
            print("Ошибка: Это бронирование уже отменено.")
            return

        confirm = input("Вы уверены, что хотите отменить это бронирование? (да/нет): ").strip().lower()
        if confirm != 'да':
            return

        cursor = conn.cursor()
        cursor.execute("UPDATE reservations SET status = 'отменено' WHERE id = %s", (reservation_id,))
        conn.commit()
        print("Бронирование успешно отменено.")
    except Exception as e:
        print(f"Ошибка при отмене бронирования: {e}")
        conn.rollback()

def main(username):
    """Основной цикл программы"""
    user_id = get_user_id(username)
    if not user_id:
        print("Не удалось определить пользователя. Завершение работы.")
        return

    while True:
        print("\nМеню администратора:")
        print("1. Мой профиль")
        print("2. Создать компанию")
        print("3. Создать ресторан")
        print("4. Создать зал")
        print("5. Управление бронированиями")
        print("6. Выйти")
        choice = input("Выберите действие (1-6): ").strip()

        if choice == "1":
            show_profile(username, user_id)
        elif choice == "2":
            create_company()
        elif choice == "3":
            create_restaurant()
        elif choice == "4":
            create_hall()
        elif choice == "5":
            show_manage_reservations(user_id)
        elif choice == "6":
            print("Выход из системы.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python admin.py <username>")
        sys.exit(1)
    username = sys.argv[1]
    main(username)