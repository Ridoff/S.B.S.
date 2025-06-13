from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.db_models import get_db, User
from .models import LoginRequest, LoginResponse, RegistrationRequest, RegistrationResponse
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "key_holder"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=LoginResponse)
def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_request.email).first()
    if not user or not pwd_context.verify(login_request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email})
    return {"message": "Login successful", "token": access_token}

@router.post("/register", response_model=RegistrationResponse)
def register(registration_request: RegistrationRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == registration_request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(registration_request.password)

    new_user = User(
        email=registration_request.email,
        hashed_password=hashed_password,
        name=registration_request.name,
        role=registration_request.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": new_user.email})
    return {"message": "Registration successful", "user_id": new_user.id, "token": access_token}