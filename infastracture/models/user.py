from sqlalchemy import (
    MetaData, Table, Integer, Column,
    String, TIMESTAMP)
from datetime import datetime


metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String, nullable=False, max_length=50),
    Column("email", String, nullable=False),
    Column("created_at", TIMESTAMP, default=datetime.now),
    Column("phone_number", String, nullable=True),
)
