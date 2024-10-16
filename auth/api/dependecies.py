from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.core.config import setup_logging
from auth.core.utils.utils_jwt import decode_jwt
from auth.database.user_repo import UserRepository
from auth.exceptions import InvalidTokenException
from auth.schemas.token import TokenSchema
from auth.schemas.user import UserCreateSchema
from auth.schemas.user import UserInDBSchema

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


async def get_current_auth_user(token: str, db: AsyncSession) -> UserCreateSchema:
    try:
        payload = await decode_jwt(token)
        username = payload.get('username')
        if username is None:
            raise AuthFailedException

        user = await UserRepository(db).get_user_by_username(username)

        if not user:
            raise AuthFailedException

        return user
    except PyJWTError:
        raise AuthFailedException



async def get_info_of_user_by_token(token: TokenSchema, db: AsyncSession) \
        -> UserInDBSchema:
    token_credentials = token.access_token
    payload = await decode_jwt(token_credentials)

    username = payload.get("username")
    user = await UserRepository(db).get_user_by_username(username)

    if not user:
        raise InvalidTokenException

    return user
