from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from auth.api.dependecies import get_current_auth_user
from auth.database.repo import SqlAlchemyARepository
from auth.database.user import User
from sqlalchemy.exc import SQLAlchemyError
import logging
from auth.exceptions import SignUpFailedException


class UserRepository(SqlAlchemyRepository):
    model = User

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def add_new_user(self, new_object: User) -> User:
        return await super().add_new(new_object)

    async def get_user_by_username(self, username: str) -> User:
        return await super().get_by_username(model=self.model, username=username)

    async def get_user_by_id(self, id: int) -> User:
        return await super().get_by_id(model=self.model, id=id)

    async def delete_user_obj(self, id: int):
        return await super().delete_obj(model=self.model, id=id)

    async def update_profile_of_current_user(self, id: int, obj_data: dict) -> User:
        user = await self.get_user_by_id(id)
        return await super().update_profile_of_current_user(user, obj_data)

