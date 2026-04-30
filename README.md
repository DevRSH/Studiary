# Studiary — Centro de Comando Académico

> PWA móvil-first para gestión académica personal con cálculo predictivo de notas.

## Features

- 📊 **Cálculo predictivo de notas** en tiempo real.
- ✏️ **Notas con handwriting digital** (Fabric.js + Markdown).
- ⚡ **Sistema de tareas** con priorización automática basada en el algoritmo:

  $$P = \frac{W \cdot D}{T + 1}$$

- ☁️ **Integración con Nextcloud** para almacenamiento de recursos.
- 📱 **PWA instalable** con capacidades offline.

## Tech Stack

| Capa | Tecnología |
|---|---|
| **Backend** | FastAPI 0.104+ · SQLAlchemy 2.0 Async · SQLite WAL · Alembic |
| **Frontend** | React 18 · TypeScript Strict · Vite 5 · Tailwind CSS · TanStack Query |
| **Deploy** | Railway (Single Container, Free Tier) |
| **PWA** | vite-plugin-pwa |

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose

### Setup

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd studiary

# 2. Configurar variables de entorno
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.development

# 3. Editar backend/.env — establecer SECRET_KEY
# SECRET_KEY=<genera con: openssl rand -hex 32>

# 4. Levantar los servicios
docker compose up --build

# 5. Acceder a la aplicación
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

### Desarrollo sin Docker

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (nueva terminal)
cd frontend
npm install
npm run dev
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

## API Documentation

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

## Project Structure

```
studiary/
├── backend/              # FastAPI application (Clean Architecture)
│   ├── app/
│   │   ├── core/         # Config, DB, security, logging
│   │   ├── domain/       # Entities & repository interfaces
│   │   ├── infrastructure/ # SQLAlchemy models & repo implementations
│   │   ├── application/  # Services (use cases) & schemas
│   │   └── presentation/ # FastAPI routers
│   ├── alembic/          # Database migrations
│   └── tests/
└── frontend/             # React PWA
    └── src/
        ├── app/          # Router, providers
        ├── features/     # Domain-driven feature modules
        └── shared/       # Reusable components & utilities
```

## License

MIT © 2026 Studiary
