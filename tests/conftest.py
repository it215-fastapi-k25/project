import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest
from fastapi.testclient import TestClient
from app.db.database import Base, engine, SessionLocal
from app import models
from app.main import app


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    from app.core.limiter import limiter
    limiter.reset()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def register_and_login(client):
    def _create(email: str, password: str = "12345678", full_name: str = "Test User"):
        client.post("/auth/register", json={"email": email, "full_name": full_name, "password": password})
        r = client.post("/auth/login", data={"username": email, "password": password})
        token = r.json()["access_token"]
        refresh_token = r.json()["refresh_token"]
        headers = {"Authorization": f"Bearer {token}"}
        me = client.get("/users/me", headers=headers).json()
        return {"headers": headers, "user_id": me["id"], "email": email, "token": token, "refresh_token": refresh_token}
    return _create


@pytest.fixture
def make_admin():
    def _make_admin(email: str):
        from app.models.user import User, UserRole
        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        user.role = UserRole.ADMIN
        db.commit()
        db.close()
    return _make_admin


@pytest.fixture
def make_inactive():
    def _make_inactive(email: str):
        from app.models.user import User
        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        user.is_active = False
        db.commit()
        db.close()
    return _make_inactive


@pytest.fixture
def create_project(client):
    def _create(headers, name="Test Project", description=None):
        r = client.post("/research-projects", json={"name": name, "description": description}, headers=headers)
        return r.json()["id"]
    return _create