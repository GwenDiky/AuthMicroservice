import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from auth.api.main import app
from datetime import date
from uuid import uuid4

client = TestClient(app)


@pytest.fixture
def test_user():
    return {
        "id": str(uuid4()),
        "username": "maria",
        "created_at": str(date.today()),
        "role": "User_without_permissions",
        "date_of_birth": str(date(2005, 8, 20)),
        "phone": "tel:+375291118957",
        "email": "user@example.com"
    }


@pytest.mark.parametrize("username, role, email", [
    ("violetta", "User_without_permissions", "user@example.com"),
    ("john_doe", "Admin", "admin@example.com"),
    ("alice", "User_without_permissions", "alice@example.com"),
])
def test_create_user_parametrized(username, role, email):
    user_data = {
        "id": str(uuid4()),
        "username": username,
        "created_at": str(date.today()),
        "role": role,
        "date_of_birth": str(date(1995, 5, 15)),
        "phone": "tel:+375292188397",
        "email": email
    }

    response = client.post(f"/users/{user_data['id']}", json=user_data)

    assert response.status_code == 200
    assert response.json()["username"] == username
    assert response.json()["role"] == role
    assert response.json()["email"] == email


@patch("main.jsonable_encoder")
def test_create_user_with_mock(mock_jsonable_encoder, test_user):
    test_user['phone'] = 'tel:+375-29-111-89-57'

    mock_jsonable_encoder.return_value = test_user

    user_id = test_user["id"]
    response = client.post(f"/users/{user_id}", json=test_user)

    assert response.status_code == 200
    assert response.json() == test_user

