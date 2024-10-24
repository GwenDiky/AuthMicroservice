from datetime import datetime

from sqlalchemy import (
    MetaData, Integer, Column,
    String, TIMESTAMP, Boolean
)

from auth.core.base import Base

metadata = MetaData()


class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", String(50), nullable=False, unique=True)
    password = Column("password", String)
    email = Column("email", String, nullable=False, unique=True)
    created_at = Column("created_at", TIMESTAMP(timezone=True), default=datetime.now)
    date_of_birth = Column("date_of_birth", TIMESTAMP(timezone=True), default=datetime.now)
    phone_number = Column("phone_number", String, nullable=True)
    is_superuser = Column("is_superuser", Boolean, default=False)