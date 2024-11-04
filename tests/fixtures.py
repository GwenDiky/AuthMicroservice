import httpx
import pytest
import pytest_asyncio
from sqlalchemy import event
from auth.models.core import AsyncSession, clear_db, engine


@pytest.fixture
async def api_client():
    from auth.main import app
    async with httpx.AsyncClient(app=app, base_url='http://test') as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def db_session():
    async with AsyncSession() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def db(db_session):
    await clear_db()
    yield db_session


@pytest_asyncio.fixture(scope="function")
async def async_db_session():
    connection = await engine.connect()
    transaction = await connection.begin()
    async_session = AsyncSession(bind=connection)
    nested = await connection.begin_nested()

    @event.listens_for(async_session.sync_session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested

        if not nested.is_active:
            nested = connection.sync_connection.begin_nested()

    try:
        yield async_session
    finally:
        await transaction.rollback()
        await async_session.close()
        await connection.close()
