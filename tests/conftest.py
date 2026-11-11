
import os

# Force a separate test database before importing the application
os.environ["DATABASE_URL"] = "sqlite://"

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.main import app
from app.db.base import Base
from app.dependencies import get_db
from app.core.security import hash_password


# Dedicated in-memory test database
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


# Database fixture
@pytest.fixture
def db_session():

    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


# FastAPI TestClient fixture
@pytest.fixture
def client(db_session):

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# Normal user fixture
@pytest.fixture
def test_user(db_session):

    user = models.User(
        name="Test User",
        email="test@example.com",
        age=24,
        password_hash=hash_password("TestPassword123"),
        role="user",
        is_active=True
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


# Admin user fixture
@pytest.fixture
def test_admin(db_session):

    admin = models.User(
        name="Admin User",
        email="admin@example.com",
        age=30,
        password_hash=hash_password("AdminPassword123"),
        role="admin",
        is_active=True
    )

    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    return admin


# Normal user authentication fixture
@pytest.fixture
def auth_headers(client, test_user):

    response = client.post(
        "/auth/login",
        data={
            "username": test_user.email,
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


# Admin authentication fixture
@pytest.fixture
def admin_headers(client, test_admin):

    response = client.post(
        "/auth/login",
        data={
            "username": test_admin.email,
            "password": "AdminPassword123"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }
