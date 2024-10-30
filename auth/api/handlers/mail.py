from fastapi import APIRouter

from auth.core.config import setup_logging
from auth.schemas.email import EmailSchema
from auth.services.email import create_message, send_email as send_email_service

setup_logging()

mail_router = APIRouter()


@mail_router.post('/send-mail')
async def send_mail(emails: EmailSchema):
    mails = emails.addresses

    html = "<h1>Welcome to AsyncMicroservice</h1>"
    message = await create_message(
        recipients=mails,
        subject="Welcome",
        body=html
    )

    await send_email_service(message)

    return {"message": "Email sent successfully"}



