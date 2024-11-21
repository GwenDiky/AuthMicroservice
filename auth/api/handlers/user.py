import logging

import jwt
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession
from auth.api import dependecies
from auth.core.config import settings, setup_logging
from auth import exceptions
from auth.models.core import get_async_session
from auth.models.user_model import User
from auth.schemas import user, token_schema, paginator_schema, email_schema
from auth.services.email import is_email_verified, verify_email
from auth.services.user import UserRepository
from auth.utils import (utils_mail, utils_users, utils_jwt, redis_client as
    redis_utils)

setup_logging()

user_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")
TOKEN_TYPE = "Bearer"


@user_router.post("/signup")
async def signup(
        user: user.UserCreateSchema, db: AsyncSession = Depends(get_async_session)
) -> user.UserInDBSchema:
    user.password = await utils_users.hash_password(user.password)

    await verify_email(user.email)

    new_user = User(**user.model_dump())
    try:
        result = await UserRepository(db).add_new_user(new_user)
        await utils_mail.create_user_send_message(user.email)

    except exceptions.SignUpFailedException:
        logging.error("User creation failed")
        raise exceptions.SignUpFailedException

    return result


@user_router.post("/resend_verification")
async def resend_verification(
        email: str, db: AsyncSession = Depends(get_async_session)
):
    user = await UserRepository(db).get_user_by_email(email)
    if not user:
        raise exceptions.AuthFailedException

    if user.is_verified:
        raise exceptions.UserAlreadyVerifiedException

    await verify_email(email=email)

    if not await is_email_verified(email):
        raise exceptions.MailNotVerifiedException

    await utils_mail.create_user_send_message(email)
    return email_schema.EmailResponseSchema(
        message="Verification email resend successfully",
    )


@user_router.post("/login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_async_session),
) -> token_schema.TokenSchema:
    user = await UserRepository(db).get_user_by_username(form_data.username)
    if not user:
        raise exceptions.AuthFailedException

    await utils_users.compare_passwords(form_data.password, user.password)

    jwt_payload = {
        "sub": user.id,
        "username": user.username,
        "email": user.email,
    }

    token = await utils_jwt.encode_jwt(jwt_payload)
    return token_schema.TokenSchema(access_token=token, token_type=TOKEN_TYPE)


@user_router.get("/me", response_model=user.UserCreateSchema)
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_async_session),
        redis_client=Depends(redis_utils.get_redis),
) -> user.UserCreateSchema:
    if await redis_utils.is_token_blacklisted(token, redis_client):
        logging.info("Token is blacklisted")
        raise exceptions.InvalidTokenException
    return await dependecies.get_current_auth_user(token, db)


@user_router.post("/refresh-token", response_model=token_schema.TokenSchema)
async def refresh_token(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_async_session),
        redis_client=Depends(redis_utils.get_redis),
) -> token_schema.TokenSchema:
    try:
        if await redis_utils.is_token_blacklisted(token, redis_client):
            logging.info("Token is blacklisted")
            raise exceptions.InvalidTokenException

        user = await dependecies.get_current_auth_user(token, db)
        new_token = jwt.encode(
            {"sub": user.id, "username": user.username},
            settings.jwt.jwt_secret,
            algorithm=settings.jwt.jwt_algorithm,
        )
        return token_schema.TokenSchema(access_token=new_token,
                                  token_type=TOKEN_TYPE)
    except PyJWTError:
        raise exceptions.AuthFailedException


@user_router.post("/get-info-of-user-by-token")
async def get_info_by_token(
        token: token_schema.TokenSchema, db: AsyncSession = Depends(
            get_async_session)
) -> user.UserInDBSchema:
    return await dependecies.get_info_of_user_by_token(token, db)


