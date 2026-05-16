#!/bin/bash

echo "🚀 Deploying Studiary to Railway..."

# 1. Verificar que estamos en la rama main
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "❌ Error: Debes estar en la rama 'main' para deployar"
    exit 1
fi

# 2. Verificar que no hay cambios sin commitear
if ! git diff-index --quiet HEAD --; then
    echo "❌ Error: Hay cambios sin commitear"
    exit 1
fi

# 3. Build frontend
echo "📦 Building frontend..."
cd frontend
npm run build

# 4. Verificar build exitoso
if [ ! -d "dist" ]; then
    echo "❌ Error: Build de frontend falló"
    exit 1
fi

# 5. Copiar build al backend para servir
echo "📋 Copying frontend build to backend..."
rm -rf ../backend/static
cp -r dist ../backend/static

# 6. Ejecutar tests backend
echo "🧪 Running backend tests..."
cd ../backend
pytest tests/ -v

# 7. Deploy
echo "🚢 Deploying to Railway..."
git add -A
git commit -m "chore: deploy to railway $(date +'%Y-%m-%d %H:%M')"
git push origin main

echo "✅ Deploy iniciado. Monitorea en: https://railway.app/dashboard"
echo "📊 Logs: railway logs"
