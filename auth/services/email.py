from pathlib import Path

from fastapi_mail import FastMail, ConnectionConfig, MessageSchema

from auth.core.config import settings
from auth.core.config import setup_logging
import logging
import aioboto3

setup_logging()

Base_DIR = Path(__file__).resolve().parent.parent.parent


async def is_email_verified(email: str) -> bool:
    async with aioboto3.Session().client(
        "ses",
        aws_access_key_id=settings.mail.aws_access_key_id,
        aws_secret_access_key=settings.mail.aws_secret_access_key,
        region_name=settings.mail.aws_default_region,
        endpoint_url=settings.mail.localstack_endpoint,
    ) as ses:
        response = await ses.get_identity_verification_attributes(Identities=[email])
        verification_status = (
            response["VerificationAttributes"].get(email, {}).get("VerificationStatus")
        )
        return verification_status == "Success"


async def verify_email(email):
    async with aioboto3.Session().client(
        "ses",
        aws_access_key_id=settings.mail.aws_access_key_id,
        aws_secret_access_key=settings.mail.aws_secret_access_key,
        region_name=settings.mail.aws_default_region,
        endpoint_url=settings.mail.localstack_endpoint,
    ) as ses:
        try:
            response = await ses.verify_email_identity(EmailAddress=email)
            logging.info(f"Verification initiated for {email}: {response}")
        except Exception as e:
            logging.error(f"Failed to verify email: {e}")


async def send_email(recipients: list, subject: str, body: str, html_body: str) -> None:
    async with aioboto3.Session().client(
        "ses",
        region_name=settings.mail.aws_default_region,
        endpoint_url=settings.mail.localstack_endpoint,
        aws_access_key_id=settings.mail.aws_access_key_id,
        aws_secret_access_key=settings.mail.aws_secret_access_key,
    ) as ses:
        try:
            await verify_email(settings.mail.mail_from)
            response = await ses.send_email(
                Source=settings.mail.mail_from,
                Destination={"ToAddresses": recipients},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Text": {"Data": body, "Charset": "UTF-8"},
                        "Html": {"Data": html_body, "Charset": "UTF-8"},
                    },
                },
            )
            logging.info(f"Email sent! Message ID: {response['MessageId']}")
        except Exception as e:
            logging.error(f"Failed to send email: {e}")


async def create_message(recipients: list[str], subject: str, body: str):
    message = MessageSchema(
        recipients=recipients, subject=subject, body=body, subtype="html"
    )
    return message
