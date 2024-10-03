from user import User, UserRole


class Admin(User):
    role: UserRole = UserRole.ADMIN