from pathlib import Path

from fastapi_mail import (
    FastMail,
    ConnectionConfig,
    MessageSchema
)

from auth.core.config import settings
from auth.core.config import setup_logging
import boto3
from botocore.exceptions import ClientError
import logging

setup_logging()

Base_DIR = Path(__file__).resolve().parent.parent.parent

async def verify_email(email):
    client = boto3.client(
        'ses',
        aws_access_key_id=settings.mail.aws_access_key_id,
        aws_secret_access_key=settings.mail.aws_secret_access_key,
        region_name=settings.mail.aws_default_region,
        endpoint_url=settings.mail.localstack_endpoint
    )

    try:
        response = client.get_identity_verification_attributes(Identities=[email])
        verification_status = response['VerificationAttributes'].get(email, {}).get('VerificationStatus')

        if verification_status != 'Success':
            response = await client.verify_email_identity(EmailAddress=email)
            logging.info(f"Verification initiated for {email}: {response}")
        else:
            logging.info("Email already verified")

    except ClientError as e:
        logging.error(f"Failed to verify email: {e.response['Error']['Message']}")


async def send_email(recipients: list, subject: str, body: str) -> None:
    ses = boto3.client(
        'ses',
        region_name=settings.mail.aws_default_region,
        endpoint_url=settings.mail.localstack_endpoint,
        aws_access_key_id=settings.mail.aws_access_key_id,
        aws_secret_access_key=settings.mail.aws_secret_access_key,
    )

    try:
        await verify_email(settings.mail.mail_from)
        response = ses.send_email(
            Source=settings.mail.mail_from,
            Destination={'ToAddresses': recipients},
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': body,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        logging.info(f"Email sent! Message ID: {response['MessageId']}")
    except ClientError as e:
        logging.error(f"Failed to send email: {e}")
    finally:
        ses.close()


async def create_message(recipients: list[str], subject: str, body: str):
    message = MessageSchema(
        recipients=recipients,
        subject=subject,
        body=body,
        subtype="html"
    )
    return message
