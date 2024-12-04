from datetime import date, datetime
from typing import Optional, Annotated
from uuid import UUID, uuid4

from annotated_types import MinLen, MaxLen
from pydantic import (
    BaseModel, EmailStr, ConfigDict, Field)
from pydantic_extra_types.phone_numbers import PhoneNumber
from auth.schemas.token_schema import TokenSchema


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    id: UUID = Field(default_factory=uuid4)
    username: str
    created_at: date = Field(default_factory=date.today)
    is_superuser: bool = False
    date_of_birth: Optional[date]
    phone_number: Optional[PhoneNumber] = None
    email: EmailStr
    password: str
    is_verified: bool = Field(default=False)


class UserSchemaWithoutPassword(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int
    username: str
    created_at: date = Field(default_factory=date.today)
    is_superuser: bool = False
    date_of_birth: Optional[date]
    phone_number: Optional[PhoneNumber] = None
    email: EmailStr
    is_verified: bool = Field(default=False)


class UserCreateSchema(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(50)]
    password: str

    phone_number: Optional[PhoneNumber]
    email: Optional[EmailStr]

    date_of_birth: Optional[date]


class UserInDBSchema(BaseModel):
    id: int
    username: Annotated[str, MinLen(3), MaxLen(50)]
    password: str
    email: Optional[EmailStr]
    created_at: datetime
    date_of_birth: Optional[date]
    phone_number: Optional[PhoneNumber]
    is_superuser: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    date_of_birth: Optional[datetime] = None
    phone_number: Optional[PhoneNumber] = None


class MessageSchemaPasswordChanged(BaseModel):
    message: str = "Password was changed successfully"

class MessageSchemaLogout(BaseModel):
    message: str = "User successfully logged out"