
from app import schemas
from app.services import user_service


# Test 1: Get user profile
def test_get_user_profile(monkeypatch):

    expected_user = object()

    def fake_get_user_by_id(db, user_id):
        assert user_id == 1
        return expected_user

    monkeypatch.setattr(
        user_service.user_repository,
        "get_user_by_id",
        fake_get_user_by_id
    )

    result = user_service.get_user_profile(None, 1)

    assert result is expected_user


# Test 2: Get user by email
def test_get_user_by_email(monkeypatch):

    expected_user = object()

    def fake_get_user_by_email(db, email):
        assert email == "test@example.com"
        return expected_user

    monkeypatch.setattr(
        user_service.user_repository,
        "get_user_by_email",
        fake_get_user_by_email
    )

    result = user_service.get_user_by_email(
        None,
        "test@example.com"
    )

    assert result is expected_user


# Test 3: Get all users
def test_get_all_users(monkeypatch):

    expected_users = ["User 1", "User 2"]

    def fake_get_all_users(db):
        return expected_users

    monkeypatch.setattr(
        user_service.user_repository,
        "get_all_users",
        fake_get_all_users
    )

    result = user_service.get_all_users(None)

    assert result == expected_users


# Test 4: Register a new user
def test_register_user_success(monkeypatch):

    user_data = schemas.UserRegister(
        name="Test User",
        email="new@example.com",
        age=24,
        password="TestPassword123"
    )

    created_user = object()
    captured_data = {}

    # No existing user
    monkeypatch.setattr(
        user_service.user_repository,
        "get_user_by_email",
        lambda db, email: None
    )

    # Mock password hashing
    monkeypatch.setattr(
        user_service,
        "hash_password",
        lambda password: "fake_hashed_password"
    )

    # Mock repository create function
    def fake_create_user(db, data):
        captured_data.update(data)
        return created_user

    monkeypatch.setattr(
        user_service.user_repository,
        "create_user",
        fake_create_user
    )

    result = user_service.register_user(None, user_data)

    assert result is created_user
    assert captured_data["password_hash"] == "fake_hashed_password"
    assert "password" not in captured_data
    assert captured_data["email"] == "new@example.com"


# Test 5: Reject duplicate email
def test_register_user_duplicate_email(monkeypatch):

    user_data = schemas.UserRegister(
        name="Existing User",
        email="existing@example.com",
        age=25,
        password="TestPassword123"
    )

    existing_user = object()

    monkeypatch.setattr(
        user_service.user_repository,
        "get_user_by_email",
        lambda db, email: existing_user
    )

    # Creating a duplicate user must never happen
    def fake_create_user(db, data):
        raise AssertionError("Duplicate user should not be created")

    monkeypatch.setattr(
        user_service.user_repository,
        "create_user",
        fake_create_user
    )

    result = user_service.register_user(None, user_data)

    assert result is None
