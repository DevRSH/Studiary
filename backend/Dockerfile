# Studiary Backend Dockerfile
# Multi-stage build para optimizar tamaño de imagen

# ─── Build stage ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copiar archivos de dependencias
COPY pyproject.toml ./
COPY README.md ./

# Configurar Poetry para no crear venv separado
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-root --no-interaction

# ─── Development stage ──────────────────────────────────────────────────────
FROM python:3.11-slim AS development

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Directorio para la base de datos
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ─── Production stage ───────────────────────────────────────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN mkdir -p /app/data

# Usuario no-root para seguridad
RUN useradd -r -u 1001 studiary && chown -R studiary:studiary /app
USER studiary

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
