from sqlalchemy import (
    create_engine, select
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)
import os
from dotenv import load_dotenv
from .base import Base
from infrastracture.database.models.user import User

load_dotenv()


class UserRepository:
    def __init__(self):
        self.db_url = os.getenv("SQLALCHEMY_DATABASE_URL")
        self.engine = create_async_engine(
            self.db_url,
            echo=True
        )
        self.sessionLocalAsync = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def create_user_table(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_user_by_username(self, username: str):
        async with self.sessionLocalAsync(expire_on_commit=False) as session:
            try:
                query = select(User).where(User.username == username)
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                if not user:
                    return "user wasn't found. check up your statement again"
                # return (f"data of {username}:\n "
                #         f"email: {user.email}\n "
                #         f"birthday: {user.date_of_birth}\n"
                #         f"phone: {user.phone_number}\n "
                #         f"valid: {user.is_active}\n") // make logs!
                return user
            except Exception as e:
                print(f"error occurred: {e}")

    async def get_current_user(self):
        ...

    async def change_password_of_current_user(self):
        ...

    async def get_db(self) -> AsyncSession:
        async with self.sessionLocalAsync() as session:
            yield session

    async def test_db_connection(self):
        ...
        # try:
        #     async with databases.Database(self.db) as database:
        #         await database.connect()
        #         print("Connection to the database established successfully.")
        #         return True
        # except OperationalError as e:
        #     print("Failed to connect to the database.")
        #     print(e)
        #     return False
