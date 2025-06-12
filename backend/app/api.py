from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from login import login_user
from registration import register_user
from enum import Enum

app = FastAPI()

class UserType(str, Enum):
    user = "user"
    moderator = "moderator"

class LoginRequest(BaseModel):
    login: str
    password: str
    user_type: UserType

class RegisterRequest(BaseModel):
    login: str
    password: str
    user_type: UserType

@app.post("/api/login")
def login(request: LoginRequest):
    result = login_user(request.login, request.password, request.user_type.value)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=401, detail=result["message"])

@app.post("/api/register")
def register(request: RegisterRequest):
    result = register_user(request.login, request.password, request.user_type.value)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=401, detail=result["message"])