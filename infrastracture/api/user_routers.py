""""
сбросить/изменить пароль
"""
from fastapi import APIRouter, Depends, Form, HTTPException, status
from auth.domain.entities.user import UserSchema
from auth.domain.entities.token import Token
from fastapi.security import HTTPBearer
from .utils import (
    utils_jwt as auth_utils,
    utils_users as user_utils
)
from datetime import date
from uuid import uuid4

user_router = APIRouter()
http_bearer = HTTPBearer()


@user_router.post("/signup")
async def signup():
    hashed_password = await auth_utils.hash_password("qwerty")
    user = UserSchema(
        id=uuid4(),
        username="John",
        password=hashed_password,
        phone="+375292188397",
        email="johnexample@gmail.com",
        created_at=date.today(),  # Use the current date
        date_of_birth=date(1990, 1, 1),
    )
    return {"message": "User created", "user": user}


def validate_auth_user_login(
        username: str = Form(),
        password: str = Form()
):
    # unauthed_exc = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Invalid username or password",
    # )
    # # if not (user := users_db.get(username)):
    # #     raise unauthed_exc
    # if not auth_utils.validate_password(
    #         password=password,
    #         hashed_password=user.password
    # ):
    #     return unauthed_exc
    # if not user.active:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="user unactive",
    #     )
    #
    # raise user
    ...


@user_router.post("/login", response_model=Token)
async def login(
        user: UserSchema = Depends(validate_auth_user_login),
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


@user_router.get("/me")
async def get_current_user(user: UserSchema = Depends(user_utils.get_current_auth_user)):
    # if user.active:
    #     return user
    # raise HTTPException(
    #     status_code=status.HTTP_403_FORBIDDEN,
    #     detail="user unactive",
    # )
    return user

    ...
    # try:
    #     payload = decodeJWT(token)
    #     username: str = payload.get("sub")
    #     if username is None:
    #         return None
    # except JWTError:
    #     return None
    # user = USERS.get(username)
    # if user is None:
    #     return None
    # return user
