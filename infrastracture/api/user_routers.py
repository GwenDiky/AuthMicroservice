import os
from fastapi import APIRouter, Depends, Form
from ..exceptions import (
    AuthFailedException,
    InactiveUserException,
    SignUpFailedException,
    InvalidTokenException,
    AuthTokenExpiredException,
    BadRequestException
)
from sqlalchemy.exc import SQLAlchemyError
from auth.domain.entities.user import UserSchema, UserCreate
from auth.domain.entities.token import Token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .utils import (
    utils_jwt as auth_utils,
    utils_users as user_utils
)
from pydantic_extra_types.phone_numbers import PhoneNumber
from infrastracture.database.postgres_repo import UserRepository
from infrastracture.database.models.user import User
from datetime import date
from uuid import uuid4
from sqlalchemy.orm import Session
from auth.domain.entities.user import UserRole
import bcrypt
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
import jwt
import logging


logging.basicConfig(level=logging.INFO)

user_router = APIRouter()
http_bearer = HTTPBearer()

user_repo = UserRepository()


@user_router.post("/signup")
async def signup(user: UserCreate, db: Session = Depends(user_repo.get_db)):
    hashed_password = await auth_utils.hash_password(user.password)

    new_user = User(
        username=user.username,
        password=str(hashed_password),
        is_active=True,
        email=user.email,
        phone_number=user.phone,
        date_of_birth=user.date_of_birth,
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except SQLAlchemyError as db_error:
        await db.rollback()
        logging.error(f"Error occurred: {db_error}")
        raise SignUpFailedException
    return {"message": "User created", "user": new_user}


async def compare_passwords(password, hashed_password):
    if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        raise AuthFailedException
    return True


async def validate_auth_user_login(
        username: str = Form(),
        password: str = Form(),
):
    if not (await user_repo.get_user_by_username(username)):
        raise AuthFailedException
    else:
        user = await user_repo.get_user_by_username(username)

    await compare_passwords(password, user.password)

    return user


@user_router.post("/login", response_model=Token)
async def login(
        user: UserSchema = Depends(validate_auth_user_login),
):
    if not user.is_active:
        raise InactiveUserException

    jwt_payload = {
        "sub": user.id,
        "id": user.id,
        "username": user.username,
        "email": user.email if user.email else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
        "phone": user.phone_number if user.phone_number else None
    }
    token = await auth_utils.encode_jwt(jwt_payload)
    return Token(
        access_token=token,
        token_type="Bearer"
    )


@user_router.get("/me")
async def get_current_user(token: HTTPAuthorizationCredentials = Depends(http_bearer)):
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


@user_router.post("/refresh-token", response_model=Token)
async def refresh_token(
        user: UserSchema = Depends(validate_auth_user_login)
):
    jwt_payload = {
        "sub": user.id,
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": date.today(),
        "date_of_birth": user.date_of_birth,
        "phone": user.phone
    }
    token = auth_utils.encode_jwt(jwt_payload)
    return Token(
        access_token=token,
        token_type="Bearer"
    )


@user_router.post("/logout")
async def logout():
    ...


@user_router.put("/change-password")
async def change_password():
    ...


@user_router.post("/forgot-password")
async def forgot_password():
    ...
