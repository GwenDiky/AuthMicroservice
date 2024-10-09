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
from ...security.settings import access_security
from fastapi_jwt import (
    JwtAccessBearer,
    JwtAuthorizationCredentials
)

load_dotenv()

logging.basicConfig(level=logging.INFO)

# http_bearer = HTTPBearer()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

# def get_current_token_payload(
#         token: str = Depends(oauth2_scheme),
# ):
#     try:
#         payload = auth_utils.decode_jwt(
#             token=token
#         )
#
#     except InvalidTokenError as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="invalid token error"
#         )
#     return payload


async def get_current_user(credentials: JwtAuthorizationCredentials = Security(access_security)):
    return credentials.subject

# async def get_current_user(Authorization: str = Header(...)):
#     try:
#         token = Authorization.split(" ")[1]
#         # payload = jwt.decode(token, os.getenv("JWT_SECRET"),
#         #                      algorithms=[os.getenv("JWT_ALGORITHM")])
#         # return payload
#         return token
#         # return User(id=payload["id"], username=payload["username"], email=payload["email"])
#         #payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM")])
#         # print("payload:", jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM")]))
#         # user_id = payload.get("id")
#         # if user_id is None:
#         #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
#         # return User(id=user_id, username=payload.get("username"), email=payload.get("email"),
#         #             created_at=payload.get("created_at"), date_of_birth=payload.get("date_of_birth"),
#         #             phone=payload.get("phone"))
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# def get_current_auth_user(payload: dict = Depends(get_current_token_payload)) -> UserSchema:
#     username: str | None = payload.get("sub")
#     if not (user := user_db.get(username)):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="token invalid user not found"
#         )
