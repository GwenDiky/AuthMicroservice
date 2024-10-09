from fastapi_jwt import (
    JwtAccessBearer,
    JwtAuthorizationCredentials
)
import os

access_security = JwtAccessBearer(secret_key=os.getenv("JWT_SECRET"))
