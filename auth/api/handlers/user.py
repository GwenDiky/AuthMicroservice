import logging
from datetime import datetime

import jwt
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.api.dependecies import (
    get_current_auth_user,
    get_info_of_user_by_token
)
from auth.core.config import settings
from auth.core.config import setup_logging
from auth.core.config import templates
from auth.exceptions import (
    AuthFailedException,
    SignUpFailedException,
    PasswordNotChangedException,
    ProfileNotChangedException, InvalidTokenException
)
from auth.models.core import get_async_session
from auth.models.user_model import User
from auth.schemas.token import TokenSchema
from auth.schemas.user import UserCreateSchema, UserInDBSchema, UserUpdateSchema
from auth.services.email import mail, create_message
from auth.services.user import UserRepository
from auth.utils.redis_client import add_token_to_blacklist, is_token_blacklisted, get_redis
from auth.utils.utils_jwt import (
    encode_jwt
)
from auth.utils.utils_mail import (
    create_urL_safe_token,
    decode_url_safe_token,
    forgot_password_send_message
)
from auth.utils.utils_users import compare_passwords
from auth.utils.utils_users import hash_password

setup_logging()

user_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")
TOKEN_TYPE = "Bearer"


@user_router.post("/signup")
async def signup(user: UserCreateSchema,
                 db: AsyncSession = Depends(get_async_session)) \
        -> UserInDBSchema:
    hashed_password = await hash_password(user.password)

    user_data = user.model_dump()
    user_data['password'] = hashed_password

    email = user_data["email"]

    new_user = User(**user_data)
    try:
        result = await UserRepository(db).add_new_user(new_user)

        if isinstance(result.date_of_birth, datetime):
            result.date_of_birth = result.date_of_birth.date()

        token = await create_urL_safe_token(
            {"email": email}
        )
        link = f"http://{settings.domain}/api/user/verify/{token}"
        html_message = templates.get_template("verify-email.html").render(link=link)

        message = await create_message(
            recipients=[email],
            subject="Verify your email",
            body=html_message
        )

        await mail.send_message(message)
    except SignUpFailedException:
        logging.error("User creation failed")
        raise SignUpFailedException

    return result


@user_router.post("/resend_verification")
async def resend_verification(email: str, db: AsyncSession = Depends(get_async_session)):
    user = await UserRepository(db).get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="User is already verified")

    token = await create_urL_safe_token({"email": email})
    link = f"http://{settings.domain}/api/user/verify/{token}"

    html_message = templates.get_template("verify-email.html").render(link=link, username=user.username)

    message = await create_message(
        recipients=[email],
        subject="Verify your email",
        body=html_message
    )

    await mail.send_message(message)

    return {"message": "Verification email resent successfully"}


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
async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(get_async_session),
                           redis_client=Depends(get_redis)
                           ) \
        -> UserCreateSchema:
    if await is_token_blacklisted(token, redis_client):
        logging.info("Token is blacklisted")
        raise InvalidTokenException
    return await get_current_auth_user(token, db)


@user_router.post("/refresh-token", response_model=TokenSchema)
async def refresh_token(token: str = Depends(oauth2_scheme),
                        db: AsyncSession = Depends(get_async_session),
                        redis_client=Depends(get_redis)
                        ) \
        -> TokenSchema:
    try:
        if await is_token_blacklisted(token, redis_client):
            logging.info("Token is blacklisted")
            raise InvalidTokenException

        user = await get_current_auth_user(token, db)
        new_token = jwt.encode({"sub": user.id, "username": user.username}, settings.jwt.jwt_secret,
                               algorithm=settings.jwt.jwt_algorithm)
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
                          db: AsyncSession = Depends(get_async_session),
                          redis_client=Depends(get_redis)
                          ) -> UserInDBSchema:
    if await is_token_blacklisted(token, redis_client):
        logging.info("Token is blacklisted")
        raise InvalidTokenException

    user = await get_current_auth_user(token, db)
    hashed_password = await hash_password(new_password)

    try:
        result = await UserRepository(db).change_password_of_current_user(user.id, hashed_password)
        if not result:
            raise PasswordNotChangedException

        return result

    except PyJWTError:
        raise AuthFailedException


@user_router.put('/me/update-profile')
async def update_profile_of_current_user(user: UserUpdateSchema,
                                         token: str = Depends(oauth2_scheme),
                                         db: AsyncSession = Depends(get_async_session)
                                         ):
    user_data = user.model_dump()
    user_in_db = await get_current_auth_user(token, db)

    try:
        result = await UserRepository(db).update_profile_of_current_user(user_in_db.id, user_data)
        if not result:
            raise ProfileNotChangedException
        logging.info("Profile was changed successfully")
        return result

    except PyJWTError:
        raise AuthFailedException


@user_router.get('/verify/{token}')
async def verify_user_account(token: str,
                              db: AsyncSession = Depends(get_async_session)):
    token_data = await decode_url_safe_token(token)
    user_email = token_data.get('email')

    user = await UserRepository(db).get_user_by_email(user_email)
    if not user:
        raise UserNotFoundException

    await UserRepository(db).update_status_of_email_verification(user, {'is_verified': True})


@user_router.get('/reset-password/verify/{token}/{new_password}')
async def verify_user_account_password_forgot(token: str,
                                              new_password: str,
                                              db: AsyncSession = Depends(get_async_session)):
    token_data = await decode_url_safe_token(token)
    user_email = token_data.get('email')

    user = await UserRepository(db).get_user_by_email(user_email)
    if not user:
        raise UserNotFoundException

    hashed_password = await hash_password(new_password)
    await UserRepository(db).change_password_of_current_user(user.id, hashed_password)

    return {
        "new_password": user.password
    }


@user_router.post("/forgot-password")
async def forgot_password(email: str,
                          new_password: str) \
        -> dict:
    await forgot_password_send_message(email, new_password)
    return {
        "comments": f"Check up u'r mail: {email}"
    }


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
