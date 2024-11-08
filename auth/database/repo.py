import logging
import math
from abc import ABC, abstractmethod

from sqlalchemy import func, or_, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional

from auth.core.base import Base
from auth.core.config import setup_logging
from auth.exceptions import (BadRequestException, SignUpFailedException,
                             UserNotFoundException)
from auth.models.user_model import User
from auth.schemas.page import PaginationSchema

from auth.schemas.paginator import Paginator

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
            logging.error(f"Error occurred: {db_error}")
            raise BadRequestException(f"Database error: {db_error}")

        return model

    async def get_all(
        self,
        model: Base,
        page: int = 1,
        limit: int = 10,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
    ):
        query = select(model)
        if filter is not None and filter != "null":
            try:
                criteria = dict(x.split("*") for x in filter.split("-"))
            except ValueError:
                raise ValueError(
                    "Filter format is incorrect. Ensure it is in the format 'key*value-key*value'."
                )

            criteria_list = []
            for attr, value in criteria.items():
                _attr = getattr(model, attr)

                if value.lower() == "true":
                    criteria_list.append(_attr.is_(True))
                elif value.lower() == "false":
                    criteria_list.append(_attr.is_(False))
                else:
                    search = "%{}%".format(value)
                    criteria_list.append(_attr.like(search))

            query = query.filter(or_(*criteria_list))

        if sort is not None and sort != "null":
            query = query.order_by(text(self.convert_sort(sort)))

        count_query = select(func.count(1)).select_from(query)

        offset_page = (page - 1) * limit
        query = query.offset(offset_page).limit(limit)

        total_record = (await self.db.execute(count_query)).scalar() or 0
        result = await self.db.execute(query)

        result_list = [dict(row) for row in result.mappings()]

        total_page = math.ceil(total_record / limit)

        return PaginationSchema(
            page_number=page,
            page_size=limit,
            total_pages=total_page,
            total_record=total_record,
            content=result_list,
        )

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
        else:
            return [getattr(model, col.strip()) for col in columns.split("-")]
