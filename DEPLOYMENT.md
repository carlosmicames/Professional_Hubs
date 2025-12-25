# Deployment Guide - Professional Hubs Conflict API

## Railway Deployment (Recommended)

### Prerequisites
- GitHub account
- Railway account (sign up at [railway.app](https://railway.app))

### Steps

#### 1. Push Code to GitHub
```bash
git add .
git commit -m "Add fuzzy conflict search with Railway deployment"
git push origin main
```

#### 2. Deploy to Railway

1. Go to [railway.app](https://railway.app) and click "Start a New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `Professional_Hubs` repository
4. Railway will automatically detect the configuration from `railway.toml`

#### 3. Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a PostgreSQL database
4. The `DATABASE_URL` environment variable will be automatically set

#### 4. Configure Environment Variables

Go to your service's "Variables" tab and add:

```
APP_NAME=Professional Hubs - Conflict API
API_VERSION=v1
DEBUG=False
FUZZY_THRESHOLD=70
FUZZY_HIGH_CONFIDENCE=90
CORS_ORIGINS=*
TIMEZONE=America/Puerto_Rico
```

**Note:** `DATABASE_URL` is automatically set by Railway when you add PostgreSQL.

#### 5. Run Database Migrations

After first deployment, run migrations:

1. Go to your service in Railway
2. Click on "Deployments" tab
3. Click on the latest deployment
4. Open "Logs" and verify the app started
5. Alternatively, connect via Railway CLI:
   ```bash
   railway login
   railway link
   railway run alembic upgrade head
   ```

#### 6. Access Your API

Your API will be available at: `https://your-project.railway.app/api/v1/docs`

---

## Manual Deployment (Alternative)

### Requirements
- Python 3.11+
- PostgreSQL 14+

### Setup

1. **Install dependencies:**
```bash
cd conflict_api
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp ../.env.example .env
# Edit .env with your database credentials
```

3. **Run migrations:**
```bash
alembic upgrade head
```

4. **Start server:**
```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## API Endpoints

Once deployed, access:

- **API Documentation:** `/api/v1/docs`
- **Alternative Docs:** `/api/v1/redoc`
- **Health Check:** `/health`
- **Root:** `/`

---

## Testing the Conflict Search

### Example 1: Search by person name (with accents)
```bash
curl -X POST "https://your-api.railway.app/api/v1/conflictos/verificar" \
  -H "Content-Type: application/json" \
  -H "X-Firm-ID: 1" \
  -d '{
    "nombre": "José",
    "apellido": "González",
    "segundo_apellido": "Rivera"
  }'
```

### Example 2: Search by company
```bash
curl -X POST "https://your-api.railway.app/api/v1/conflictos/verificar" \
  -H "Content-Type: application/json" \
  -H "X-Firm-ID: 1" \
  -d '{
    "nombre_empresa": "Corporación ABC"
  }'
```

### Expected Response
```json
{
  "termino_busqueda": "José González Rivera",
  "total_conflictos": 2,
  "conflictos": [
    {
      "cliente_id": 5,
      "cliente_nombre": "Jose Gonzalez Rivera",
      "asunto_id": 12,
      "asunto_nombre": "González vs. State",
      "estado_asunto": "activo",
      "tipo_coincidencia": "cliente_persona",
      "similitud_score": 95.5,
      "nivel_confianza": "alta",
      "campo_coincidente": "cliente_nombre"
    },
    {
      "cliente_id": 8,
      "cliente_nombre": "Maria Rodriguez",
      "asunto_id": 23,
      "asunto_nombre": "Rodriguez vs. Municipality",
      "estado_asunto": "cerrado",
      "tipo_coincidencia": "parte_relacionada_demandado",
      "similitud_score": 73.2,
      "nivel_confianza": "media",
      "campo_coincidente": "parte_relacionada (demandado: José González)"
    }
  ],
  "mensaje": "Se encontraron 2 posible(s) conflicto(s): 1 alta confianza, 1 media confianza"
}
```

---

## Fuzzy Matching Features

### ✅ Implemented

1. **Exact Match (Case-Insensitive, Accent-Insensitive)**
   - José = Jose = JOSÉ = jose
   - María = Maria = MARIA = maria
   - González = Gonzalez = GONZÁLEZ

2. **Fuzzy Match (>70% similarity)**
   - Handles typos: "Gonzalez" matches "Gonsalez" (90%)
   - Word order: "Juan García" matches "García Juan" (100%)

3. **Search Scope**
   - ✅ Clients (nombre + apellido + segundo_apellido)
   - ✅ Companies (nombre_empresa)
   - ✅ Related parties in ALL matters (active, closed, pending, archived)

4. **Confidence Scoring**
   - **High:** ≥90% similarity (exact or near-exact match)
   - **Medium:** 70-89% similarity (fuzzy match)

5. **Match Context**
   - Shows which field matched (cliente_nombre, empresa_nombre, parte_relacionada)
   - Shows relationship type for related parties

---

## Database Schema Updates

### New Field: `segundo_apellido`

The `clientes` table now includes:
- `segundo_apellido` VARCHAR(100) - Second surname (common in Puerto Rico)

**Migration:** Run `alembic upgrade head` to apply

---

## Troubleshooting

### Issue: "Module not found" errors
**Solution:** Ensure you're in the `conflict_api` directory when running the app

### Issue: Database connection errors
**Solution:** Verify `DATABASE_URL` in Railway dashboard or `.env` file

### Issue: Migration errors
**Solution:**
```bash
railway run alembic downgrade -1
railway run alembic upgrade head
```

---

## Next Steps

After deployment:

1. Create a law firm (firma) via `/api/v1/firmas`
2. Add clients via `/api/v1/clientes` with `X-Firm-ID` header
3. Add legal matters via `/api/v1/asuntos`
4. Add related parties via `/api/v1/partes-relacionadas`
5. Test conflict checking via `/api/v1/conflictos/verificar`

---

## Support

For issues or questions:
- Check Railway logs: `railway logs`
- Check API docs: `https://your-api.railway.app/api/v1/docs`
- Review error responses for debugging information
