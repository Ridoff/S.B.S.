from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from connect import create_connection
from datetime import datetime

router = APIRouter()

class UserProfile(BaseModel):
    id: int
    login: str
    registration_date: str

class Reservation(BaseModel):
    id: int
    restaurant: str
    table: str
    date: str
    time: str
    guests: int
    status: str

@router.get("/user/{user_id}", response_model=UserProfile)
def get_user_profile(user_id: int):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, login, registration_date FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        return {
            "id": row[0],
            "login": row[1],
            "registration_date": row[2].strftime('%d.%m.%Y') if row[2] else "не указана"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/reservations/{user_id}", response_model=List[Reservation])
def get_user_reservations(user_id: int):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.id, res.name, t.name,
                   r.start_time::date,
                   CONCAT(TO_CHAR(r.start_time, 'HH24:MI'), ' - ', TO_CHAR(r.end_time, 'HH24:MI')),
                   r.guests_count, r.status
            FROM reservations r
            JOIN restaurants res ON r.restaurant_id = res.id
            JOIN tables t ON r.table_id = t.id
            WHERE r.user_id = %s
            ORDER BY r.start_time DESC
        """, (user_id,))

        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "restaurant": row[1],
                "table": row[2],
                "date": row[3].strftime('%d.%m.%Y') if isinstance(row[3], datetime) else str(row[3]),
                "time": row[4],
                "guests": row[5],
                "status": row[6]
            }
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
