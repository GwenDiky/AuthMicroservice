from datetime import timedelta, datetime
import jwt
import time
from typing import Dict
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()


async def token_response(token: str):
    return {
        "access_token": token
    }


async def encode_jwt(
        payload: dict,
        algorithm: str = os.getenv("JWT_ALGORITHM"),
        secret: str = os.getenv("JWT_SECRET"),
        expire: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")),
        expire_timedelta: timedelta | None = None
) -> Dict[str, str]:
    to_encode = payload.copy()
    now = datetime.now()

    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutus=expire)

    to_encode.update(
        exp=expire,
        iat=now,
    )
    token = jwt.encode(to_encode, secret, algorithm=[algorithm])
    return await token_response(token)


async def decode_jwt(
        token: str,
        algorithm: str = os.getenv("JWT_ALGORITHM"),
        secret: str = os.getenv("JWT_SECRET"),
) -> dict:
    try:
        decoded_token = jwt.decode(token, secret, algorithms=[algorithm])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception as e:
        return {"error": e}


async def hash_password(
        password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


async def validate_password(
        password: str,
        hashed_password: bytes
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password
    )
