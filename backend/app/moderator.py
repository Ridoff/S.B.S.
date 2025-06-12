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
                   a.position, a.created_at, c.name
            FROM users u
            LEFT JOIN administrators a ON u.id = a.user_id
            LEFT JOIN companies c ON a.company_id = c.id
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
                print(f"Компания: {user_data[5] or 'Системный администратор'}")
                print(f"Администратор с: {user_data[4].strftime('%d.%m.%Y') if user_data[4] else 'не указана'}")
        else:
            print("Данные пользователя не найдены.")
    except Exception as e:
        print(f"Ошибка загрузки профиля: {e}")
    finally:
        if conn:
            conn.close()

def show_users_management():
    """Управление пользователями и администраторами"""
    try:
        conn = create_connection()
        if not conn:
            raise RuntimeError("Не удалось подключиться к базе данных")
        cursor = conn.cursor()

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
        users = cursor.fetchall()

        print("\nСписок пользователей:")
        print("ID | Логин | Тип | Дата регистрации | Админ | Модератор")
        print("-" * 60)
        for row in users:
            user_type = "Обычный пользователь" if row[2] == 1 else "Модератор" if row[2] == 2 else "Администратор"
            print(f"{row[0]} | {row[1]} | {user_type} | {row[3]} | {row[4]} | {row[5]}")

        manage_user(conn, users)

    except Exception as e:
        print(f"Ошибка загрузки пользователей: {e}")
    finally:
        if conn:
            conn.close()

def manage_user(conn, users):
    """Управление доступом для выбранного пользователя"""
    user_id = input("Введите ID пользователя для управления (или 'q' для выхода): ")
    if user_id.lower() == 'q':
        return

    try:
        user_id = int(user_id)
        user = next((u for u in users if u[0] == user_id), None)
        if not user:
            print("Пользователь с таким ID не найден.")
            return

        login = user[1]
        current_type = "Обычный пользователь" if user[2] == 1 else "Модератор" if user[2] == 2 else "Администратор"
        is_admin = user[4] == 'Да'
        is_moderator = user[5] == 'Да'

        print(f"\nУправление доступом для {login}")
        new_type = input(f"Новый тип (Обычный пользователь/Модератор/Администратор, текущий: {current_type}): ").strip()
        user_type_map = {
            "Обычный пользователь": 1,
            "Модератор": 2,
            "Администратор": 3
        }
        if new_type not in user_type_map:
            print("Неверный тип пользователя.")
            return

        cursor = conn.cursor()
        cursor.execute("UPDATE users SET user_type = %s WHERE id = %s", (user_type_map[new_type], user_id))
        conn.commit()

        if new_type != "Модератор" and is_moderator:
            cursor.execute("DELETE FROM moderators WHERE user_id = %s", (user_id,))
            conn.commit()
            print("Пользователь удалён из модераторов.")

        if new_type != "Администратор" and is_admin:
            cursor.execute("DELETE FROM administrators WHERE user_id = %s", (user_id,))
            conn.commit()
            print("Права администратора сняты.")

        if new_type == "Модератор" and not is_moderator:
            cursor.execute("INSERT INTO moderators (user_id, login) VALUES (%s, %s)", (user_id, login))
            conn.commit()
            print("Пользователь назначен модератором.")

        if new_type == "Администратор":
            if is_admin:
                action = input("Действие (keep/change/remove): ").strip().lower()
                if action == "change":
                    position = input(f"Введите новую должность для {login}: ")
                    cursor.execute("UPDATE administrators SET position = %s WHERE user_id = %s", (position, user_id))
                    conn.commit()
                    print("Должность обновлена.")
                elif action == "remove":
                    cursor.execute("DELETE FROM administrators WHERE user_id = %s", (user_id,))
                    conn.commit()
                    print("Права администратора сняты.")
            else:
                position = input(f"Введите должность для {login}: ")
                cursor.execute("INSERT INTO administrators (user_id, login, position) VALUES (%s, %s, %s)", (user_id, login, position))
                conn.commit()
                print("Пользователь назначен администратором.")

        conn.commit()
        print("Изменения применены.")

    except ValueError:
        print("ID должен быть числом.")
    except Exception as e:
        print(f"Ошибка управления доступом: {e}")
        conn.rollback()

def show_reservations_management():
    """Управление бронированиями"""
    user_id = input("Введите ID пользователя для просмотра бронирований: ")
    if not user_id.isdigit():
        print("ID должен быть числом.")
        return

    try:
        conn = create_connection()
        if not conn:
            raise RuntimeError("Не удалось подключиться к базе данных")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.id, res.name, t.name,
                   TO_CHAR(r.start_time, 'DD.MM.YYYY'),
                   CONCAT(TO_CHAR(r.start_time, 'HH24:MI'), ' - ', TO_CHAR(r.end_time, 'HH24:MI')),
                   r.guests_count, r.status
            FROM reservations r
            JOIN restaurants res ON r.restaurant_id = res.id
            JOIN tables t ON r.table_id = t.id
            WHERE r.user_id = %s
            ORDER BY r.start_time DESC
        """, (int(user_id),))
        reservations = cursor.fetchall()

        print("\nБронирования:")
        print("ID | Ресторан | Стол | Дата | Время | Гости | Статус")
        print("-" * 80)
        for row in reservations:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]}")

    except Exception as e:
        print(f"Ошибка загрузки бронирований: {e}")
    finally:
        if conn:
            conn.close()

def main(username):
    """Основной цикл программы"""
    user_id = get_user_id(username)
    if not user_id:
        print("Не удалось определить пользователя. Завершение работы.")
        return

    while True:
        print("\nМеню модератора:")
        print("1. Мой профиль")
        print("2. Управление пользователями")
        print("3. Управление бронированиями")
        print("4. Выйти")
        choice = input("Выберите действие (1-4): ").strip()

        if choice == "1":
            show_profile(username, user_id)
        elif choice == "2":
            show_users_management()
        elif choice == "3":
            show_reservations_management()
        elif choice == "4":
            print("Выход из системы.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python moderator.py <username>")
        sys.exit(1)
    username = sys.argv[1]
    main(username)