import logging

import jwt
from fastapi import APIRouter, Depends
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)
from jwt import PyJWTError

from auth.api.dependecies import get_current_auth_user
from auth.api.dependecies import get_info_of_user_by_token
from auth.core.config import setup_logging
from auth.core.security import hash_password
from auth.core.settings import settings
from auth.core.utils.utils_jwt import (
    decode_jwt,
    encode_jwt, token_response
)
from auth.core.utils.utils_users import compare_passwords
from auth.database.user import User
from auth.database.user_repo import UserRepository, get_user_repo
from auth.schemas.token import TokenSchema
from auth.schemas.user import UserSchema, UserCreateSchema, UserSignUpSchema
from exceptions import (
    AuthFailedException,
    SignUpFailedException
)
from sqlalchemy.ext.asyncio import create_async_engine
from auth.core.settings import settings

setup_logging()

user_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")
TOKEN_TYPE = "Bearer"

@user_router.post("/signup")
async def signup(user: UserCreateSchema,
                 user_repo: UserRepository = Depends(get_user_repo)):
    hashed_password = await hash_password(user.password)

    user_data = user.model_dump()
    user_data['password'] = hashed_password

    new_user = User(**user_data)
    try:
        result = await user_repo.add_new_user(new_user)
    except SignUpFailedException:
        logging.error("User creation failed")
        raise SignUpFailedException

    return result


@user_router.post("/login", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                user_repo: UserRepository = Depends(get_user_repo)) \
        -> TokenSchema:
    user = await user_repo.get_user_by_username(form_data.username)
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
async def get_current_user(token: str = Depends(oauth2_scheme)) \
        -> UserCreateSchema:
    try:
        payload = await decode_jwt(token)
        user = await get_current_auth_user(payload)
        return user

    except PyJWTError:
        raise AuthFailedException


@user_router.post("/refresh-token", response_model=TokenSchema)
async def refresh_token(token: str = Depends(oauth2_scheme)) \
        -> TokenSchema:
    try:
        payload = await decode_jwt(token)
        user = await get_current_auth_user(payload)

        new_token = jwt.encode({"sub": user.id, "username": user.username}, settings.jwt.jwt_secret, algorithm=settings.jwt.jwt_algorithm)
        return TokenSchema(
            access_token=new_token,
            token_type=TOKEN_TYPE
        )
    except PyJWTError:
        raise AuthFailedException

@user_router.get('/get-token-of-current-user')
async def get_token(token: str = Depends(oauth2_scheme)) \
        -> TokenSchema:
    return TokenSchema(
        access_token = token,
        token_type = "Bearer"
    )

@user_router.post("/get-info-of-user-by-token")
async def get_info_by_token(user: UserSchema = Depends(get_info_of_user_by_token)) -> UserSchema:
    return user


@user_router.post("/logout")
async def logout():
    ...


@user_router.put("/change-password")
async def change_password(new_password: str, token: str = Depends(oauth2_scheme),
                          user_repo: UserRepository = Depends(get_user_repo)):
    payload = await decode_jwt(token)
    user = await get_current_auth_user(payload)
    hashed_password = await hash_password(new_password)

    try:
        result = await user_repo.change_password_of_current_user(user.id, hashed_password)
        return result

    except PyJWTError:
        raise AuthFailedException
    except Exception as e:
        logging.error(f"Error during password change: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@user_router.post("/forgot-password")
async def forgot_password():
    ...


@user_router.delete("/me/delete")
async def delete_me(token: str = Depends(oauth2_scheme),
                    user_repo: UserRepository = Depends(get_user_repo)) -> (
        dict):
    payload = await decode_jwt(token)
    user = await get_current_auth_user(payload)

    try:
        result = await user_repo.delete_user(user.id)
        return result
    except PyJWTError:
        raise AuthFailedException