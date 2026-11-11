
import pytest
import jwt

from fastapi import HTTPException
from app import models
from app.dependencies import (
    get_db,
    get_current_user,
    get_current_admin
)
from app.core.config import settings
from app.core.security import create_access_token


# Test 1: Database dependency creates and closes session
def test_get_db():
    db_generator = get_db()
    db = next(db_generator)

    assert db is not None

    db_generator.close()


# Test 2: Invalid JWT token
def test_get_current_user_invalid_token(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user("invalid-token", db_session)

    assert exc_info.value.status_code == 401


# Test 3: JWT token without user ID
def test_get_current_user_missing_subject(db_session):
    token = jwt.encode(
        {},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token, db_session)

    assert exc_info.value.status_code == 401


# Test 4: User does not exist
def test_get_current_user_not_found(db_session):
    token = create_access_token({"sub": "999"})

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token, db_session)

    assert exc_info.value.status_code == 401


# Test 5: Inactive user
def test_get_current_user_inactive(db_session):
    user = models.User(
        name="Inactive User",
        email="inactive@example.com",
        age=25,
        password_hash="fake_hash",
        role="user",
        is_active=False
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token({"sub": str(user.id)})

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token, db_session)

    assert exc_info.value.status_code == 401


# Test 6: Normal user cannot access admin dependency
def test_get_current_admin_forbidden(test_user):
    with pytest.raises(HTTPException) as exc_info:
        get_current_admin(test_user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Admin access required"


# Test 7: Admin can access admin dependency
def test_get_current_admin_success(test_admin):
    result = get_current_admin(test_admin)

    assert result is test_admin
    assert result.role == "admin"
