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
from . import utils_jwt as auth_utils
from fastapi import (
    HTTPException,
    status,
    Header
)
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
