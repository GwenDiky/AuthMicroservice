import logging

from itsdangerous import URLSafeTimedSerializer

from auth.core.config import settings
from auth.exceptions import InvalidTokenException

serializer = URLSafeTimedSerializer(
    secret_key=settings.jwt.jwt_secret,
    salt="email-configuration",
)


async def create_urL_safe_token(
        data: dict
):
    token = serializer.dumps(data)
    return token


async def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token)

        return token_data
    except InvalidTokenException:
        logging.error("Token decode was failed")
