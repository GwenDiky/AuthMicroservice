from sqlalchemy.ext.asyncio import AsyncSession
from auth.services.user import UserRepository, User
from auth.schemas.user import UserCreateSchema
from auth.utils.utils_users import hash_password


user_schema = UserCreateSchema(
    username="testuser",
    password="securepassword",
    phone_number=None,
    email="test@example.com",
    date_of_birth=None
)

async def create_user(db: AsyncSession):
    user_data = user_schema.model_dump()
    user_data["password"] = await hash_password(user_data["password"])
    new_user = User(**user_data)
    user = await UserRepository(db).add_new_user(new_user)
    return user

async def create_user_by_fields(db: AsyncSession, username:str, password:str, email:str, phone_number:str=None, date_of_birth=None):
    user_data = {'username': username,
                 'password': password,
                 'email':email,
                 'phone_number':phone_number,
                 'date_of_birth':date_of_birth}
    user_data["password"] = await hash_password(user_data["password"])
    new_user = User(**user_data)
    user = await UserRepository(db).add_new_user(new_user)
    return user