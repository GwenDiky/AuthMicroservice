from auth.database.repo import SqlAlchemyARepository
from auth.database.user import User
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)

class UserRepository(SqlAlchemyARepository):
    model = User

    def __init__(self):
        super().__init__()
