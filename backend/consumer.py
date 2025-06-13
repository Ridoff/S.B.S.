import os
import pika
from sqlalchemy.orm import Session
from app.auth.db_models import Notification, get_db, User
import smtplib
from email.mime.text import MIMEText
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "your-email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-app-password")

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

def callback(ch, method, properties, body):
    notification_id = int(body.decode())
    db = next(get_db())
    try:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return

        user = db.query(User).filter(User.id == notification.user_id).first()
        if not user or not user.email:
            notification.status = "failed"
            db.commit()
            return

        if send_email(user.email, "Seatly Notification", notification.message):
            notification.status = "sent"
        else:
            notification.status = "failed"
        db.commit()
        logger.info(f"Notification {notification_id} processed: {notification.status}")
    except Exception as e:
        logger.error(f"Error processing notification {notification_id}: {e}")
        notification.status = "failed" if notification else None
        db.commit()
    finally:
        db.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.URLParameters(os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672")))
    channel = connection.channel()
    channel.queue_declare(queue='notifications')
    channel.basic_consume(queue='notifications', on_message_callback=callback)
    logger.info("Starting RabbitMQ consumer...")
    channel.start_consuming()