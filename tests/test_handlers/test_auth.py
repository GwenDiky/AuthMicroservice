from unittest.mock import AsyncMock, patch

from auth.schemas.user import UserCreateSchema
from auth.schemas.token_schema import TokenSchema
from auth.services.email import verify_email
from auth.services.user import UserRepository
from auth.utils.utils_users import hash_password
from auth.utils.utils_mail import create_user_send_message
from auth.api.handlers.user import signup
from tests.fixtures import db, db_session, api_client, mock_redis_client
from fastapi.encoders import jsonable_encoder
import uuid
import pytest
from auth.exceptions import AuthFailedException, InvalidTokenException
import logging
from auth.core.config import setup_logging
from auth.services.user import User
from tests.conftest import event_loop
from tests.utils.users import create_user, user_schema, create_user_by_fields
from auth.utils.utils_jwt import (
    encode_jwt
)

setup_logging()

class TestRegistration:
    user_properties = {
        "username":"testuser",
        "password":"securepassword",
        "phone_number":None,
        "email":"test@example.com",
        "date_of_birth":None
    }
    url = '/api/user/signup'

    @pytest.mark.asyncio
    async def test_create_user(self, db, api_client):
        async with api_client as client:
            response = await client.post(self.url, json=user_schema.model_dump())

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_user_invalid_body(self, db, api_client, event_loop):
        response = await api_client.post(self.url, json=self.user_properties | {"email":"smth"})
        assert response.status_code == 422

        response = await api_client.post(self.url, json=self.user_properties | {"username":"31"})
        assert response.status_code == 422

        response = await api_client.post(self.url, json=self.user_properties | {"phone_number": "3982Jdseq"})
        assert response.status_code == 422

        response = await api_client.post(self.url, json=self.user_properties | {"phone_number": "+37529328873"})
        assert response.status_code == 422


class TestVerification:
    url = '/api/user/resend_verification?email='
    @pytest.mark.asyncio
    async def test_resend_verification(self, api_client, db, event_loop):
        user = await create_user(db)
        assert user is not None, "User wasn't created"

        async with api_client as client:
            response = await client.post(self.url + user.email)

        assert response.status_code == 200
        assert response.json().get("message") == ("Verification email resend "
                                                  "successfully")

    @pytest.mark.asyncio
    async def test_resend_verification_to_invalid_email(self, api_client, db, event_loop):
        invalid_email = "non_existent_mail@gmail.com"
        async with api_client as client:
            response = await client.post(self.url + invalid_email)
        assert response.status_code == 403


class TestLogin:
    url = '/api/user/login'
    @pytest.mark.asyncio
    async def test_login(self, api_client, db, event_loop):
        user = await create_user(db)
        assert user is not None, "User wasn't created"

        async with api_client as client:
            response = await client.post(
                self.url,
                data={"username": user.username, "password": user_schema.password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
        assert "access_token" in response.json()

    @pytest.mark.asyncio
    async def test_login_invalid(self, api_client, db, event_loop):
        username = "invalid_username"
        password = "invalid_password"

        async with api_client as client:
            response = await client.post(
                self.url,
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

        assert response.status_code == 403

class TestLogout:
    url = '/api/user/logout'

    @pytest.mark.asyncio
    async def test_logout(self, api_client, db, mock_redis_client):
        user = await create_user(db)
        token = await encode_jwt({"sub": user.id, "username": user.username})

        async with api_client as client:
            response = await client.post(self.url, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json().get("message") == "Successfully logged out"

    @pytest.mark.asyncio
    async def test_logout_invalid(self, api_client, db, mock_redis_client):
        token = "token"
        response = await api_client.post(self.url, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401

        response = await api_client.post(self.url,  headers={})
        assert  response.status_code == 401

        blacklisted_token = "blacklisted_token"
        response = await api_client.post(self.url, headers={"Authorization": f"Bearer {blacklisted_token}"})
        assert response.status_code == 401


class TestUser:
    user_properties = {
        "username":"testuser",
        "password":"securepassword",
        "phone_number":None,
        "email":"test@example.com",
        "date_of_birth":None
    }

    url_current_user = '/api/user/me'
    url_delete_current_user = '/api/user/me/delete'

    @pytest.mark.asyncio
    async def test_delete_me(self, api_client, db):
        user = await create_user(db)
        token = await encode_jwt({"sub": user.id, "username": user.username})

        async with api_client as client:
            response = await client.delete(self.url_delete_current_user, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json().get("result") == "Object was deleted"


    @pytest.mark.asyncio
    async def test_delete_me_invalid_token(self, api_client, db):
        async with api_client as client:
            response = await client.delete(self.url_delete_current_user, headers={})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(self, api_client, db, mock_redis_client):
        user = await create_user(db)
        token = await encode_jwt({"sub": user.id, "username": user.username, "email": user.email})

        async with api_client as client:
            response = await client.get(self.url_current_user, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
        assert response.json().get("username") == "testuser"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid(self, api_client, db, mock_redis_client):
        blacklisted_token = "blacklisted_token"
        response = await api_client.post(self.url_current_user, headers={"Authorization": f"Bearer {blacklisted_token}"})
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_get_all_person(self, api_client, db):
        for i in range(5):
            await create_user_by_fields(db, username=f"username{i}",
                                        password=f"password{i}",
                                        email=f"username{i}@gmail.com",
                                        phone_number="+375332565435",
                                        date_of_birth=None)
        async with api_client as client:
            response = await client.get("/api/user/get-all-users?page=1&limit=5")

        assert response.status_code == 200
        data = response.json()

        print(f"дэйта: {data}")

        assert data["page_number"] == 1
        assert data["page_size"] == 5
        assert len(data["content"]) == 5

        for user in data["content"]:
            assert "id" in user
            assert "username" in user
            assert "email" in user
            assert "created_at" in user
            assert "is_superuser" in user
            assert "phone_number" in user
            assert "is_verified" in user



class TestAuth:
    @pytest.mark.asyncio
    async def test_refresh_token(self, api_client, db, mock_redis_client):
        user = await create_user(db)
        token = await encode_jwt({"sub": user.id, "username": user.username})

        async with api_client as client:
            response = await client.post('/api/user/refresh-token', headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert "access_token" in response.json()

    @pytest.mark.asyncio
    async def test_change_password(self, api_client, db, mock_redis_client):
        new_password = "newsecurepassword"

        user = await create_user(db)
        token = await encode_jwt({"sub": user.id, "username": user.username})

        async with api_client as client:
            response = await client.put(f'/api/user/change-password?new_password={new_password}',
                                        headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json().get("id") == user.id

    @pytest.mark.asyncio
    async def test_forgot_password(self, api_client, db):
        new_password="newpassword"
        user = await create_user(db)

        async with api_client as client:
            response = await client.post(f'/api/user/forgot-password?email={user.email}&new_password={new_password}')

        assert response.status_code == 200

        assert response.json().get("message") == (f"Check up u'r mail:"
                                               f" {user.email}")
