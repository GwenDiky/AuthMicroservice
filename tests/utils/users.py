from sqlalchemy.ext.asyncio import AsyncSession
from auth.services.user import UserRepository, User
from auth.schemas.user import UserCreateSchema
from auth.utils.utils_users import hash_password
import pytest_asyncio


@pytest_asyncio.fixture
async def user_properties():
    return {"username": "testuser",
            "password": "securepassword",
            "phone_number": None,
            "email": "test@example.com",
            "date_of_birth": None
    }

@pytest_asyncio.fixture
async def create_user(db: AsyncSession):
    async def _create_user(username: str = "testuser", password: str = "securepassword", email: str = "test@example.com",
                           phone_number: str = None, date_of_birth: str = None):
        user_data = {
            'username': username,
            'password': password,
            'email': email,
            'phone_number': phone_number,
            'date_of_birth': date_of_birth
        }

        user_data["password"] = await hash_password(user_data["password"])

        new_user = User(**user_data)

        user = await UserRepository(db).add_new_user(new_user)
        return user

    return _create_user
