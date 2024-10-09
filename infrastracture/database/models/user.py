from sqlalchemy import (
    MetaData, Integer, Column,
    String, TIMESTAMP, Enum,
    Boolean
)
from datetime import datetime
from ...database.base import Base
from auth.domain.entities.user import UserRole

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
    role = Column("role", Enum(UserRole), nullable=False, default=UserRole.USER)
    is_active = Column("is_active", Boolean, default=True)
    # role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    # role = relationship("Role", back_populates="users")


# users = Table(
#     "users",
#     metadata,
#     Column("id", Integer, primary_key=True, autoincrement=True),
#     Column("username", String, nullable=False, max_length=50),
#     Column("email", String, nullable=True),
#     Column("created_at", TIMESTAMP, default=datetime.now),
#     Column("phone_number", String, nullable=True),
#
#     Column("role_id", Integer, ForeignKey()),
#     role=relationship("Role", back_populates="user")
# )
