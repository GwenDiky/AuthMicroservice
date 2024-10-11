from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen
from pydantic import (
    BaseModel, field_validator,
    EmailStr, ConfigDict, Field)
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import date
from uuid import UUID, uuid4
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


def get_today():
    return date.today()


class UserSchema(BaseModel):
    model_config = ConfigDict(
        strict=True)  # pydantic will not automatically convert data types for non-matching types.

    id: UUID = Field(default_factory=uuid4)  # generate automatic
    username: str
    created_at: date = Field(default_factory=date.today)
    role: Optional[UserRole] = UserRole.USER
    # avatar:
    date_of_birth: Optional[date]
    phone: PhoneNumber | None = None
    email: EmailStr | None = None
    password: bytes
    is_active: bool = True


class UserCreateSchema(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(50)]
    password: bytes

    phone: Optional[PhoneNumber] = None
    email: Optional[EmailStr] = None

    is_active: bool = True
    date_of_birth: Optional[date] = None
