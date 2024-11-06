import logging

from itsdangerous import URLSafeTimedSerializer

from auth.core.config import settings
from auth.exceptions import InvalidTokenException
from auth.core.config import templates
from auth.services.email import send_email
import boto3


serializer = URLSafeTimedSerializer(
    secret_key=settings.jwt.jwt_secret,
    salt="email-configuration",
)


async def create_urL_safe_token(data: dict):
    token = serializer.dumps(data)
    return token


async def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token)
        return token_data
    except InvalidTokenException:
        logging.error("Token decode was failed")


async def forgot_password_send_message(email: str, new_password: str) -> None:
    token = await create_urL_safe_token({"email": email})
    link = f"http://{settings.domain}/api/user/reset-password/verify/{token}/{new_password}"
    html_body = templates.get_template("forgot-password.html").render(link=link)
    await send_email(
        recipients=[email],
        subject="Verify your email",
        body="Verify your email",
        html_body=html_body,
    )


async def create_user_send_message(email: str) -> None:
    token = await create_urL_safe_token({"email": email})
    link = f"http://{settings.domain}/api/user/verify/{token}"
    html_body = templates.get_template("verify-email.html").render(link=link)
    await send_email(
        recipients=[email],
        subject="Verification Email",
        body="Verify your email",
        html_body=html_body,
    )
