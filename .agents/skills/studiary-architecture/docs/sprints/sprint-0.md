# SPRINT 0: FOUNDATION SETUP

## 1. Objetivo de Ejecución
Crear la estructura base del proyecto StudyHub. Se requiere implementar una arquitectura modular estricta, establecer la configuración de desarrollo local, y definir el pipeline de CI/CD básico.

## 2. Entregables Esperados
1.  Estructura de directorios completa y validada (backend + frontend).
2.  Configuración de *tooling* de análisis estático (Linters, formatters, pre-commit).
3.  Entorno Dockerizado (Desarrollo y Producción).
4.  Configuración de Alembic para el control de versiones del esquema de base de datos.
5.  Scripts de inicialización para SQLite en modo WAL.
6.  Documentación técnica (README) con instrucciones de despliegue.
7.  Workflow básico de GitHub Actions.

## 3. Topología de Directorios Requerida

### Backend (Python/FastAPI)
Generar la siguiente jerarquía bajo el directorio `/backend/`:
- /alembic/ (versions/, env.py)
- /app/ (main.py, __init__.py)
  - /core/ (config.py, database.py, dependencies.py, exceptions.py, logging.py, security.py)
  - /domain/ (entities/, repositories/)
  - /infrastructure/ (models/, repositories/)
    - models/ (base.py, periodo.py, curso.py, evaluacion.py, tarea.py, nota.py, recurso.py)
  - /application/ (services/, schemas/requests/, schemas/responses/)
    - services/ (curso_service.py, evaluacion_service.py, nota_service.py, calculadora_service.py)
  - /presentation/ (api/v1/endpoints/, dependencies.py)
    - endpoints/ (periodos.py, cursos.py, evaluaciones.py, tareas.py, notas.py)
- /tests/ (unit/, integration/, conftest.py)
- Archivos raíz: .env.example, .env.test, pyproject.toml, pytest.ini, alembic.ini, Dockerfile

### Frontend (React/TypeScript)
Generar la siguiente jerarquía bajo el directorio `/frontend/`:
- /public/ (manifest.json, icons/)
- /src/ (main.tsx, vite-env.d.ts)
  - /app/ (App.tsx, router.tsx, providers.tsx)
  - /features/ (periodos/, cursos/, evaluaciones/, tareas/, notas/, calculadora/)
    - Cada feature debe contener: api/, components/, hooks/, types/, index.ts
  - /shared/ (components/ui/, components/layouts/, components/forms/, hooks/, utils/, types/, api/client.ts, api/queryClient.ts)
  - /assets/
  - /styles/ (globals.css)
- /tests/ (setup.ts, mocks/)
- Archivos raíz: .env.example, .env.development, index.html, package.json, tsconfig.json, vite.config.ts, tailwind.config.js, Dockerfile

### Root Workspace
Generar en la raíz del repositorio:
- docker-compose.yml
- docker-compose.prod.yml
- .github/workflows/ci.yml
- .gitignore
- LICENSE
- README.md

## 4. Tareas de Implementación Crítica

### Tarea 4.1: Backend Core Configuration
Crear `backend/app/core/config.py`:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with validation"""
    app_name: str = "StudyHub API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    database_url: str = "sqlite+aiosqlite:///./studyhub.db"
    cors_origins: list[str] = ["http://localhost:5173"]
    
    secret_key: str
    algorithm: str = "HS256"
    rate_limit_per_minute: int = 60
    
    nextcloud_url: str | None = None
    nextcloud_username: str | None = None
    nextcloud_password: str | None = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

Tarea 4.2: Database Setup
Crear backend/app/core/database.py:

Python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass

async def get_db() -> AsyncSession:
    """Dependency for getting async DB session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
Tarea 4.3: Base SQLAlchemy Model
Crear backend/app/infrastructure/models/base.py:

Python
from datetime import datetime
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

class BaseModel(Base, TimestampMixin):
    """Base model with ID and timestamps"""
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
Tarea 4.4: Frontend API Client
Crear frontend/src/shared/api/client.ts:

TypeScript
import axios, { AxiosError, AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    });
    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  public getInstance(): AxiosInstance {
    return this.client;
  }
}

export const apiClient = new ApiClient().getInstance();
Tarea 4.5: Docker Setup
Crear docker-compose.yml:

YAML
version: '3.8'
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - backend-db:/app/data
    env_file:
      - ./backend/.env
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    command: npm run dev -- --host

volumes:
  backend-db:
Tarea 4.6: Pre-commit Hooks
Crear .pre-commit-config.yaml en la raíz:

YAML
repos:
  - repo: [https://github.com/astral-sh/ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit)
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
  - repo: [https://github.com/psf/black](https://github.com/psf/black)
    rev: 23.11.0
    hooks:
      - id: black
  - repo: [https://github.com/pre-commit/mirrors-eslint](https://github.com/pre-commit/mirrors-eslint)
    rev: v8.54.0
    hooks:
      - id: eslint
        files: \.(js|ts|tsx)$
        types: [file]
Tarea 4.7: README.md Template
Markdown
# StudyHub - Centro de Comando Académico
PWA móvil-first para gestión académica personal con cálculo predictivo de notas.

## Features
- Cálculo de notas en tiempo real.
- Notas con handwriting digital.
- Sistema de tareas con priorización automática basada en el algoritmo $P=\frac{W \cdot D}{T+1}$.
- Integración con Nextcloud para almacenamiento de recursos.
- PWA instalable con capacidades offline.

## Tech Stack
**Backend:** FastAPI + SQLAlchemy + SQLite (WAL Mode)
**Frontend:** React + TypeScript + Vite + Tailwind
**Deploy:** Railway

## Local Development
### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose

### Setup
[Incluir instrucciones detalladas de compilación y ejecución de contenedores]

## API Documentation
Servicio activo en: `http://localhost:8000/docs`

## License
MIT
5. Criterios de Aceptación y Validación (Checklist)
Antes de finalizar el sprint, el agente debe verificar de forma autónoma:

[ ] docker-compose up compila sin errores de sintaxis o dependencias.

[ ] Backend accesible y respondiendo en el puerto 8000.

[ ] Frontend renderizando correctamente en el puerto 5173.

[ ] Esquema OpenAPI disponible en la ruta /docs.

[ ] Linters correctamente inicializados (black, ruff, eslint, prettier).

[ ] Hooks de pre-commit instalados y funcionales.

[ ] Archivos de entorno .env.example generados correctamente.

[ ] Resolución absoluta de módulos e importaciones funcionales en Python y TypeScript.

[ ] Análisis de tipos superado sin errores (mypy, tsc --noEmit).

Instrucción Final: Genera el código completo y listo para producción de todos los archivos descritos. Aplica docstrings y comentarios inline exclusivamente en bloques lógicos complejos. Omite confirmaciones intermedias y procede con la ejecución de la estructura.    