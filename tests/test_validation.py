
# API Validation Tests

# Test 1: Invalid email
def test_register_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "invalid-email",
            "age": 24,
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 422


# Test 2: Password too short
def test_register_short_password(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "short@example.com",
            "age": 24,
            "password": "123"
        }
    )

    assert response.status_code == 422


# Test 3: Name too short
def test_register_short_name(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "A",
            "email": "name@example.com",
            "age": 24,
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 422


# Test 4: Age out of range
def test_register_invalid_age(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "age@example.com",
            "age": 150,
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 422


# Test 5: Missing required field
def test_register_missing_password(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "missing@example.com",
            "age": 24
        }
    )

    assert response.status_code == 422


# Test 6: Empty request body
def test_register_empty_body(client):
    response = client.post(
        "/auth/register",
        json={}
    )

    assert response.status_code == 422
