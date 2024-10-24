from pathlib import Path

from fastapi_mail import (
    FastMail,
    ConnectionConfig,
    MessageSchema
)

from auth.core.config import settings
from auth.core.config import setup_logging

setup_logging()

Base_DIR = Path(__file__).resolve().parent.parent.parent

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.mail.mail_username,
    MAIL_PASSWORD=settings.mail.mail_password,
    MAIL_FROM=settings.mail.mail_from,
    MAIL_PORT=settings.mail.mail_port,
    MAIL_SERVER=settings.mail.mail_server,
    MAIL_FROM_NAME=settings.mail.mail_from_name,
    MAIL_STARTTLS=settings.mail.mail_starttls,
    MAIL_SSL_TLS=settings.mail.mail_ssl_tls,
    USE_CREDENTIALS=settings.mail.mail_use_credentials,
    VALIDATE_CERTS=settings.mail.mail_validate_certs,

    TEMPLATE_FOLDER=Path(Base_DIR, 'templates')
)

mail = FastMail(
    config=mail_config
)


async def create_message(recipients: list[str], subject: str, body: str):
    message = MessageSchema(
        recipients=recipients,
        subject=subject,
        body=body,
        subtype="html"
    )
    return message
