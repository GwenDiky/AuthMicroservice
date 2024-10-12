from sqlalchemy import (
    MetaData, Integer, Column,
    String, TIMESTAMP, Enum,
    Boolean
)
from datetime import datetime
from auth.core.base import Base
from sqlalchemy.ext.asyncio import AsyncSession

metadata = MetaData()


class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", String(50), nullable=False)
    password = Column("password", String)
    email = Column("email", String, nullable=True)
    created_at = Column("created_at", TIMESTAMP(timezone=True), default=datetime.now)
    date_of_birth = Column("date_of_birth", TIMESTAMP(timezone=True), default=datetime.now)
    phone_number = Column("phone_number", String, nullable=True)
    role = Column("role", String, nullable=False, default="user")
    is_active = Column("is_active", Boolean, default=True)
    # role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    # role = relationship("Role", back_populates="users")

    @classmethod
    async def find_by_email(cls, db: AsyncSession, email: str):
        query = select(cls).where(cls.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def find_by_username(cls, db: AsyncSession, username: str):
        query = select(cls).where(cls.username == username)
        result = await db.execute(query)
        return result.scalars().first()


