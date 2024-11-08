from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from auth.core.base import Base
from auth.core.config import settings

engine = create_async_engine(settings.db.db_url, echo=True)

sessionLocalAsync = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncSession:
    async with sessionLocalAsync() as session:
        yield session


async def async_init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def clear_db():
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
