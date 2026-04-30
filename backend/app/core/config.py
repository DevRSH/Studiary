"""Application settings — Tarea 4.1 del Sprint 0.

Usa pydantic-settings para validación estricta y carga desde .env.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with strict validation.

    All values are loaded from environment variables or .env file.
    Secrets must NEVER be hardcoded.
    """

    # ─── App ──────────────────────────────────────────────────────────────────
    app_name: str = "Studiary API"
    app_version: str = "1.0.0"
    debug: bool = False

    # ─── Database ─────────────────────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./data/studiary.db"

    # ─── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:5173"]

    # ─── Security ─────────────────────────────────────────────────────────────
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # ─── Rate Limiting ────────────────────────────────────────────────────────
    rate_limit_per_minute: int = 60

    # ─── Nextcloud (opcional) ─────────────────────────────────────────────────
    nextcloud_url: str | None = None
    nextcloud_username: str | None = None
    nextcloud_password: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Cached singleton para las configuraciones de la aplicación.

    El decorador lru_cache garantiza que la instancia se cree una sola vez
    por proceso, evitando re-lecturas del filesystem en cada request.
    """
    return Settings()  # type: ignore[call-arg]
