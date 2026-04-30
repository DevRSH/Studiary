"""Database engine y session factory — Tarea 4.2 del Sprint 0.

Configura SQLAlchemy async con SQLite en modo WAL para concurrencia
sin bloqueos en Railway Free Tier.
"""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

# ─── Engine ───────────────────────────────────────────────────────────────────
# connect_args solo aplica a SQLite; ignorado en otros drivers
_connect_args: dict[str, object] = {}
if "sqlite" in settings.database_url:
    _connect_args = {
        "check_same_thread": False,
        "timeout": 20,  # segundos de espera en busy (complementa PRAGMA)
    }

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args=_connect_args,
    pool_pre_ping=True,  # Detecta conexiones muertas automáticamente
)

# ─── Session Factory ──────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ─── Base Declarativa ────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models in Studiary."""

    pass


# ─── Dependency ───────────────────────────────────────────────────────────────
async def get_db() -> AsyncIterator[AsyncSession]:
    """Dependency de FastAPI: proporciona una sesión async por request.

    Garantiza commit en éxito y rollback en cualquier excepción,
    y cierra la sesión al finalizar el request lifecycle.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
