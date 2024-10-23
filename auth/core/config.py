import logging

from fastapi.security import HTTPBearer

http_bearer = HTTPBearer()
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseSettings):
    db_url: str = Field(validation_alias="SQLALCHEMY_DATABASE_URL")
    db_user: str = Field(validation_alias="DB_USER")
    db_password: str = Field(validation_alias="DB_PASSWORD")
    db_name: str = Field(validation_alias="DB_NAME")

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra="allow"
    )

class JWTSettings(BaseSettings):
    jwt_secret: str = Field(validation_alias="JWT_SECRET")
    jwt_algorithm: str = Field(validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra="allow"
    )

class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    jwt: JWTSettings = JWTSettings()

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

settings = Settings()