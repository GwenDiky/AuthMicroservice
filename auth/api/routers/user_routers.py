from fastapi import APIRouter, Depends, Form
from exceptions import (
    AuthFailedException,
    InactiveUserException,
    SignUpFailedException,
    InvalidTokenException,
    AuthTokenExpiredException,
    BadRequestException
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from auth.schemas.user import UserSchema, UserCreateSchema
from auth.schemas.token import TokenSchema
from fastapi.security import (
    HTTPBearer,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes
)
from auth.core.utils import (
    utils_jwt as auth_utils,
    utils_users as user_utils
)
from auth.database.user import User
from sqlalchemy.orm import Session
import bcrypt
import logging
from auth.core.config import setup_logging
from auth.database.user_repo import UserRepository
from auth.api.dependecies import get_current_auth_user, get_info_of_user_by_token
from auth.core.security import hash_password
from auth.core.settings import settings
import jwt
from jwt import PyJWTError
from auth.core.utils.utils_jwt import (
    decode_jwt,
    encode_jwt
)

setup_logging()

user_router = APIRouter()
http_bearer = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")
TOKEN_TYPE = "Bearer"


@user_router.post("/signup")
async def signup(user: UserCreateSchema, db: AsyncSession = Depends(UserRepository().get_db)):
    hashed_password = await hash_password(user.password)

    user_data = user.model_dump()
    user_data['password'] = hashed_password

    new_user = User(**user_data)
    user_repository = UserRepository(db)
    try:
        result = await user_repository.add_new_user(new_user)
    except SignUpFailedException:
        logging.error("User creation failed")
        raise SignUpFailedException

    return result


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


@user_router.post("/login", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await UserRepository().get_user_by_username(form_data.username)
    if not user:
        raise AuthFailedException

    await compare_passwords(form_data.password, user.password)

    if not user.is_active:
        raise InactiveUserException

    jwt_payload = {
        "sub": user.id,
        "username": user.username,
        "email": user.email,
    }

    token = jwt.encode(jwt_payload, settings.jwt.jwt_secret, algorithm=settings.jwt.jwt_algorithm)
    return TokenSchema(
        access_token=token,
        token_type=TOKEN_TYPE
    )


@user_router.get("/me", response_model=UserCreateSchema)
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserCreateSchema:
    try:
        payload = jwt.decode(token, settings.jwt.jwt_secret, algorithms=[settings.jwt.jwt_algorithm])
        username = payload.get("username")

        if username is None:
            raise AuthFailedException

        user = await UserRepository().get_user_by_username(username)

        if not user:
            raise AuthFailedException

        return user

    except PyJWTError:
        raise AuthFailedException


@user_router.post("/refresh-token", response_model=TokenSchema)
async def refresh_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token,  settings.jwt.jwt_secret, algorithms=[settings.jwt.jwt_algorithm])
        username: str = payload.get("username")
        if username is None:
            raise AuthFailedException

        user = await UserRepository().get_user_by_username(username)
        if not user:
            raise AuthFailedException

        new_token = jwt.encode({"sub": user.id, "username": user.username}, settings.jwt.jwt_secret, algorithm=settings.jwt.jwt_algorithm)
        return TokenSchema(
            access_token=new_token,
            token_type=TOKEN_TYPE
        )
    except PyJWTError:
        raise AuthFailedException


@user_router.post("/get-info-of-user-by-token")
async def get_info_by_token(user: UserSchema = Depends(get_info_of_user_by_token)):
    return user


@user_router.post("/logout")
async def logout():
    ...


@user_router.put("/change-password")
async def change_password():
    ...


@user_router.post("/forgot-password")
async def forgot_password():
    ...


@user_router.delete("/me/delete")
async def delete_me():
    ...