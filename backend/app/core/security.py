"""Security utilities: JWT token creation/validation and password hashing.

Implementa HS256 JWT con expiración configurable y bcrypt para
almacenamiento seguro de contraseñas.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException

settings = get_settings()

# Contexto de hashing — bcrypt con coste adaptativo
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its bcrypt hash.

    Args:
        plain_password: The raw password from the request.
        hashed_password: The stored bcrypt hash.

    Returns:
        True if the password matches, False otherwise.
    """
    return _pwd_context.verify(plain_password, hashed_password)  # type: ignore[return-value]


def hash_password(password: str) -> str:
    """Hash a plain password with bcrypt.

    Args:
        password: The raw password to hash.

    Returns:
        The bcrypt hash string.
    """
    return _pwd_context.hash(password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token.

    Args:
        data: Payload to encode in the token.
        expires_delta: Custom expiration delta; defaults to settings value.

    Returns:
        The encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token.

    Args:
        token: The JWT string to validate.

    Returns:
        The decoded payload dictionary.

    Raises:
        UnauthorizedException: If the token is invalid or expired.
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as exc:
        raise UnauthorizedException("Invalid or expired token") from exc
