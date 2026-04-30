"""Test configuration and shared fixtures for Studiary backend.

Provides async test client, in-memory SQLite test database,
and common fixtures following pytest-asyncio conventions.
"""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app

# ─── Test DB ──────────────────────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

_test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

_TestSessionLocal = async_sessionmaker(
    bind=_test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db() -> AsyncIterator[None]:
    """Create all tables once per test session and drop them after."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _test_engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """Provide a transactional test session that rolls back after each test."""
    async with _TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Provide an async HTTP test client with overridden DB dependency."""

    async def _override_get_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    # 1. Mantenemos el override para proteger la DB real
    app.dependency_overrides[get_db] = _override_get_db

    # 2. Actualizamos SOLO esta parte con ASGITransport
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        yield ac
        
    # 3. (Opcional pero recomendado) Limpiamos el override al terminar
    app.dependency_overrides.clear()
