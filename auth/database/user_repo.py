from auth.database.repo import SqlAlchemyARepository
from auth.database.user import User

class UserRepository(SqlAlchemyARepository):
    model = User

    def __init__(self):
        super().__init__()
