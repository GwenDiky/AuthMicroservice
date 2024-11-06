from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.core.config import setup_logging
from auth.utils.utils_jwt import decode_jwt
from auth.services.user import UserRepository
from auth.exceptions import InvalidTokenException
from auth.schemas.token import TokenSchema
from auth.schemas.user import UserCreateSchema
from auth.schemas.user import UserInDBSchema

setup_logging()


async def get_current_auth_user(token: str, db: AsyncSession) -> UserCreateSchema:
    try:
        payload = await decode_jwt(token)
        username = payload.get("username")
        if username is None:
            raise AuthFailedException

        user = await UserRepository(db).get_user_by_username(username)

        if not user:
            raise AuthFailedException

        return user
    except PyJWTError:
        raise AuthFailedException


async def get_info_of_user_by_token(
    token: TokenSchema, db: AsyncSession
) -> UserInDBSchema:
    token_credentials = token.access_token
    payload = await decode_jwt(token_credentials)

    username = payload.get("username")
    user = await UserRepository(db).get_user_by_username(username)

    if not user:
        raise InvalidTokenException

    return user
