
# API Integration Tests

def test_user_registration(client):

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


def test_duplicate_email_registration(client):

    user_data = {
        "name": "Test User",
        "email": "duplicate@example.com",
        "age": 24,
        "password": "TestPassword123"
    }

    first_response = client.post(
        "/auth/register",
        json=user_data
    )

    second_response = client.post(
        "/auth/register",
        json=user_data
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_user_login(client):

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


def test_unauthorized_profile_access(client):

    response = client.get("/users/me")

    assert response.status_code == 401


def test_authorized_profile_access(client, auth_headers):

    response = client.get(
        "/users/me",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_normal_user_admin_access(client, auth_headers):

    response = client.get(
        "/users/",
        headers=auth_headers
    )

    assert response.status_code == 403


def test_admin_access(client, admin_headers):

    response = client.get(
        "/users/",
        headers=admin_headers
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["role"] == "admin"

# Additional Authentication and Authorization Tests

def test_invalid_token(client):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401


def test_inactive_user_cannot_access_profile(
    client, db_session, test_user
):
    test_user.is_active = False
    db_session.commit()

    response = client.get(
        "/users/me",
        headers={
            "Authorization": "Bearer " +
            __import__("app.core.security", fromlist=["create_access_token"])
            .create_access_token({"sub": str(test_user.id)})
        }
    )

    assert response.status_code == 401


def test_user_cannot_access_admin_endpoint(client, auth_headers):
    response = client.get(
        "/users/",
        headers=auth_headers
    )

    assert response.status_code == 403

# Test: Home endpoint
def test_home_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to Day 8 FastAPI Architecture"
    }


# Test: Process time middleware
def test_process_time_header(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "X-Process-Time" in response.headers
    assert float(response.headers["X-Process-Time"]) >= 0


# Test: Login with incorrect password
def test_login_incorrect_password(client, test_user):
    response = client.post(
        "/auth/login",
        data={
            "username": test_user.email,
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


# Test: Login with unknown email
def test_login_unknown_email(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "unknown@example.com",
            "password": "Password123"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
# Test: Global exception handler
def test_global_exception_handler(client):
    from app.main import app

    @app.get("/test-server-error")
    def trigger_server_error():
        raise Exception("Test internal error")

    from fastapi.testclient import TestClient

    test_client = TestClient(
        app,
        raise_server_exceptions=False
    )

    response = test_client.get("/test-server-error")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Internal server error"
    }
