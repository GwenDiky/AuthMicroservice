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
from datetime import datetime
from auth.core.base import Base


class AbstractRepository(ABC):
    @abstractmethod
    async def create_table(self):
        raise NotImplementedError

    @abstractmethod
    async def add_new(self, new_object):
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, model: Base, username: str):
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, model: Base, id: int):
        raise NotImplementedError

    @abstractmethod
    async def change_password_of_current_user(self, user: User, hashed_password: str):
        raise NotImplementedError

    @abstractmethod
    async def update_profile_of_current_user(self, model: Base, obj_data: dict):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_new(self, new_object):
        try:
            self.db.add(new_object)
            await self.db.commit()
            await self.db.refresh(new_object)
        except SQLAlchemyError as db_error:
            await self.db.rollback()
            logging.error(f"Error occurred: {db_error}")
            raise SignUpFailedException
        return new_object

    async def create_table(self):
        async with self.db.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_by_username(self, model: Base, username: str):
        try:
            query = select(model).where(model.username == username)
            result = await self.db.execute(query)
            obj = result.scalar_one_or_none()
            if not obj:
                raise UserNotFoundException
            return obj
        except SQLAlchemyError as db_error:
            logging.error(f"Database error {db_error}")
            raise BadRequestException(f"Database error: {db_error}")

    async def get_by_id(self, model: Base, id: int):
        try:
            query = select(model).where(model.id == id)
            result = await self.db.execute(query)
            obj = result.scalar_one_or_none()
            if not obj:
                raise UserNotFoundException
            return obj
        except SQLAlchemyError as db_error:
            logging.error(f"Database error {db_error}")
            raise BadRequestException(f"Database error: {db_error}")

    async def delete_obj(self, model: Base, id: int):
        try:
            query = select(model).where(model.id == id)
            result = await self.db.execute(query)
            obj = result.scalar_one_or_none()
            await self.db.delete(obj)
            await self.db.commit()
        except SQLAlchemyError as db_error:
            await self.db.rollback()
            logging.error(f"Error occurred: {db_error}")
            raise BadRequestException(f"Database error: {db_error}")
        return {"result": "Object was deleted"}

    async def change_password_of_current_user(self, id: int, hashed_password: str):
        try:
            user = await self.get_by_id(id)
            user.password = hashed_password
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
        except SQLAlchemyError as db_error:
            await self.db.rollback()
            logging.error(f"Error occurred: {db_error}")
            raise BadRequestException(f"Database error: {db_error}")
        return user

    async def update_profile_of_current_user(self, model: Base,
                                             obj_data: dict):
        try:
            for k, v in obj_data.items():
                setattr(model, k, v)

            await self.db.commit()
            await self.db.refresh(model)

        except SQLAlchemyError as db_error:
            await self.db.rollback()
            logging.error(f"Error occurred: {db_error}")
            raise BadRequestException(f"Database error: {db_error}")

        return model


