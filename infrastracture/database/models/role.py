from sqlalchemy import (
    MetaData, Table, Integer, Column,
    String, JSON, ForeignKey, PrimaryKeyConstraint, Enum)
from sqlalchemy.orm import relationship
from auth.domain.entities.user import UserRole

metadata = MetaData()

roles = Table(
    "roles",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", Enum(UserRole), nullable=False),
    # Column("permissions", JSON)
    user=relationship("User", back_populates="role", uselist=False)
)
