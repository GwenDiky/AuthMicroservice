from typing import List

from pydantic import BaseModel


class EmailSchema(BaseModel):
    addresses: List[str]


class EmailResponseSchema(BaseModel):
    message: str = "Email was sent successfully"
