import logging

from fastapi.security import HTTPBearer

http_bearer = HTTPBearer()
from pydantic import Field
from pydantic_settings import BaseSettings
from fastapi.templating import Jinja2Templates

class MailSettings(BaseSettings):
    mail_username: str = Field(validation_alias="MAIL_USERNAME")
    mail_password: str = Field(validation_alias="MAIL_PASSWORD")
    mail_from: str = Field(validation_alias="MAIL_FROM")
    mail_port: int = Field(validation_alias="MAIL_PORT")
    mail_server: str = Field(validation_alias="MAIL_SERVER")
    mail_from_name: str = Field(validation_alias="MAIL_FROM_NAME")
    mail_ssl_tls: bool = False
    mail_starttls: bool = True
    mail_use_credentials: bool = True
    mail_validate_certs: bool = True


class DbSettings(BaseSettings):
    db_url: str = Field(validation_alias="SQLALCHEMY_DATABASE_URL")
    db_user: str = Field(validation_alias="DB_USER")
    db_password: str = Field(validation_alias="DB_PASSWORD")
    db_name: str = Field(validation_alias="DB_NAME")


class JWTSettings(BaseSettings):
    jwt_secret: str = Field(validation_alias="JWT_SECRET")
    jwt_algorithm: str = Field(validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")


class RedisSettings(BaseSettings):
    redis_url: str = Field(validation_alias="REDIS_URL")
    redis_port: str = Field(validation_alias="REDIS_PORT")
    redis_password: str = Field(validation_alias="REDIS_PASSWORD")


class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    jwt: JWTSettings = JWTSettings()
    mail: MailSettings = MailSettings()
    redis: RedisSettings = RedisSettings()

    domain: str = Field(validation_alias="DOMAIN")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

templates = Jinja2Templates(directory="templates")

settings = Settings()
