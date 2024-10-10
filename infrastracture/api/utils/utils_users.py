from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
)
from fastapi import (
    Depends,
    Security
)
from auth.domain.entities.user import UserSchema
from . import utils_jwt as auth_utils
from fastapi import (
    HTTPException,
    status,
    Header
)
from jwt import InvalidTokenError
import logging
import os
from dotenv import load_dotenv
from ...security.config import access_security
from fastapi_jwt import (
    JwtAccessBearer,
    JwtAuthorizationCredentials
)

load_dotenv()

logging.basicConfig(level=logging.INFO)


async def get_current_user(credentials: JwtAuthorizationCredentials = Security(access_security)):
    return credentials.subject
