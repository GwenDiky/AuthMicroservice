import httpx
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy import event
from auth.models.core import AsyncSession, clear_db, engine, sessionLocalAsync
from auth.schemas.user import UserInDBSchema, UserCreateSchema
from auth.services.user import UserRepository
from unittest.mock import AsyncMock


@pytest_asyncio.fixture
async def api_client():
    from auth.main import app
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url='http://test')
    try:
        yield client
    finally:
        await client.aclose()


@pytest_asyncio.fixture(autouse=True, scope="function")
async def db_session():
    async with sessionLocalAsync() as session:
        await clear_db()
        yield session
        await session.rollback()


@pytest_asyncio.fixture(autouse=True, scope="function")
async def db(db_session):
    yield db_session



@pytest.fixture
def mock_redis_client(monkeypatch):
    mock = AsyncMock()
    mock.get.return_value = None
    mock.set.return_value = True

    async def mock_get_redis():
        return mock

    async def mock_is_token_blacklisted(token, redis_client):
        if token == "blacklisted_token":
            return True
        return False

    monkeypatch.setattr('auth.utils.redis_client.get_redis', mock_get_redis)
    monkeypatch.setattr('auth.utils.redis_client.is_token_blacklisted', mock_is_token_blacklisted)
    return mock


@pytest_asyncio.fixture(scope="function")
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