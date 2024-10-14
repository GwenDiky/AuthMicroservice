from auth.database.repo import SqlAlchemyARepository
from auth.database.user import User
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)
from auth.core.settings import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import engine

class UserRepository(SqlAlchemyARepository):
    model = User

    def __init__(self, async_engine: engine):
        super().__init__(async_engine)

async def get_user_repo() -> UserRepository:
    return UserRepository(create_async_engine(
        settings.db.db_url,
        echo=True
    ))
