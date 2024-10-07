from user import UserSchema, UserRole


class AdminSchema(UserSchema):
    role: UserRole = UserRole.ADMIN