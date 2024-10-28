from typing import List, Generic, TypeVar, Any
from pydantic import BaseModel
from auth.core.base import Base


class ResponseSchema(BaseModel):
    detail: str
    result: Any

class PageResponse(BaseModel):
    page_number: int
    page_size: int
    total_pages: int
    total_record: int
    content: List[Any]