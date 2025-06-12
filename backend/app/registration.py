from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime
from connect import create_connection
import hashlib

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    user_type: int = 1

@router.post("/register")
def register_user(data: RegisterRequest):
    login = data.username
    email = data.email
    password = data.password
    user_type = data.user_type

    if not login or not email or not password:
        raise HTTPException(status_code=400, detail="Все поля обязательны")

    try:
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Нет подключения к БД")

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE login = %s", (login,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Логин уже занят")

        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        cursor.execute("""
            INSERT INTO users (user_type, login, password, email, registration_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_type, login, hashed_pw, email, datetime.now()))
        conn.commit()

        return {"message": "Пользователь зарегистрирован успешно"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if conn:
            conn.close()
