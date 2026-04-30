"""Custom exception hierarchy for Studiary domain errors.

Cada excepción mapea a un código HTTP específico, permitiendo el
manejo centralizado en el exception_handler de FastAPI en main.py.
"""

from http import HTTPStatus


class StudiaryException(Exception):
    """Base exception for all Studiary domain errors."""

    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR.value
    code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None) -> None:
        """Initialize with optional custom message."""
        if message:
            self.message = message
        super().__init__(self.message)


class NotFoundException(StudiaryException):
    """Resource not found in the database."""

    status_code = HTTPStatus.NOT_FOUND.value
    code = "NOT_FOUND"
    message = "Resource not found"


class ConflictException(StudiaryException):
    """Duplicate or conflicting resource."""

    status_code = HTTPStatus.CONFLICT.value
    code = "CONFLICT"
    message = "Resource already exists"


class ValidationException(StudiaryException):
    """Domain-level validation failure (beyond Pydantic schema)."""

    status_code = HTTPStatus.UNPROCESSABLE_ENTITY.value
    code = "VALIDATION_ERROR"
    message = "Validation failed"


class UnauthorizedException(StudiaryException):
    """Authentication required or token invalid."""

    status_code = HTTPStatus.UNAUTHORIZED.value
    code = "UNAUTHORIZED"
    message = "Authentication required"


class ForbiddenException(StudiaryException):
    """Authenticated but not authorized for this action."""

    status_code = HTTPStatus.FORBIDDEN.value
    code = "FORBIDDEN"
    message = "You do not have permission to perform this action"


class ServiceUnavailableException(StudiaryException):
    """External service (Nextcloud) unavailable."""

    status_code = HTTPStatus.SERVICE_UNAVAILABLE.value
    code = "SERVICE_UNAVAILABLE"
    message = "External service temporarily unavailable"
