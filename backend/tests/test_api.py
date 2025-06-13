import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api import UserType
from app.login import login_user
from app.registration import register_user

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def mock_login_user():
    return lambda login, password, user_type: {"success": True, "token": "fake-token"} if login == "test" and password == "test" else {"success": False, "message": "Invalid credentials"}

@pytest.fixture
def mock_register_user():
    return lambda login, password, user_type: {"success": True, "message": "User registered"} if login and password else {"success": False, "message": "Registration failed"}

def test_login_success(client, monkeypatch, mock_login_user):
    monkeypatch.setattr("app.api.login_user", mock_login_user)
    response = client.post("/api/login", json={"login": "test", "password": "test", "user_type": "user"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "token" in response.json()

def test_login_failure(client, monkeypatch, mock_login_user):
    monkeypatch.setattr("app.api.login_user", mock_login_user)
    response = client.post("/api/login", json={"login": "wrong", "password": "wrong", "user_type": "user"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_invalid_user_type(client, monkeypatch, mock_login_user):
    monkeypatch.setattr("app.api.login_user", mock_login_user)
    response = client.post("/api/login", json={"login": "test", "password": "test", "user_type": "invalid"})
    assert response.status_code == 422

def test_register_success(client, monkeypatch, mock_register_user):
    monkeypatch.setattr("app.api.register_user", mock_register_user)
    response = client.post("/api/register", json={"login": "newuser", "password": "pass123", "user_type": "user"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "User registered"

def test_register_failure(client, monkeypatch, mock_register_user):
    monkeypatch.setattr("app.api.register_user", mock_register_user)
    response = client.post("/api/register", json={"login": "", "password": "pass123", "user_type": "user"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Registration failed"

def test_register_invalid_user_type(client, monkeypatch, mock_register_user):
    monkeypatch.setattr("app.api.register_user", mock_register_user)
    response = client.post("/api/register", json={"login": "newuser", "password": "pass123", "user_type": "invalid"})
    assert response.status_code == 422