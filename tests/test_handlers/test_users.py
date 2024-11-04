from unittest.mock import AsyncMock, patch

from auth.schemas.user import UserCreateSchema
from auth.services.email import verify_email
from auth.utils.utils_users import hash_password
from auth.utils.utils_mail import create_user_send_message
import pytest
from auth.api.handlers.user import signup
from tests.fixtures import db, user_create_schema, db_session
from fastapi.encoders import jsonable_encoder
import uuid



class TestUser:
    @pytest.mark.asyncio
    @patch("auth.utils.utils_users.hash_password", new_callable=AsyncMock)
    @patch("auth.services.email.verify_email", new_callable=AsyncMock)
    @patch("auth.utils.utils_mail.create_user_send_message", new_callable=AsyncMock)
    async def test_signup_handler(self,
                                  mock_send_message,
                                  mock_verify_email,
                                  mock_hash_password,
                                  db,
                                  user_create_schema
                                  ):
        unique_username = f"testuser_{uuid.uuid4()}"

        user_create_schema = UserCreateSchema(
            username=unique_username,
            password="securepassword",
            phone_number=None,
            email="test@example.com",
            date_of_birth=None
        )

        mock_hash_password.return_value = "hashedpassword"
        mock_verify_email.return_value = None
        mock_send_message.return_value = None

        result = await signup(user_create_schema, db=db)

        assert result.username == unique_username
