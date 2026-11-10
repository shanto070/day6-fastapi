

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.main import app
from app.db.base import Base
from app.dependencies import get_db


# Separate in-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


# Override database dependency
def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# Reset database before every test
@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


# Test 1: User Registration
def test_user_registration():

    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "age": 24,
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    assert "password_hash" not in response.json()


# Test 2: Duplicate Email Registration
def test_duplicate_email_registration():

    user_data = {
        "name": "Test User",
        "email": "duplicate@example.com",
        "age": 24,
        "password": "TestPassword123"
    }

    client.post("/auth/register", json=user_data)

    response = client.post(
        "/auth/register",
        json=user_data
    )

    assert response.status_code == 409


# Test 3: User Login
def test_user_login():

    client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "age": 24,
            "password": "TestPassword123"
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "login@example.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()


# Test 4: Unauthorized Profile Access
def test_unauthorized_profile_access():

    response = client.get("/users/me")

    assert response.status_code == 401


# Test 5: Authorized Profile Access
def test_authorized_profile_access():

    client.post(
        "/auth/register",
        json={
            "name": "Profile User",
            "email": "profile@example.com",
            "age": 24,
            "password": "TestPassword123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "profile@example.com",
            "password": "TestPassword123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["email"] == "profile@example.com"


# Test 6: Normal User Cannot Access Admin Endpoint
def test_normal_user_admin_access():

    client.post(
        "/auth/register",
        json={
            "name": "Normal User",
            "email": "normal@example.com",
            "age": 24,
            "password": "TestPassword123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "normal@example.com",
            "password": "TestPassword123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


# Test 7: Admin Can Access Admin Endpoint
def test_admin_access():

    # Register admin user
    client.post(
        "/auth/register",
        json={
            "name": "Admin User",
            "email": "admin-test@example.com",
            "age": 24,
            "password": "TestPassword123"
        }
    )

    # Change role to admin in test database
    db = TestingSessionLocal()

    user = db.query(models.User).filter(
        models.User.email == "admin-test@example.com"
    ).first()

    user.role = "admin"
    db.commit()
    db.close()

    # Login as admin
    login_response = client.post(
        "/auth/login",
        data={
            "username": "admin-test@example.com",
            "password": "TestPassword123"
        }
    )

    token = login_response.json()["access_token"]

    # Access admin endpoint
    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["role"] == "admin"
