from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import asc, desc


class Paginator(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1)
    sort: Optional[str] = None
    filter: Optional[str] = None

    def apply(self, query, model):
        if self.sort:
            sort_field = getattr(model, self.sort.lstrip("-"), None)
            if sort_field is not None:
                query = query.order_by(
                    desc(sort_field) if self.sort.startswith("-") else asc(
                        sort_field)
                )

        query = query.offset((self.page - 1) * self.limit).limit(self.limit)
        return query


class PaginationSchema(BaseModel):
    page_number: int
    page_size: int
    total_pages: int
    total_records: int
    content: list
