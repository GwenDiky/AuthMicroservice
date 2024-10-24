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
from auth.exceptions import (
    BadRequestException,
    UserNotFoundException,
    SignUpFailedException
)
from datetime import datetime


class AbstractRepository(ABC):
    @abstractmethod
    async def create_table(self):
        raise NotImplementedError

    @abstractmethod
    async def add_new(self, new_object):
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, model: Base, id: int):
        raise NotImplementedError

    async def delete_obj(self, model: Base, id: int):
        raise NotImplementedError

    @abstractmethod
    async def update_status_of_email_verification(self, user: User, user_data: dict) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update_current_obj(self, model: Base, obj_data: dict):
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

    async def get_user_by_email(self, email: str):
        try:
            query = select(model).where(model.id == id)
            query = select(User).where(User.email == email)
            result = await self.db.execute(query)
            obj = result.scalar_one_or_none()
            await self.db.delete(obj)
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
        except SQLAlchemyError as db_error:
            await self.db.rollback()
            logging.error(f"Error occurred: {db_error}")
            raise BadRequestException(f"Database error: {db_error}")
        return {"result": "Object was deleted"}

    async def update_current_obj(self, model: Base,
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
        return {"result": "user was deleted"}

    async def update_profile_of_current_user(self, id: int,
                                             user_data: dict) -> User:
        try:
            user = await self.get_user_by_id(id)
            user.username = user_data["username"]
            user.email = user_data['email']
            user.date_of_birth = user_data['date_of_birth']
            user.phone_number = user_data['phone_number']

            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
        except SQLAlchemyError as db_error:
            await self.db.rollback()
            logging.error(f"Error occurred: {db_error}")
            raise BadRequestException(f"Database error: {db_error}")
        return user

    async def update_status_of_email_verification(self, user: User, user_data: dict) -> User:
        try:
            for k, v in user_data.items():
                setattr(user, k, v)

            await self.db.commit()
            await self.db.refresh(user)

        except SQLAlchemyError as db_error:
            await self.db.rollback()
            logging.error(f"Error occurred: {db_error}")
            raise BadRequestException(f"Database error: {db_error}")

        return user
