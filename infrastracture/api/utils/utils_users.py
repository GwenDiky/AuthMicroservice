from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
)
from fastapi import (
    Depends,
    Security
)
from auth.domain.entities.user import UserSchema
from auth.domain.entities.token import Token
from . import utils_jwt as auth_utils
from ...exceptions import InvalidTokenException
import jwt
import logging
import os
from infrastracture.security.config import http_bearer, user_repo, setup_logging

setup_logging()


async def get_current_auth_user(token: HTTPAuthorizationCredentials = Depends(http_bearer)):
    try:
        token_credentials = token.credentials.replace("Bearer ", "")
        payload = await auth_utils.decode_jwt(token_credentials)

        logging.info(f"username: {payload.get('username')}"
                     f"email: {payload.get('email')}"
                     f"created_at: {payload.get('created_at')}"
                     f"date_of_birth: {payload.get('date_of_birth')}"
                     f"phone: {payload.get('phone')}"
                     )

        return await user_repo.get_user_by_username(payload.get("username"))
    except jwt.ExpiredSignatureError:
        raise AuthTokenExpiredException
    except jwt.InvalidTokenError:
        raise InvalidTokenException


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
        return Token(
            access_token=new_token,
            token_type="Bearer"
        )
    except jwt.ExpiredSignatureError:
        raise AuthTokenExpiredException
    except jwt.InvalidTokenError:
        raise InvalidTokenException


async def get_info_of_user_by_token(token: Token) -> UserSchema:
    token_credentials = token.access_token
    payload = await auth_utils.decode_jwt(token_credentials)

    username = payload.get("username")
    user = await user_repo.get_user_by_username(username)

    if not user:
        raise InvalidTokenException

    return user

