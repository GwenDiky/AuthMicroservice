from fastapi.security import (
    HTTPAuthorizationCredentials,
)
from fastapi import (
    Depends
)
from auth.schemas.user import UserSchema
from auth.schemas.token import TokenSchema
from auth.core.utils import utils_jwt as auth_utils
from exceptions import (
    InvalidTokenException,
    AuthFailedException
)
import jwt
import logging
from auth.core.config import http_bearer, setup_logging
import bcrypt

setup_logging()


async def refresh_token_of_current_user(token: HTTPAuthorizationCredentials = Depends(http_bearer)):
    try:
        token_credentials = token.credentials.replace("Bearer ", "")
        payload = await auth_utils.decode_jwt(token_credentials)

        username = payload.get("username")
        user = await user_repo.get_user_by_username(username)

        if not user:
            raise InvalidTokenException

        new_token = await auth_utils.encode_jwt(user.to_dict())
        logging.info(f"Token refreshed for user: {username}")
        return TokenSchema(
            access_token=new_token,
            token_type="Bearer"
        )
    except jwt.ExpiredSignatureError:
        raise AuthTokenExpiredException
    except jwt.InvalidTokenError:
        raise InvalidTokenException


async def compare_passwords(password, hashed_password):
    if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        raise AuthFailedException
    return True
