import logging
from abc import ABC, abstractmethod

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.core.base import Base
from auth.core.config import setup_logging
from auth.exceptions import (BadRequestException, SignUpFailedException,
                             UserNotFoundException)
from auth.models.user_model import User
from auth.schemas.paginator_schema import Paginator

setup_logging()


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
    async def update_status_of_email_verification(
        self, user: User, user_data: dict
    ) -> User:
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
            logging.error("Error occurred: %s", db_error)
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
            # if not obj:
            #     raise UserNotFoundException
            return obj
        except SQLAlchemyError as db_error:
            logging.error("Database error: %s", db_error)
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

    async def update_current_obj(self, model: Base, obj_data: dict):
        try:
            for k, v in obj_data.items():
                setattr(model, k, v)

            await self.db.commit()
            await self.db.refresh(model)

        except SQLAlchemyError as db_error:
            await self.db.rollback()
            logging.error(f"Error occurred: {db_error}")
            raise BadRequestException(f"Database error: {db_error}")
        return {"result": "user was updated succesfully"}

    async def update_status_of_email_verification(
        self, model: Base, obj_data: dict
    ) -> User:
        try:
            for k, v in obj_data.items():
                setattr(model, k, v)

            await self.db.commit()
            await self.db.refresh(model)

        except SQLAlchemyError as db_error:
            await self.db.rollback()
            logging.error("Error occurred: %s", db_error)
            raise BadRequestException(f"Database error: {db_error}")

        return model

    async def get_all(self, paginator: Paginator):
        query = select(self.model)
        query = paginator.apply(query, self.model)
        result = await self.db.execute(query)
        users = result.scalars().all()
        return users

    async def get_total_count(self):
        count_query = select(func.count()).select_from(self.model)
        total_records_result = await self.db.execute(count_query)
        return total_records_result.scalar()

    @staticmethod
    def convert_sort(sort):
        return ",".join(sort.split("-"))

    @staticmethod
    def convert_columns(model, columns):
        if columns is None or columns == "all":
            return [model]
        return [getattr(model, col.strip()) for col in columns.split("-")]
