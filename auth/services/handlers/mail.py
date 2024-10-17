import logging

import jwt
from fastapi import APIRouter, Depends
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.api.dependecies import get_current_auth_user
from auth.api.dependecies import get_info_of_user_by_token
from auth.core.config import setup_logging
from auth.core.security import hash_password
from auth.core.settings import settings
from auth.core.utils.utils_jwt import (
    encode_jwt
)
from auth.core.utils.utils_users import compare_passwords
from auth.database.core import get_async_session
from auth.database.user import User
from auth.database.user_repo import UserRepository
from auth.exceptions import (
    AuthFailedException,
    SignUpFailedException,
    PasswordNotChangedException,
    ProfileNotChangedException
)
from auth.schemas.token import TokenSchema
from auth.schemas.user import UserCreateSchema, UserInDBSchema, UserUpdateSchema
from auth.schemas.email import EmailSchema
from auth.services.email import mail, create_message

setup_logging()

mail_router = APIRouter()

@mail_router.post('/send-mail')
async def send_mail(emails: EmailSchema):
    mails = emails.addresses

    html = "<h1>Welcome to the Authmicroservice app</h1>"
    message = await create_message(
        recipients=mails,
        subject="Welcome",
        body=html
    )

    await mail.send_message(message)

    return {"message": "Email sent successfully"}


