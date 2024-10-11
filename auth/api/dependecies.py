from fastapi.security import (
    HTTPAuthorizationCredentials,
)
from fastapi import (
    Depends
)
from auth.schemas.user import UserSchema
from auth.schemas.token import TokenSchema
from exceptions import InvalidTokenException
from auth.core.utils import utils_jwt as auth_utils
import jwt
import logging
from auth.core.config import http_bearer, user_repo, setup_logging

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


async def get_info_of_user_by_token(token: TokenSchema) -> UserSchema:
    token_credentials = token.access_token
    payload = await auth_utils.decode_jwt(token_credentials)

    username = payload.get("username")
    user = await user_repo.get_user_by_username(username)

    if not user:
        raise InvalidTokenException

    return user

