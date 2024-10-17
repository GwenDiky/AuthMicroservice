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
    PasswordNotChangedException, InvalidTokenException
)
from auth.schemas.token import TokenSchema
from auth.schemas.user import UserCreateSchema, UserInDBSchema
from auth.core.utils.redis_client import add_token_to_blacklist, is_token_blacklisted, get_redis

setup_logging()

user_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")
TOKEN_TYPE = "Bearer"

@user_router.post("/signup")
async def signup(user: UserCreateSchema,
                 db: AsyncSession = Depends(get_async_session))\
        -> UserInDBSchema:
    hashed_password = await hash_password(user.password)

    user_data = user.model_dump()
    user_data['password'] = hashed_password

    new_user = User(**user_data)
    try:
        result = await UserRepository(db).add_new_user(new_user)
    except SignUpFailedException:
        logging.error("User creation failed")
        raise SignUpFailedException

    return result


@user_router.post("/login", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_async_session)) \
        -> TokenSchema:
    user = await UserRepository(db).get_user_by_username(form_data.username)
    if not user:
        raise AuthFailedException

    await compare_passwords(form_data.password, user.password)

    jwt_payload = {
        "sub": user.id,
        "username": user.username,
        "email": user.email,
    }

    token = await encode_jwt(jwt_payload)
    return TokenSchema(
        access_token=token,
        token_type=TOKEN_TYPE
    )


@user_router.get("/me", response_model=UserCreateSchema)
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_session)) \
        -> UserCreateSchema:
    return await get_current_auth_user(token, db)


@user_router.post("/refresh-token", response_model=TokenSchema)
async def refresh_token(token: str = Depends(oauth2_scheme),
                        db: AsyncSession = Depends(get_async_session)) \
        -> TokenSchema:
    try:
        user = await get_current_auth_user(token, db)
        new_token = jwt.encode({"sub": user.id, "username": user.username}, settings.jwt.jwt_secret, algorithm=settings.jwt.jwt_algorithm)
        return TokenSchema(
            access_token=new_token,
            token_type=TOKEN_TYPE
        )
    except PyJWTError:
        raise AuthFailedException


@user_router.post("/get-info-of-user-by-token")
async def get_info_by_token(token: TokenSchema, db: AsyncSession = Depends(get_async_session)) -> UserInDBSchema:
    return await get_info_of_user_by_token(token, db)


@user_router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme),
                 redis_client=Depends(get_redis)) -> dict:
    logging.info(f"Current token: {token}")

    if not token:
        logging.error("Token wasn't provided")
        raise InvalidTokenException

    await add_token_to_blacklist(token, redis_client)
    return {"message": "Successfully logged out"}


@user_router.put("/change-password")
async def change_password(new_password: str, token: str = Depends(oauth2_scheme),
                          db: AsyncSession = Depends(get_async_session)) -> UserInDBSchema:
    user = await get_current_auth_user(token, db)
    hashed_password = await hash_password(new_password)

    try:
        result = await UserRepository(db).change_password_of_current_user(user.id, hashed_password)
        if not result:
            raise PasswordNotChangedException

        return result

    except PyJWTError:
        raise AuthFailedException


@user_router.post("/forgot-password")
async def forgot_password():
    ...


@user_router.delete("/me/delete")
async def delete_me(token: str = Depends(oauth2_scheme),
                    db: AsyncSession = Depends(get_async_session)) -> (
        dict):
    user = await get_current_auth_user(token, db)

    try:
        result = await UserRepository(db).delete_user(user.id)
        return result
    except PyJWTError:
        raise AuthFailedException