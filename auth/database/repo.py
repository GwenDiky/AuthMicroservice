from sqlalchemy import (
    select
)

from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)
import os
from auth.core.base import Base
from auth.database.user import User
import logging
from sqlalchemy.exc import SQLAlchemyError
from exceptions import BadRequestException
from abc import ABC, abstractmethod
from auth.core.settings import settings


class AbstractRepository(ABC):
    @abstractmethod
    async def create_user_table(self):
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_username(self, username: str):
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_id(self, id: int):
        raise NotImplementedError

    @abstractmethod
    async def change_password_of_current_user(self, new_password: str):
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_token(self):
        raise NotImplementedError

    @abstractmethod
    async def get_db(self):
        raise NotImplementedError


class SqlAlchemyARepository(AbstractRepository):
    model = None

    def __init__(self):
        self.db_url = settings.db.db_url
        self.engine = create_async_engine(
            self.db_url,
            echo=True
        )
        self.sessionLocalAsync = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def create_user_table(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_user_by_username(self, username: str):
        async with self.sessionLocalAsync(expire_on_commit=False) as session:
            try:
                query = select(User).where(User.username == username)
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                if not user:
                    return "user wasn't found. check up your statement again"
                logging.info(f"data of {user.username}:\n "
                             f"email: {user.email}\n "
                             f"birthday: {user.date_of_birth}\n"
                             f"phone: {user.phone_number}\n "
                             f"valid: {user.is_active}\n")
                return user
            except SQLAlchemyError as db_error:
                logging.error(f"Database error {db_error}")
                raise BadRequestException(f"Database error: {db_error}")

    async def get_user_by_id(self, id: int):
        async with self.sessionLocalAsync(expire_on_commit=False) as session:
            try:
                query = select(User).where(User.id == id)
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                if not user:
                    return "user wasn't found. check up your statement again"
                logging.info(f"data of {username}:\n "
                             f"email: {user.email}\n "
                             f"birthday: {user.date_of_birth}\n"
                             f"phone: {user.phone_number}\n "
                             f"valid: {user.is_active}\n")
                return user
            except SQLAlchemyError as db_error:
                logging.error(f"Database error {db_error}")
                raise BadRequestException(f"Database error: {db_error}")

    async def change_password_of_current_user(self, new_password: str):
        ...

    async def get_user_by_token(self):
        ...

    async def get_db(self) -> AsyncSession:
        async with self.sessionLocalAsync() as session:
            yield session
