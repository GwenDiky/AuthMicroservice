from pydantic import BaseModel, EmailStr
from datetime import datetime

class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenDataSchema(BaseModel):
    sub: int
    username: str
    email: EmailStr
    exp: datetime
    iat: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: int(v.timestamp())
        }