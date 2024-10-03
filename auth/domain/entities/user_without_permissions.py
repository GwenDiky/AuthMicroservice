from user import User, UserRole


class UserWithoutPermissions(User):
    role: UserRole = UserRole.USER_WITHOUT_PERMISSIONS
