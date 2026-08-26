import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest
from fastapi.testclient import TestClient
from app.db.database import Base, engine
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
        return {"Authorization": f"Bearer {token}"}
    return _create