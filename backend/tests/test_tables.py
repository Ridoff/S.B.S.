import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes.tables import router as tables_router
from app.auth.db_models import User, Table
import os

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_get_tables_empty(client, mock_token, db_session):
    response = client.get("/tables", headers={"Authorization": f"Bearer {mock_token}"})
    assert response.status_code == 200
    assert response.json() == []

def test_get_tables_with_data(client, mock_token, db_session):
    table = Table(id=1, x=10, y=20, status="free")
    db_session.add(table)
    db_session.commit()
    response = client.get("/tables", headers={"Authorization": f"Bearer {mock_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == 1
    assert response.json()[0]["status"] == "free"

def test_get_tables_unauthorized(client):
    response = client.get("/tables")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_reserve_table_success(client, mock_token, db_session):
    table = Table(id=1, x=10, y=20, status="free")
    db_session.add(table)
    db_session.commit()
    response = client.post("/reserve", json={"table_id": 1}, headers={"Authorization": f"Bearer {mock_token}"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert db_session.query(Table).filter(Table.id == 1).first().status == "occupied"

def test_reserve_table_occupied(client, mock_token, db_session):
    table = Table(id=1, x=10, y=20, status="occupied")
    db_session.add(table)
    db_session.commit()
    response = client.post("/reserve", json={"table_id": 1}, headers={"Authorization": f"Bearer {mock_token}"})
    assert response.status_code == 200
    assert response.json()["success"] is False
    assert response.json()["message"] == "Table is occupied or not found"

def test_reserve_table_not_found(client, mock_token, db_session):
    response = client.post("/reserve", json={"table_id": 999}, headers={"Authorization": f"Bearer {mock_token}"})
    assert response.status_code == 200
    assert response.json()["success"] is False
    assert response.json()["message"] == "Table is occupied or not found"

def test_upload_hall_moderator(client, mock_token, db_session):
    user = User(email="moderator@example.com", role="moderator")
    db_session.add(user)
    db_session.commit()
    with open("test_image.jpg", "wb") as f:
        f.write(b"test_image_data")
    with open("test_image.jpg", "rb") as image_file:
        response = client.post(
            "/upload_hall/",
            files={"file": ("test_image.jpg", image_file, "image/jpeg")},
            headers={"Authorization": f"Bearer {mock_token}"}
        )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert len(response.json()["tables"]) >= 0

def test_upload_hall_non_moderator(client, mock_token, db_session):
    user = User(email="user@example.com", role="user")
    db_session.add(user)
    db_session.commit()
    with open("test_image.jpg", "wb") as f:
        f.write(b"test_image_data")
    with open("test_image.jpg", "rb") as image_file:
        response = client.post(
            "/upload_hall/",
            files={"file": ("test_image.jpg", image_file, "image/jpeg")},
            headers={"Authorization": f"Bearer {mock_token}"}
        )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only moderators can upload hall layouts"

def test_upload_hall_invalid_image(client, mock_token, db_session):
    user = User(email="moderator@example.com", role="moderator")
    db_session.add(user)
    db_session.commit()
    with open("test_invalid.jpg", "wb") as f:
        f.write(b"not_an_image")
    with open("test_invalid.jpg", "rb") as image_file:
        response = client.post(
            "/upload_hall/",
            files={"file": ("test_invalid.jpg", image_file, "image/jpeg")},
            headers={"Authorization": f"Bearer {mock_token}"}
        )
    assert response.status_code == 200
    assert response.json()["success"] is False
    assert "Failed to read the image" in response.json()["message"]

def test_upload_hall_missing_file(client, mock_token, db_session):
    user = User(email="moderator@example.com", role="moderator")
    db_session.add(user)
    db_session.commit()
    response = client.post(
        "/upload_hall/",
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    assert response.status_code == 422