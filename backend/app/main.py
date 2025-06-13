from fastapi import FastAPI, Request, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from auth.routes import router as auth_router
from routes import tables
from auth.db_models import Table, User, Booking, Notification, get_db
import os
import cv2
import numpy as np
import redis.asyncio as redis
import asyncio
import pika
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
import logging

app = FastAPI(
    title="Seatly API",
    description="API for Seatly Smart Restaurant Booking System",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://seatly.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(tables.router, prefix="/api", tags=["Tables"])

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "your-email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-app-password")

def get_rabbitmq_channel():
    connection = pika.BlockingConnection(pika.URLParameters(os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672")))
    return connection.channel()

def get_db():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

@app.post("/api/hall/upload")
async def upload_hall(restaurant_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        image_path = os.path.join("uploads", file.filename)
        os.makedirs("uploads", exist_ok=True)
        with open(image_path, "wb") as buffer:
            buffer.write(await file.read())

        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Failed to read image")
        _, thresh = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        tables_data = []
        for i, contour in enumerate(contours):
            (x, y), radius = cv2.minEnclosingCircle(contour)
            if radius > 10:
                table_x = int(x) // 40
                table_y = int(y) // 40
                table = Table(id=i + 1, restaurant_id=restaurant_id, x=table_x, y=table_y, status="free")
                db.merge(table)
                tables_data.append({"id": i + 1, "x": table_x, "y": table_y, "status": "free"})

        db.commit()
        os.remove(image_path)
        return JSONResponse(status_code=200, content={"success": True, "tables": tables_data})
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=400, content={"success": False, "message": str(e)})

@app.get("/api/tables/availability")
async def get_availability(restaurant_id: int, date: str, party_size: int, db: Session = Depends(get_db)):
    try:
        cache_key = f"availability:{restaurant_id}:{date}:{party_size}"
        cached = await redis_client.get(cache_key)
        if cached:
            return JSONResponse(status_code=200, content={"tables": eval(cached.decode())})

        available_tables = db.query(Table).filter(
            Table.restaurant_id == restaurant_id,
            Table.status == "free",
            ~db.query(Booking).filter(
                Booking.table_id == Table.id,
                Booking.booking_time == date
            ).exists()
        ).all()

        tables_data = [{"id": t.id, "x": t.x, "y": t.y, "status": t.status} for t in available_tables]
        await redis_client.setex(cache_key, 300, str(tables_data))
        return JSONResponse(status_code=200, content={"tables": tables_data})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/tables/reserve")
async def reserve_table(restaurant_id: int, table_id: int, date_time: str, party_size: int, db: Session = Depends(get_db)):
    try:
        table = db.query(Table).filter(Table.id == table_id, Table.restaurant_id == restaurant_id).first()
        if not table or table.status != "free":
            raise HTTPException(status_code=400, detail="Table not available")

        user = db.query(User).filter(User.id == 1).first()
        if not user or not user.email:
            raise HTTPException(status_code=400, detail="User not found")

        booking = Booking(table_id=table_id, user_id=1, booking_time=date_time, party_size=party_size)
        db.add(booking)
        table.status = "occupied"
        db.commit()

        notification = Notification(user_id=1, message=f"Booking {booking.id} confirmed for {date_time}", status="pending")
        db.add(notification)
        db.commit()

        channel = get_rabbitmq_channel()
        channel.basic_publish(exchange='', routing_key='notifications', body=str(notification.id).encode())
        channel.close()

        await redis_client.delete(f"availability:{restaurant_id}:{date_time.split('T')[0]}:*")
        return JSONResponse(status_code=200, content={"booking_id": booking.id, "message": "Reservation confirmed"})
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/notifications/send")
async def send_notification(user_id: int, message: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.email:
            raise HTTPException(status_code=400, detail="User not found")

        notification = Notification(user_id=user_id, message=message, status="pending")
        db.add(notification)
        db.commit()

        channel = get_rabbitmq_channel()
        channel.basic_publish(exchange='', routing_key='notifications', body=str(notification.id).encode())
        channel.close()

        return JSONResponse(status_code=200, content={"status": "queued", "message": message})
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)}
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to the Seatly API!"}

with next(get_db()) as db:
    Table.metadata.create_all(bind=db.bind)
    User.metadata.create_all(bind=db.bind)
    Booking.metadata.create_all(bind=db.bind)
    Notification.metadata.create_all(bind=db.bind)