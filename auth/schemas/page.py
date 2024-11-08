from typing import Any, List

from pydantic import BaseModel


class ResponseSchema(BaseModel):
    detail: str
    result: Any


class PaginationSchema(BaseModel):
    page_number: int
    page_size: int
    total_pages: int
    total_records: int
    content: list
