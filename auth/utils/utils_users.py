import bcrypt

from auth.exceptions import AuthFailedException


async def compare_passwords(password, hashed_password):
    if not bcrypt.checkpw(password.encode("utf-8"),
                          hashed_password.encode("utf-8")):
        raise AuthFailedException
    return True


async def hash_password(
        password: str,
) -> str:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()

    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


async def validate_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password=password.encode(),
                          hashed_password=hashed_password)
