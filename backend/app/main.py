"""Studiary FastAPI Application Entry Point.

Configura el servidor ASGI, middleware de seguridad, rate limiting,
CORS y los routers de la API v1.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.database import engine, Base
from app.core.exceptions import StudiaryException
from app.core.logging import configure_logging
from app.presentation.api.v1 import router as api_v1_router

settings = get_settings()
configure_logging(debug=settings.debug)
log = structlog.get_logger(__name__)

# Rate limiter global
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifecycle manager: inicializa DB y configura SQLite WAL."""
    log.info("studiary.startup", version=settings.app_version, debug=settings.debug)

    # Crear tablas si no existen (solo en desarrollo; en prod usar Alembic)
    if settings.debug:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.exec_driver_sql("PRAGMA journal_mode=WAL")
            await conn.exec_driver_sql("PRAGMA busy_timeout=5000")
        log.info("studiary.db.initialized")

    yield

    log.info("studiary.shutdown")
    await engine.dispose()


def create_application() -> FastAPI:
    """Factory para crear la instancia de FastAPI con toda la configuración."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="API REST para Studiary — Centro de Comando Académico",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ─── Rate Limiting ────────────────────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    # ─── Middleware ───────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ─── Exception Handlers ───────────────────────────────────────────────────
    @app.exception_handler(StudiaryException)
    async def studiary_exception_handler(request: object, exc: StudiaryException) -> JSONResponse:
        """Mapea excepciones de dominio a respuestas HTTP estandarizadas."""
        log.warning("studiary.exception", code=exc.code, message=exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    # ─── Routers ──────────────────────────────────────────────────────────────
    app.include_router(api_v1_router, prefix="/api/v1")

    # ─── Health Check ─────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"], summary="Health check endpoint")
    async def health_check() -> dict[str, str]:
        """Retorna el estado operacional del servicio."""
        return {"status": "healthy", "version": settings.app_version}

    # ─── Static Files (Production) ────────────────────────────────────────────
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists() and is_production:
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            """Serve React SPA for all non-API routes."""
            file_path = static_dir / full_path
            
            # Si el archivo existe, servirlo
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)
            
            # Caso contrario, servir index.html (SPA routing)
            return FileResponse(static_dir / "index.html")

    return app


app = create_application()
