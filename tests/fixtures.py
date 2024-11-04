import httpx
import pytest
import pytest_asyncio
from sqlalchemy import event
from auth.models.core import AsyncSession, clear_db, engine, sessionLocalAsync
from auth.schemas.user import UserInDBSchema, UserCreateSchema
from auth.services.user import UserRepository


@pytest.fixture
async def api_client():
    from auth.main import app
    async with httpx.AsyncClient(app=app, base_url='http://test') as client:
        yield client

@pytest_asyncio.fixture()
async def db_session():
    async with sessionLocalAsync() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def db(db_session):
    await clear_db()
    yield db_session

@pytest_asyncio.fixture
async def user_repo(db_session):
    repo = UserRepository(db_session)
    async def mock_add_new_user(user_data):
        return UserInDBSchema(
            email=user_data.email,
            date_of_birth=user_data.date_of_birth,
            username=user_data.username,
            is_verified=False
        )
    repo.add_new_user = mock_add_new_user
    return repo

@pytest_asyncio.fixture
async def user_create_schema():
    return UserCreateSchema(
        username="testuser",
        email="test@example.com",
        password="securepassword"
    )