from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

headers = {"WWW-Authenticate": "Bearer"}


class PasswordNotChangedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Password wasn't changed",
            headers=headers,
        )


class ProfileNotChangedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Profile wasn't changed",
            headers=headers,
        )


class UserNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User wasn't found. Check up your credentials",
            headers=headers,
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
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
            headers=headers,
        )


class SignUpFailedException(HTTPException, SQLAlchemyError):
    def __init__(self, detail: Any = None) -> None:
        HTTPException.__init__(
            self,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail if detail else "Some of fields are incorrect",
        )
        SQLAlchemyError.__init__(self)


class InvalidTokenException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers=headers,
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


class UserAlreadyExistsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with such email already exists. Try to log in.",
            headers=headers,
        )


class UserAlreadyVerifiedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is already verified.",
            headers=headers,
        )


class MailVerificationFailedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Mail verification failed",
            headers=headers,
        )


class MailNotVerifiedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Recipient email is not verified. " "Please verify the email first.",
            headers=headers,
        )

class KafkaConnectionError(Exception):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Kafka connection error",
        )

class KafkaTimeoutErrorError(Exception):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Kafka timeout error",
        )


class KafkaErrorError(Exception):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Unexpected Kafka error",
        )

