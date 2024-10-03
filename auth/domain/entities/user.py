from dataclasses import Field
from typing import Optional
from pydantic import (
    BaseModel, field_validator,
    EmailStr)
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import date
from uuid import UUID
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "Admin"
    USER_WITHOUT_PERMISSIONS = "User_without_permissions"


def get_today():
    return date.today()


class User(BaseModel):
    id: UUID
    username: str
    created_at: date
    role: UserRole = UserRole.USER_WITHOUT_PERMISSIONS
    # avatar:
    date_of_birth: Optional[date]
    phone: PhoneNumber
    email: EmailStr
    # order_by: Literal[]

    @field_validator('date_of_birth')
    def check_date_of_birth(cls, v) -> str:
        if v >= date.today():
            raise ValueError('date_of_birth must be less than today')
        return v
