from sqlalchemy import (
    MetaData, Table, Integer, Column,
    String, JSON)


metadata = MetaData()

roles = Table(
    "roles",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("permissions", JSON)
)