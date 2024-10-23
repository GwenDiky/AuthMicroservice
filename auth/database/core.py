from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)

from auth.core.base import Base
from auth.core.config import settings

engine = create_async_engine(
    settings.db.db_url,
    echo=True

)

sessionLocalAsync = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_session() -> AsyncSession:
    async with sessionLocalAsync() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        finally: await session.close()


async def async_init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def clear_db():
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())

