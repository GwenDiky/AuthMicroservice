from user import UserSchema, UserRole


class UserWithoutPermissionsSchema(UserSchema):
    role: UserRole = UserRole.USER_WITHOUT_PERMISSIONS
