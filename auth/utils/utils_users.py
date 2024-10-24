import logging

import bcrypt
import jwt
from fastapi import (
    Depends
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
)

from auth.core.config import http_bearer, setup_logging
from auth.utils import utils_jwt as auth_utils
from auth.exceptions import (
    InvalidTokenException,
    AuthFailedException
)
from auth.schemas.token import TokenSchema

setup_logging()


async def refresh_token_of_current_user(token: HTTPAuthorizationCredentials = Depends(http_bearer)):
    token_credentials = token.credentials.replace("Bearer ", "")
    try:
        payload = await auth_utils.decode_jwt(token_credentials)
    except jwt.ExpiredSignatureError:
        raise AuthTokenExpiredException
    except jwt.InvalidTokenError:
        raise InvalidTokenException

    username = payload.get("username")
    user = await user_repo.get_user_by_username(username)

    if not user:
        raise InvalidTokenException

    new_token = await auth_utils.encode_jwt(
        {
            "username": user.username,
            "password": user.password,
            "email": user.email
        }
    )
    logging.info(f"Token refreshed for user: {username}")
    return TokenSchema(
        access_token=new_token,
        token_type="Bearer"
    )


async def compare_passwords(password, hashed_password):
    if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        raise AuthFailedException
    return True


import bcrypt


async def hash_password(
        password: str,
) -> str:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()

    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')


async def validate_password(
        password: str,
        hashed_password: str
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password
    )
