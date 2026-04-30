"""Alembic environment configuration for Studiary.

Configures async SQLAlchemy engine for SQLite WAL mode migrations.
"""

from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio
import sys
import os

# Agregar el directorio raíz al path para importar los modelos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings
from app.core.database import Base  # noqa: F401

# Importar todos los modelos para que Alembic los detecte en autogenerate
from app.infrastructure.models import (  # noqa: F401
    periodo,
    curso,
    evaluacion,
    tarea,
    nota,
    recurso,
)

# this is the Alembic Config object
config = context.config

# Interpreter logging configuration
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata target para autogenerate
target_metadata = Base.metadata

settings = get_settings()


def get_url() -> str:
    """Retrieve database URL from application settings."""
    return settings.database_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_as_batch=True,  # Necesario para SQLite ALTER TABLE
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations in a synchronous connection context."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations using async engine for SQLite WAL compatibility."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Habilitar WAL mode para concurrencia sin bloqueos
        await connection.exec_driver_sql("PRAGMA journal_mode=WAL")
        await connection.exec_driver_sql("PRAGMA busy_timeout=5000")
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using asyncio."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
