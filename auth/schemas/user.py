from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen
from pydantic import (
    BaseModel, field_validator,
    EmailStr, ConfigDict, Field)
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import date
from uuid import UUID, uuid4
from enum import Enum


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
    is_active: bool = True


class UserCreateSchema(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(50)]
    password: str

    phone_number: Optional[PhoneNumber] = None
    email: Optional[EmailStr]

    is_active: bool = True
    date_of_birth: Optional[date] = None
