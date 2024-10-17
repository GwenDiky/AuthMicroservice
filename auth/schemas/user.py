from datetime import date, datetime
from typing import Optional, Annotated
from uuid import UUID, uuid4

from annotated_types import MinLen, MaxLen
from pydantic import (
    BaseModel, EmailStr, ConfigDict, Field)
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserSchema(BaseModel):
    model_config = ConfigDict(
        strict=True)

    id: UUID = Field(default_factory=uuid4)
    username: str
    created_at: date = Field(default_factory=date.today)
    role: str = "user"
    # avatar:
    date_of_birth: Optional[date]
    phone_number: Optional[PhoneNumber] = None
    email: EmailStr
    password: str


class UserCreateSchema(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(50)]
    password: str

    phone_number: Optional[PhoneNumber] = None
    email: Optional[EmailStr]

    date_of_birth: Optional[date] = None


class UserInDBSchema(BaseModel):
    id: int
    username: Annotated[str, MinLen(3), MaxLen(50)]
    password: str
    email: Optional[EmailStr]
    created_at: datetime
    date_of_birth: date
    phone_number: Optional[PhoneNumber]
    role: str
