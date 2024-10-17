import time
from datetime import timedelta, datetime
from typing import Dict

import jwt
from dotenv import load_dotenv

from auth.core.settings import settings
from auth.exceptions import InvalidTokenException

load_dotenv()


async def token_response(token: str):
    return {
        "access_token": token
    }

async def encode_jwt(
        payload: dict,
        algorithm: str = settings.jwt.jwt_algorithm,
        secret: str = settings.jwt.jwt_secret,
        expire: int = settings.jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None
) -> Dict[str, str]:
    to_encode = payload.copy()
    now = datetime.now()

    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire)

    to_encode.update(
        exp=expire,
        iat=int(time.time()),
    )
    token = jwt.encode(to_encode, secret, algorithm=algorithm)
    return token


async def decode_jwt(
        token: str,
        algorithm: str = settings.jwt.jwt_algorithm,
        secret: str = settings.jwt.jwt_secret,
) -> dict:
    try:
        decoded_token = jwt.decode(token, secret, algorithms=[algorithm])
        return decoded_token
    except jwt.InvalidTokenError:
        raise InvalidTokenException


