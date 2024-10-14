import logging

import jwt
from fastapi import Depends, Form
from fastapi.security import (
    HTTPAuthorizationCredentials,
)

from auth.core.config import http_bearer, user_repo, setup_logging
from auth.core.utils import utils_jwt as auth_utils
from auth.schemas.token import TokenSchema
from auth.schemas.user import UserSchema
from exceptions import InvalidTokenException

setup_logging()

class PermissionChecker:
    def __init__(self, permission: str):
        self.permission = permission

    # def __call__(self, user_id=Depends(get_user_id)):
    #     has_permission = ...
    #
    #     if not has_permission:
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail='Insufficient permissions'
    #         )

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


async def validate_auth_user_login(
        username: str = Form(),
        password: str = Form(),
):
    if not (await UserRepository().get_user_by_username(username)):
        raise AuthFailedException
    else:
        user = await UserRepository().get_user_by_username(username)

    await compare_passwords(password, user.password)

    return user
