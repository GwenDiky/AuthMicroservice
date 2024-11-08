from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import asc, desc
from fastapi import Depends, Query

class Paginator(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1)
    sort: Optional[str] = None
    filter: Optional[str] = None

    def apply(self, query, model):
        if self.sort:
            sort_field = getattr(model, self.sort.lstrip('-'), None)
            if sort_field is not None:
                query = query.order_by(desc(sort_field) if self.sort.startswith('-') else asc(sort_field))

        query = query.offset((self.page - 1) * self.limit).limit(self.limit)
        return query
