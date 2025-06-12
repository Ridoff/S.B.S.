from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str
    token: str

class RegistrationRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Optional[str] = "user"

class RegistrationResponse(BaseModel):
    message: str
    user_id: Optional[int] = None
    token: Optional[str] = None
    
