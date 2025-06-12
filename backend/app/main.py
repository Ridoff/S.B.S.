from fastapi import FastAPI, Request, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from auth.routes import router as auth_router
from routes import tables
from auth.db_models import Table, User, get_db
import os
import cv2
import numpy as np
from sqlalchemy.orm import Session

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
app.include_router(tables.router)

@app.post("/upload_hall/")
async def upload_hall(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        image_path = os.path.join("uploads", file.filename)
        os.makedirs("uploads", exist_ok=True)
        with open(image_path, "wb") as buffer:
            buffer.write(await file.read())

        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        _, thresh = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        tables_data = []
        for i, contour in enumerate(contours):
            (x, y), radius = cv2.minEnclosingCircle(contour)
            if radius > 10:
                tables_data.append({'id': i + 1, 'x': int(x) // 40, 'y': int(y) // 40, 'status': 'free'})

        for table in tables_data:
            new_table = Table(id=table['id'], x=table['x'], y=table['y'], status=table['status'])
            db.merge(new_table)
        db.commit()

        os.remove(image_path)
        return JSONResponse(
            status_code=200,
            content={"success": True, "tables": tables_data}
        )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": str(e)}
        )

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