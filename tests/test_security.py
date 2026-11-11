
import pytest
import jwt

from datetime import datetime, timedelta, timezone

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.core.config import settings


# Test 1: Password hashing
def test_password_hashing():

    password = "TestPassword123"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert hashed_password is not None


# Test 2: Verify correct password
def test_verify_correct_password():

    password = "TestPassword123"

    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password) is True


# Test 3: Reject incorrect password
def test_verify_incorrect_password():

    password = "TestPassword123"

    hashed_password = hash_password(password)

    assert verify_password("WrongPassword123", hashed_password) is False


# Test 4: Create JWT access token
def test_create_access_token():

    data = {"sub": "123"}

    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0


# Test 5: Decode JWT token successfully
def test_decode_access_token():

    data = {"sub": "123"}

    token = create_access_token(data)

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm]
    )

    assert payload["sub"] == "123"
    assert "exp" in payload


# Test 6: Reject invalid JWT token
def test_invalid_access_token():

    with pytest.raises(jwt.InvalidTokenError):

        jwt.decode(
            "invalid.token.value",
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )


# Test 7: Reject expired JWT token
def test_expired_access_token():

    expired_payload = {
        "sub": "123",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5)
    }

    expired_token = jwt.encode(
        expired_payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    with pytest.raises(jwt.ExpiredSignatureError):

        jwt.decode(
            expired_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