@user_router.post("/logout")
async def logout(
        token: str = Depends(oauth2_scheme), redis_client=Depends(redis_utils.get_redis)
) -> user.UserMessageSchema:
    logging.info(f"Current token: {token}")

    if not token:
        logging.error("Token wasn't provided")
        raise exceptions.InvalidTokenException

    if await redis_utils.is_token_blacklisted(token, redis_client):
        raise exceptions.InvalidTokenException

    payload = await utils_jwt.decode_jwt(token)
    user_id = payload.get("sub")
    if not user_id:
        raise exceptions.InvalidTokenException

    await redis_utils.add_token_to_blacklist(token, redis_client)
    return user.UserMessageSchema(message="Successfully logged out")


@user_router.put("/change-password")
async def change_password(
        new_password: str,
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_async_session),
        redis_client=Depends(redis_utils.get_redis),
) -> user.UserInDBSchema:
    if await redis_utils.is_token_blacklisted(token, redis_client):
        logging.info("Token is blacklisted")
        raise exceptions.InvalidTokenException

    user = await dependecies.get_current_auth_user(token, db)
    hashed_password = await utils_users.hash_password(new_password)

    try:
        result = await UserRepository(db).change_password_of_current_user(
            user.id, hashed_password
        )
        if not result:
            raise exceptions.PasswordNotChangedException

        return result

    except PyJWTError:
        raise exceptions.AuthFailedException


@user_router.put("/me/update-profile")
async def update_profile_of_current_user(
        user: user.UserUpdateSchema,
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_async_session),
):
    user_data = user.model_dump()
    user_in_db = await dependecies.get_current_auth_user(token, db)

    try:
        result = await UserRepository(db).update_profile_of_current_user(
            user_in_db.id, user_data
        )
        if not result:
            raise exceptions.ProfileNotChangedException
        logging.info("Profile was changed successfully")
        return result

    except PyJWTError:
        raise exceptions.AuthFailedException


@user_router.get("/verify/{token}")
async def verify_user_account(
        token: str, db: AsyncSession = Depends(get_async_session)
):
    token_data = await utils_mail.decode_url_safe_token(token)
    user_email = token_data.email

    user = await UserRepository(db).get_user_by_email(user_email)
    if not user:
        raise exceptions.UserNotFoundException

    await UserRepository(db).update_status_of_email_verification(
        user, {"is_verified": True}
    )
    return email_schema.EmailResponseSchema(
        f"U'r account '{user.username}' verified " f"successfully!"
    )


@user_router.get("/reset-password/verify/{token}/{password_hash}")
async def verify_user_account_password_forgot(
        token: str, password_hash: str,
        db: AsyncSession = Depends(get_async_session)
):
    token_data = await utils_mail.decode_url_safe_token(token)
    user_email = token_data.get("email")

    user = await UserRepository(db).get_user_by_email(user_email)
    if not user:
        raise exceptions.UserNotFoundException
    await UserRepository(db).change_password_of_current_user(user.id,
                                                             password_hash)

    return user.UserMessageSchema(
        f"Password was changed successfully for " f"current user! {token_data}"
    )


@user_router.post("/forgot-password")
async def forgot_password(email: str, new_password: str) -> email_schema.EmailResponseSchema:
    password_hash = await utils_users.hash_password(new_password)
    await utils_mail.forgot_password_send_message(email, password_hash)
    return email_schema.EmailResponseSchema(
        message=f"Check up u'r mail: {email}"
    )


@user_router.delete("/me/delete")
async def delete_me(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_async_session)
) -> dict:
    user = await dependecies.get_current_auth_user(token, db)

    try:
        result = await UserRepository(db).delete_user(user.id)
        return result
    except PyJWTError:
        raise exceptions.AuthFailedException


@user_router.get(
    "/users", response_model=paginator_schema.PaginationSchema,
response_model_exclude_none=True
)
async def show_users(
        paginator: paginator_schema.Paginator = Depends(),
        db: AsyncSession = Depends(get_async_session),
):
    user_schema, total_records = await (UserRepository(db)
    .get_users_with_pagination(
        paginator))

    total_pages = (total_records // paginator.limit) + (
        1 if total_records % paginator.limit != 0 else 0)

    return paginator_schema.PaginationSchema(
        page_number=paginator.page,
        page_size=paginator.limit,
        total_pages=total_pages,
        total_records=total_records,
        content=user_schema,
    )
