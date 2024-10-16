import logging
from abc import ABC, abstractmethod

from sqlalchemy import (
    select
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from auth.core.base import Base
from auth.database.user import User
from auth.exceptions import BadRequestException, UserNotFoundException


class AbstractRepository(ABC):
    @abstractmethod
    async def create_user_table(self):
        raise NotImplementedError

    @abstractmethod
    async def add_new_user(self, user: User):
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_username(self, username: str):
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_id(self, id: int):
        raise NotImplementedError

    @abstractmethod
    async def change_password_of_current_user(self, user: User, hashed_password: str):
        raise NotImplementedError


class SqlAlchemyARepository(AbstractRepository):
    model = None

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_new_user(self, user: User) -> User:
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
        except SQLAlchemyError as db_error:
            await self.db.rollback()
            logging.error(f"Error occurred: {db_error}")
            raise SignUpFailedException
        return user

    async def create_user_table(self):
        async with self.db.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_user_by_username(self, username: str):
        try:
            query = select(User).where(User.username == username)
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()
            if not user:
                raise UserNotFoundException
            logging.info(f"data of {user.username}:\n "
                         f"email: {user.email}\n "
                         f"birthday: {user.date_of_birth}\n"
                         f"phone: {user.phone_number}")
            return user
        except SQLAlchemyError as db_error:
            logging.error(f"Database error {db_error}")
            raise BadRequestException(f"Database error: {db_error}")

    async def get_user_by_id(self, id: int):
        try:
            query = select(User).where(User.id == id)
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()
            if not user:
                raise UserNotFoundException
            logging.info(f"data of {user.username}:\n "
                         f"email: {user.email}\n "
                         f"birthday: {user.date_of_birth}\n"
                         f"phone: {user.phone_number}")
            return user
        except SQLAlchemyError as db_error:
            logging.error(f"Database error {db_error}")
            raise BadRequestException(f"Database error: {db_error}")

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

    async def delete_user(self, id: int):
        try:
            query = select(User).where(User.id == id)
            obj = await self.db.execute(query)
            user = obj.scalar_one_or_none()
            await self.db.delete(user)
            await self.db.commit()
        except SQLAlchemyError as db_error:
            await self.db.rollback()
            logging.error(f"Error occurred: {db_error}")
            raise BadRequestException(f"Database error: {db_error}")
        return {"result": "user was deleted"}
