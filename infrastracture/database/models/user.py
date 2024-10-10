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

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "date_of_birth": self.date_of_birth.isoformat(),
            "phone": self.phone_number,
            "role": self.role,
            "is_active": self.is_active,
        }


