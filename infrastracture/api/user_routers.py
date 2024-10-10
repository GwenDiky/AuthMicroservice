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
from ..security.config import user_repo, setup_logging

setup_logging()

user_router = APIRouter()
http_bearer = HTTPBearer()


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
async def get_current_user(user: UserSchema = Depends(user_utils.get_current_auth_user)):
    return user


@user_router.post("/refresh-token", response_model=Token)
async def refresh_token(
        token: Token = Depends(user_utils.refresh_token_of_current_user)
):
    return token


@user_router.post("/get-info-of-user-by-token")
async def get_info_by_token(user: UserSchema = Depends(user_utils.get_info_of_user_by_token)):
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
