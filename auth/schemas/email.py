from pydantic import BaseModel
from typing import List


class EmailSchema(BaseModel):
    addresses: List[str]

