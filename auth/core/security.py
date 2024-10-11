from datetime import timedelta, datetime
import jwt
import time
from typing import Dict
import os
from dotenv import load_dotenv
import bcrypt
from infrastracture.exceptions import InvalidTokenException

load_dotenv()


async def hash_password(
        password: str | bytes,
) -> str:
    if isinstance(password, bytes):
        password = password.decode('utf-8')

    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()

    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')


async def validate_password(
        password: str,
        hashed_password: bytes
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password
    )
