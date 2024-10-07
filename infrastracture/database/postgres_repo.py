from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()


class UserRepository:
    def __init__(self):
        self.db_url = os.getenv("SQLALCHEMY_DATABASE_URL")
        self.engine = create_engine(self.db_url)
        self.sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    async def get_db(self):


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