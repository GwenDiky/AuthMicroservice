import logging

from fastapi import Query
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.database.repo import SqlAlchemyRepository
from auth.exceptions import BadRequestException, UserNotFoundException
from auth.models.user_model import User


class UserRepository(SqlAlchemyRepository):
    model = User

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def add_new_user(self, new_object: User) -> User:
        return await super().add_new(new_object)

    async def get_user_by_username(self, username: str) -> User:
        try:
            query = select(User).where(User.username == username)
            result = await self.db.execute(query)
            obj = result.scalar_one_or_none()
            if not obj:
                raise UserNotFoundException
            return obj
        except SQLAlchemyError as db_error:
            logging.error(f"Database error {db_error}")
            raise BadRequestException(f"Database error: {db_error}")

    async def get_user_by_id(self, id: int) -> User:
        return await super().get_by_id(model=self.model, id=id)

    async def update_status_of_user_verification(self, user_data: dict) -> User:
        return await super().update_status_of_email_verification(
            model=self.model, obj_data=user_data
        )

    async def delete_user_obj(self, id: int):
        return await super().delete_obj(model=self.model, id=id)

    async def update_profile_of_current_user(self, id: int, obj_data: dict) -> User:
        user = await self.get_user_by_id(id)
        return await super().update_current_obj(user, obj_data)

    async def change_password_of_current_user(self, id: int, hashed_password: str):
        try:
            user = await self.get_user_by_id(id)
            user.password = hashed_password
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
        except SQLAlchemyError as db_error:
            await self.db.rollback()
            logging.error(f"Error occurred: {db_error}")
            raise BadRequestException(f"Database error: {db_error}")
        return user

    async def get_user_by_email(self, email: str):
        try:
            query = select(User).where(User.email == email)
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()
            if not user:
                raise UserNotFoundException
            logging.info(
                f"data of {user.username}:\n "
                f"email: {user.email}\n "
                f"birthday: {user.date_of_birth}\n"
                f"phone: {user.phone_number}"
            )
            return user
        except SQLAlchemyError as db_error:
            logging.error(f"Database error {db_error}")
            raise BadRequestException(f"Database error: {db_error}")

    async def get_all_users(
        self,
        page: int = 1,
        limit: int = 10,
        sort: str = Query(None, alias="sort"),
        filter: str = Query(None, alias="filter"),
    ):
        return await super().get_all(
            page=page, limit=limit, sort=sort, filter=filter, model=self.model
        )
