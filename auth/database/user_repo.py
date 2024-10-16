from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from auth.database.repo import SqlAlchemyARepository
from auth.database.user import User


class UserRepository(SqlAlchemyARepository):
    model = User

    def __init__(self, db: AsyncSession):
        super().__init__(db)