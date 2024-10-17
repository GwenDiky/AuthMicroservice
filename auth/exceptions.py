from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

headers = {"WWW-Authenticate": "Bearer"}


class PasswordNotChangedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Password wasn't changed",
            headers=headers
        )


class UserNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User wasn't found. Check up your credentials",
            headers=headers
        )


class AuthFailedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers=headers,
        )


class InactiveUserException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_coded=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
            headers=headers,
        )


class SignUpFailedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details="some of fields are incorrect",
            header=headers,
        )


class InvalidTokenException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers=header,
        )


class AuthTokenExpiredException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token",
            headers=headers,
        )


class BadRequestException(HTTPException, SQLAlchemyError):
    def __init__(self, detail: Any = None) -> None:
        HTTPException.__init__(
            self,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail if detail else "Bad request",
        )
        SQLAlchemyError.__init__(self)
