# 🚀 Deploy Guide - Studiary

## Railway Deployment

### Prerequisitos

1. Cuenta en Railway: https://railway.app
2. Railway CLI instalado: `npm i -g @railway/cli` 
3. Git configurado

### Setup Inicial

1. **Crear proyecto en Railway:**
   ```bash
   railway login
   railway init
   ```

2. **Configurar variables de entorno:**
   En Railway Dashboard → Variables:
   ```
   DATABASE_URL=sqlite+aiosqlite:////app/data/studiary.db
   SECRET_KEY=<generar con: openssl rand -hex 32>
   CORS_ORIGINS=https://studiary.up.railway.app
   RAILWAY_ENVIRONMENT=production
   DEBUG=false
   ```

3. **Agregar volumen persistente:**
   Railway Dashboard → Settings → Volumes:
   - Mount Path: `/app/data` 
   - Size: 1GB

### Deploy

Opción A - Automático (script):
```bash
./scripts/deploy-railway.sh
```

Opción B - Manual:
```bash
# Build frontend
cd frontend && npm run build

# Copiar a backend
cp -r dist ../backend/static

# Push
git add -A
git commit -m "deploy"
git push origin main
```

### Verificación Post-Deploy

1. **Health check:**
   ```bash
   curl https://your-app.up.railway.app/api/v1/health
   ```

2. **Logs:**
   ```bash
   railway logs
   ```

3. **Migraciones:**
   ```bash
   railway run alembic upgrade head
   ```

### Troubleshooting

**Error: Database locked**
- Verificar que WAL mode está habilitado
- Aumentar busy_timeout en database_production.py

**Error: 502 Bad Gateway**
- Verificar logs: `railway logs` 
- Verificar health check endpoint
- Verificar que PORT env var está configurado

**App no carga (404)**
- Verificar que frontend/dist fue copiado a backend/static
- Verificar configuración de SPA routing en main.py
