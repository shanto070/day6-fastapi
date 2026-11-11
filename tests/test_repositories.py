
from app import models
from app.repositories import user_repository


# Test 1: Get user by ID
def test_get_user_by_id(db_session):
    user = models.User(
        name="Repository User",
        email="repo@example.com",
        age=24,
        role="user",
        is_active=True
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    result = user_repository.get_user_by_id(db_session, user.id)

    assert result is not None
    assert result.id == user.id
    assert result.email == "repo@example.com"


# Test 2: Return None for an unknown user ID
def test_get_user_by_id_not_found(db_session):
    result = user_repository.get_user_by_id(db_session, 999)

    assert result is None


# Test 3: Get user by email
def test_get_user_by_email(db_session):
    user = models.User(
        name="Email User",
        email="email@example.com",
        age=25,
        role="user",
        is_active=True
    )

    db_session.add(user)
    db_session.commit()

    result = user_repository.get_user_by_email(
        db_session,
        "email@example.com"
    )

    assert result is not None
    assert result.email == "email@example.com"


# Test 4: Return all users
def test_get_all_users(db_session):
    user1 = models.User(
        name="User One",
        email="one@example.com",
        age=22,
        role="user",
        is_active=True
    )

    user2 = models.User(
        name="User Two",
        email="two@example.com",
        age=23,
        role="user",
        is_active=True
    )

    db_session.add_all([user1, user2])
    db_session.commit()

    result = user_repository.get_all_users(db_session)

    assert len(result) == 2


# Test 5: Create a new user
def test_create_user(db_session):
    user_data = {
        "name": "New Repository User",
        "email": "newrepo@example.com",
        "age": 26,
        "password_hash": "fake_password_hash",
        "role": "user",
        "is_active": True
    }

    result = user_repository.create_user(db_session, user_data)

    assert result.id is not None
    assert result.name == "New Repository User"
    assert result.email == "newrepo@example.com"
    assert result.role == "user"
