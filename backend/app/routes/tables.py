from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from auth.db_models import Table, get_db, User
from fastapi.security import OAuth2PasswordBearer
from auth.routes import SECRET_KEY, ALGORITHM
import jwt
import os
import cv2
import numpy as np
from unittest.mock import patch

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/tables")
def get_tables(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    tables = db.query(Table).all()
    return [{"id": t.id, "x": t.x, "y": t.y, "status": t.status} for t in tables]

@router.post("/reserve")
def reserve_table(table_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table or table.status == "occupied":
        return {"success": False, "message": "Table is occupied or not found"}
    table.status = "occupied"
    db.commit()
    return {"success": True, "message": "Table reserved successfully"}

@router.post("/upload_hall/")
async def upload_hall(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.email == current_user).first()
    if user.role != "moderator":
        raise HTTPException(status_code=403, detail="Only moderators can upload hall layouts")

    try:
        image_path = os.path.join("uploads", file.filename)
        os.makedirs("uploads", exist_ok=True)
        with open(image_path, "wb") as buffer:
            buffer.write(await file.read())

        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Failed to read the image")
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
        return {"success": True, "tables": tables_data}
    except Exception as e:
        return {"success": False, "message": str(e)}
    
@patch('app.tables.jwt.decode')
def test_get_tables_with_mock_token(mock_decode, client):
    mock_decode.return_value = {"sub": "user@example.com"}
    response = client.get("/tables", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200