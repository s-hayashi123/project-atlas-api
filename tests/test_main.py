"""Minimal tests for the API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_user():
    response = client.post(
        "/users",
        json={"name": "Taro Yamada", "email": "taro@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Taro Yamada"
    assert data["email"] == "taro@example.com"
    assert "id" in data


def test_create_team():
    response = client.post(
        "/teams",
        json={"name": "Backend Team", "description": "Backend developers"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Backend Team"
