from sqlalchemy import (
    MetaData, Table, Integer, Column,
    String, TIMESTAMP, ForeignKey)
from datetime import datetime
from sqlalchemy.orm import relationship

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String, nullable=False, max_length=50),
    Column("email", String, nullable=True),
    Column("created_at", TIMESTAMP, default=datetime.now),
    Column("phone_number", String, nullable=True),

    Column("role_id", Integer, ForeignKey()),
    role=relationship("Role", back_populates="user")
)
