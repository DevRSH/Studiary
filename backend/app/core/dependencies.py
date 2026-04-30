"""FastAPI dependency injection utilities.

Centraliza las dependencias reutilizables: sesión DB, usuario actual,
y validación de permisos.
"""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token

# ─── DB Session ───────────────────────────────────────────────────────────────
DbSession = Annotated[AsyncSession, Depends(get_db)]

# ─── Auth ─────────────────────────────────────────────────────────────────────
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> int:
    """Extract and validate the current user ID from Bearer token.

    Args:
        credentials: HTTP Bearer credentials from Authorization header.

    Returns:
        The authenticated user's ID.

    Raises:
        UnauthorizedException: If token is missing, invalid, or expired.
    """
    if credentials is None:
        raise UnauthorizedException("Authorization header is required")

    payload = decode_access_token(credentials.credentials)
    user_id: int | None = payload.get("sub")  # type: ignore[assignment]

    if user_id is None:
        raise UnauthorizedException("Token payload is invalid")

    return user_id


CurrentUserId = Annotated[int, Depends(get_current_user_id)]
