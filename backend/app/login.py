from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from connect import create_connection
import hashlib

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str
    user_type: int = 1

@router.post("/login")
def login_user(data: LoginRequest):
    username = data.username
    password = data.password
    user_type = data.user_type

    if not username or not password:
        raise HTTPException(status_code=400, detail="Все поля обязательны")

    conn = None
    try:
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Нет подключения к БД")

        cursor = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        if user_type == 1:
            cursor.execute(
                "SELECT id FROM users WHERE login = %s AND password = %s AND user_type = %s",
                (username, hashed_pw, user_type))
            user = cursor.fetchone()
            if user:
                return {"message": "Успешный вход как Клиент", "user_id": user[0]}
            else:
                raise HTTPException(status_code=401, detail="Неверный логин или пароль")

        elif user_type == 2:
            cursor.execute("SELECT id FROM administrators WHERE login = %s", (username,))
            admin = cursor.fetchone()
            if admin:
                return {"message": "Успешный вход как Админ", "user_id": admin[0]}
            else:
                cursor.execute(
                    "SELECT id FROM users WHERE login = %s AND password = %s AND user_type = %s",
                    (username, hashed_pw, user_type))
                user = cursor.fetchone()
                if user:
                    raise HTTPException(status_code=403, detail="Аккаунт еще не подтвержден")
                else:
                    raise HTTPException(status_code=401, detail="Неверный логин или пароль")

        elif user_type == 3:
            cursor.execute("SELECT id FROM moderators WHERE login = %s", (username,))
            mod = cursor.fetchone()
            if mod:
                return {"message": "Успешный вход как Модератор", "user_id": mod[0]}
            else:
                cursor.execute(
                    "SELECT id FROM users WHERE login = %s AND password = %s AND user_type = %s",
                    (username, hashed_pw, user_type))
                user = cursor.fetchone()
                if user:
                    raise HTTPException(status_code=403, detail="Аккаунт еще не подтвержден")
                else:
                    raise HTTPException(status_code=401, detail="Неверный логин или пароль")

        else:
            raise HTTPException(status_code=400, detail="Неверный тип пользователя")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка входа: {str(e)}")
    finally:
        if conn:
            conn.close()
