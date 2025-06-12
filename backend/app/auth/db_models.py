from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from connect import create_connection

Base = declarative_base()

class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, index=True)
    x = Column(Integer)
    y = Column(Integer)
    status = Column(String(20), default="free")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)
    role = Column(String, default="user")

conn = create_connection()
if conn:
    engine = conn
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    raise RuntimeError("Не удалось подключиться к базе данных")

def get_db():
    db = SessionLocal()
    try:
      yield db
    finally:
        db.close()