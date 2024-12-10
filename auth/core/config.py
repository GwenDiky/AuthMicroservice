import logging

from fastapi.security import HTTPBearer
from fastapi.templating import Jinja2Templates
from pydantic import Field
from pydantic_settings import BaseSettings

http_bearer = HTTPBearer()


class MailSettings(BaseSettings):
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    mail_from_name: str
    localstack_endpoint: str
    mail_ssl_tls: bool = False
    mail_starttls: bool = True
    mail_use_credentials: bool = True
    mail_validate_certs: bool = True
    aws_default_region: str
    aws_access_key_id: str
    aws_secret_access_key: str


class DbSettings(BaseSettings):
    db_url: str = Field(validation_alias="SQLALCHEMY_DATABASE_URL")
    db_user: str
    db_password: str
    db_name: str


class JWTSettings(BaseSettings):
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int


class RedisSettings(BaseSettings):
    redis_url: str
    redis_port: str
    redis_password: str


class KafkaSettings(BaseSettings):
    kafka_bootstrap_servers: str


class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    jwt: JWTSettings = JWTSettings()
    mail: MailSettings = MailSettings()
    redis: RedisSettings = RedisSettings()
    kafka: KafkaSettings = KafkaSettings()

    domain: str


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


templates = Jinja2Templates(directory="templates")

settings = Settings()
