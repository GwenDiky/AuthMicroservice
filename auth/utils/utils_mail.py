import logging

from itsdangerous import URLSafeTimedSerializer

from auth.core.config import settings, templates
from auth.exceptions import InvalidTokenException
from auth.services.email import send_email
from auth.core.config import setup_logging

from auth.schemas.token import TokenDataSchema

import logging

setup_logging()

serializer = URLSafeTimedSerializer(
    secret_key=settings.jwt.jwt_secret,
    salt="email-configuration",
)


async def create_url_safe_token(data: dict):
    token = serializer.dumps(data)
    return token


async def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token)
        validated_data = TokenDataSchema(
            sub=token_data.get('sub'),
            username=token_data.get('username'),
            email=token_data.get('email'),
            exp=datetime.fromtimestamp(token_data.get('exp')),
            iat=datetime.fromtimestamp(token_data.get('iat'))
        )
        return validated_data
    except InvalidTokenException:
        logging.error("Token decode was failed")


async def forgot_password_send_message(email: str, password_hash: str) -> None:
    token = await create_url_safe_token({"email": email})
    link = f"http://{settings.domain}/api/user/reset-password/verify/{token}/{password_hash}"

    html_body = templates.get_template("forgot-password.html").render(link=link)

    await send_email(
        recipients=[email],
        subject="Verify your email",
        body="Verify your email",
        html_body=html_body,
    )


async def create_user_send_message(email: str) -> None:
    token = await create_url_safe_token({"email": email})
    link = f"http://{settings.domain}/api/user/verify/{token}"
    html_body = templates.get_template("verify-email.html").render(link=link)
    await send_email(
        recipients=[email],
        subject="Verification Email",
        body="Verify your email",
        html_body=html_body,
    )
