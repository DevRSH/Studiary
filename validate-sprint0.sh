#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  Studiary — Sprint 0 Validation Script
#  Ejecutar desde la raíz del proyecto:  bash validate-sprint0.sh
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASS=0
FAIL=0

green()  { echo -e "\033[0;32m✅ $*\033[0m"; }
red()    { echo -e "\033[0;31m❌ $*\033[0m"; }
yellow() { echo -e "\033[0;33m⚠️  $*\033[0m"; }
header() { echo -e "\n\033[1;34m── $* ──\033[0m"; }

check() {
  local label="$1"; shift
  if "$@" &>/dev/null; then
    green "$label"
    ((PASS++))
  else
    red "$label"
    ((FAIL++))
  fi
}

# ─── 1. Docker Compose ──────────────────────────────────────────────
header "1. Docker Compose"
check "docker-compose.yml sintaxis válida" docker compose -f "$ROOT/docker-compose.yml" config --quiet
check "docker-compose.prod.yml sintaxis válida" docker compose -f "$ROOT/docker-compose.prod.yml" config --quiet

# ─── 2. Backend — Archivos críticos ────────────────────────────────
header "2. Backend — Archivos de configuración"
check ".env.example existe"       test -f "$ROOT/backend/.env.example"
check ".env.test existe"          test -f "$ROOT/backend/.env.test"
check "pyproject.toml existe"     test -f "$ROOT/backend/pyproject.toml"
check "alembic.ini existe"        test -f "$ROOT/backend/alembic.ini"
check "alembic/env.py existe"     test -f "$ROOT/backend/alembic/env.py"

# ─── 3. Backend — Python ────────────────────────────────────────────
header "3. Backend — Python (requiere venv activo)"

BACKEND="$ROOT/backend"
VENV="$BACKEND/.venv"

if [ ! -d "$VENV" ]; then
  yellow "Venv no encontrado. Creando en backend/.venv…"
  python3 -m venv "$VENV"
fi

source "$VENV/bin/activate"

# Instalar dependencias si no están
if ! python -c "import fastapi" &>/dev/null; then
  yellow "Instalando dependencias del backend…"
  pip install -q poetry
  cd "$BACKEND" && poetry install --no-interaction -q
  cd "$ROOT"
fi

# Copiar .env si no existe
if [ ! -f "$BACKEND/.env" ]; then
  cp "$BACKEND/.env.example" "$BACKEND/.env"
  yellow ".env creado desde .env.example — RECUERDA cambiar SECRET_KEY"
  # Generar una SECRET_KEY temporal para tests
  SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/your-super-secret-key-change-this-in-production/$SECRET/" "$BACKEND/.env"
  else
    sed -i "s/your-super-secret-key-change-this-in-production/$SECRET/" "$BACKEND/.env"
  fi
  green ".env configurado con SECRET_KEY temporal"
fi

cd "$BACKEND"

# Imports Python
check "app.main importa sin errores" python -c "
import os; os.environ.setdefault('SECRET_KEY', 'test-key-32chars-xxxxxxxxxxxxxxxxx')
from app.main import app
"

# Pytest recolecta tests
check "pytest recopila tests (≥1 test)" bash -c "
export SECRET_KEY=test-key-32chars-xxxxxxxxxxxxxxxxx
python -m pytest tests/ --collect-only -q 2>&1 | grep -q 'test session starts'
"

# Unit tests del CalculadoraService (sin DB, sin .env)
check "Unit tests pasan (calculadora)" bash -c "
export SECRET_KEY=test-key-32chars-xxxxxxxxxxxxxxxxx
python -m pytest tests/unit/test_calculadora_service.py -q 2>&1 | grep -q 'passed'
"

deactivate
cd "$ROOT"

# ─── 4. Frontend — Archivos críticos ───────────────────────────────
header "4. Frontend — Archivos de configuración"
check "package.json existe"       test -f "$ROOT/frontend/package.json"
check "tsconfig.json existe"      test -f "$ROOT/frontend/tsconfig.json"
check "vite.config.ts existe"     test -f "$ROOT/frontend/vite.config.ts"
check "tailwind.config.js existe" test -f "$ROOT/frontend/tailwind.config.js"
check "index.html existe"         test -f "$ROOT/frontend/index.html"
check ".env.example existe"       test -f "$ROOT/frontend/.env.example"
check "src/main.tsx existe"       test -f "$ROOT/frontend/src/main.tsx"
check "src/app/App.tsx existe"    test -f "$ROOT/frontend/src/app/App.tsx"

# ─── 5. Frontend — Node / TypeScript ───────────────────────────────
header "5. Frontend — TypeScript (requiere Node 20+)"

FRONTEND="$ROOT/frontend"

if [ ! -d "$FRONTEND/node_modules" ]; then
  yellow "node_modules no encontrado. Ejecutando npm install…"
  cd "$FRONTEND" && npm install --silent
  cd "$ROOT"
fi

cd "$FRONTEND"

# Copiar .env si no existe
[ ! -f ".env.development" ] && cp .env.example .env.development

check "tsc --noEmit pasa sin errores" npx tsc --noEmit

cd "$ROOT"

# ─── 6. Pre-commit ─────────────────────────────────────────────────
header "6. Pre-commit hooks"
if command -v pre-commit &>/dev/null; then
  check "pre-commit instalado globalmente" pre-commit --version
else
  yellow "pre-commit no encontrado globalmente — instalar con: pip install pre-commit && pre-commit install"
  ((FAIL++))
fi

# ─── Resultado Final ─────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════"
echo "  Sprint 0 Validation — Resultado Final"
echo "  Pasados: $PASS  │  Fallidos: $FAIL"
echo "═══════════════════════════════════════════"

if [ "$FAIL" -eq 0 ]; then
  green "Sprint 0 COMPLETADO — Listo para Sprint 1 🚀"
  exit 0
else
  red "$FAIL validación(es) fallaron — revisar output arriba"
  exit 1
fi
