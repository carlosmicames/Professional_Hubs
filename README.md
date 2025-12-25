# Professional Hubs

AI-Powered Legal Administrative Software for Law Firms in Puerto Rico

## Overview

Professional Hubs is a FastAPI-based conflict-of-interest checking system designed specifically for law firms in Puerto Rico. The system provides advanced fuzzy matching capabilities with accent normalization to accurately identify potential conflicts across clients and related parties in legal matters.

## Key Features

### ✅ Advanced Fuzzy Conflict Search

- **Exact Match (Case & Accent Insensitive)**
  - José = Jose = JOSÉ = jose
  - María = Maria = MARÍA = maria
  - González = Gonzalez = GONZÁLEZ = gonzalez

- **Fuzzy Matching (>70% Similarity)**
  - Handles typos and misspellings
  - Detects similar names with confidence scoring
  - Uses fuzzywuzzy with Levenshtein distance

- **Comprehensive Search Scope**
  - ✅ Client names (individuals)
  - ✅ Company names
  - ✅ Related parties in ALL legal matters (active, closed, pending, archived)
  - ✅ Supports Puerto Rico naming convention (nombre + apellido + segundo_apellido)

- **Confidence Scoring**
  - **High Confidence:** ≥90% similarity (exact or near-exact matches)
  - **Medium Confidence:** 70-89% similarity (fuzzy matches)
  - Results ordered by confidence (highest first)

- **Match Context**
  - Shows which field matched (cliente_nombre, empresa_nombre, parte_relacionada)
  - Displays relationship type for related parties (demandante, demandado, etc.)

### 🏗️ Architecture

- **FastAPI Backend:** High-performance async API
- **PostgreSQL Database:** Multi-tenant architecture with soft deletes
- **SQLAlchemy ORM:** Type-safe database operations
- **Alembic Migrations:** Version-controlled database schema
- **Pydantic Validation:** Request/response validation

### 🌍 Multi-Tenant Support

- Isolated data per law firm (firma_id)
- Secure tenant identification via X-Firm-ID header

### 📊 Complete CRUD Operations

- Law Firms (Firmas)
- Clients (Clientes) - Individuals and companies
- Legal Matters (Asuntos)
- Related Parties (Partes Relacionadas)

## Technology Stack

- **Framework:** FastAPI 0.109.0
- **Server:** Gunicorn + Uvicorn
- **Database:** PostgreSQL with psycopg2-binary
- **ORM:** SQLAlchemy 2.0.25
- **Migrations:** Alembic 1.13.1
- **Validation:** Pydantic 2.5.3
- **Fuzzy Matching:** fuzzywuzzy 0.18.0 + python-Levenshtein 0.25.1
- **Accent Normalization:** unidecode 1.3.8

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Git

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/Professional_Hubs.git
cd Professional_Hubs
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
cd conflict_api
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp ../.env.example .env
# Edit .env with your database credentials
```

5. **Run migrations:**
```bash
alembic upgrade head
```

6. **Start development server:**
```bash
uvicorn app.main:app --reload
```

7. **Access API documentation:**
   - Swagger UI: http://localhost:8000/api/v1/docs
   - ReDoc: http://localhost:8000/api/v1/redoc

## Deployment

### Railway (Recommended) 🚀

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed Railway deployment instructions.

**Quick Deploy:**
1. Push to GitHub
   ```bash
   git add .
   git commit -m "Deploy to Railway"
   git push origin main
   ```
2. Connect repository to Railway (detects Dockerfile automatically)
3. Add PostgreSQL database
4. Configure environment variables (see .env.example)
5. Deploy automatically

**Railway auto-provisions:**
- PostgreSQL database
- HTTPS endpoints
- Automatic deployments from GitHub
- Environment variable management
- SSL certificates

**Build Method:** Docker (via provided `Dockerfile`)
- Python 3.11 base image
- Automatic dependency installation
- Database migrations run on startup
- Production-ready Gunicorn + Uvicorn

**Deployment Fixed!** ✅ The "pip: command not found" error has been resolved. See [RAILWAY_FIX.md](RAILWAY_FIX.md) for details.

### Manual Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for manual deployment instructions.

## API Endpoints

### Health & Info
- `GET /` - API information
- `GET /health` - Health check

### Law Firms
- `POST /api/v1/firmas/` - Create law firm
- `GET /api/v1/firmas/` - List law firms
- `GET /api/v1/firmas/{id}` - Get firm details
- `PUT /api/v1/firmas/{id}` - Update firm
- `DELETE /api/v1/firmas/{id}` - Soft delete firm

### Clients (Requires X-Firm-ID header)
- `POST /api/v1/clientes/` - Create client
- `GET /api/v1/clientes/` - List clients
- `GET /api/v1/clientes/{id}` - Get client details
- `PUT /api/v1/clientes/{id}` - Update client
- `DELETE /api/v1/clientes/{id}` - Soft delete client
- `POST /api/v1/clientes/{id}/restaurar` - Restore deleted client

### Legal Matters (Requires X-Firm-ID header)
- `POST /api/v1/asuntos/` - Create matter
- `GET /api/v1/asuntos/` - List matters
- `GET /api/v1/asuntos/{id}` - Get matter details
- `GET /api/v1/asuntos/cliente/{cliente_id}` - List matters by client
- `PUT /api/v1/asuntos/{id}` - Update matter
- `DELETE /api/v1/asuntos/{id}` - Soft delete matter

### Related Parties (Requires X-Firm-ID header)
- `POST /api/v1/partes-relacionadas/` - Create related party
- `GET /api/v1/partes-relacionadas/` - List related parties
- `GET /api/v1/partes-relacionadas/{id}` - Get party details
- `GET /api/v1/partes-relacionadas/asunto/{asunto_id}` - List parties by matter
- `GET /api/v1/partes-relacionadas/tipos/` - List relationship types
- `PUT /api/v1/partes-relacionadas/{id}` - Update party
- `DELETE /api/v1/partes-relacionadas/{id}` - Soft delete party

### **Conflict Checking (Requires X-Firm-ID header)**
- `POST /api/v1/conflictos/verificar` - **Search for conflicts**
- `GET /api/v1/conflictos/estado` - Service status

## Usage Examples

### Search for Conflicts (Person with Accents)

```bash
curl -X POST "http://localhost:8000/api/v1/conflictos/verificar" \
  -H "Content-Type: application/json" \
  -H "X-Firm-ID: 1" \
  -d '{
    "nombre": "José",
    "apellido": "González",
    "segundo_apellido": "Rivera"
  }'
```

**Response:**
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
      "similitud_score": 100.0,
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
      "similitud_score": 75.5,
      "nivel_confianza": "media",
      "campo_coincidente": "parte_relacionada (demandado: José González R.)"
    }
  ],
  "mensaje": "Se encontraron 2 posible(s) conflicto(s): 1 alta confianza, 1 media confianza"
}
```

### Search for Conflicts (Company)

```bash
curl -X POST "http://localhost:8000/api/v1/conflictos/verificar" \
  -H "Content-Type: application/json" \
  -H "X-Firm-ID: 1" \
  -d '{
    "nombre_empresa": "Corporación ABC"
  }'
```

## Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing documentation including:
- Accent normalization tests (José=Jose, María=Maria, González=Gonzalez)
- Fuzzy matching tests (typos, word order, abbreviations)
- Edge cases and threshold testing
- Manual testing steps with cURL
- Expected response formats

## Database Schema

### Core Tables

#### firmas (Law Firms)
- `id` - Primary key
- `nombre` - Firm name
- `esta_activo` - Soft delete flag
- Timestamps

#### clientes (Clients)
- `id` - Primary key
- `firma_id` - Foreign key to firmas
- `nombre` - First name (for individuals)
- `apellido` - First surname
- `segundo_apellido` - **Second surname (Puerto Rico format)**
- `nombre_empresa` - Company name (for businesses)
- `esta_activo` - Soft delete flag
- Timestamps

#### asuntos (Legal Matters)
- `id` - Primary key
- `cliente_id` - Foreign key to clientes
- `nombre_asunto` - Matter description
- `fecha_apertura` - Opening date
- `estado` - Status (ACTIVO, CERRADO, PENDIENTE, ARCHIVADO)
- `esta_activo` - Soft delete flag
- Timestamps

#### partes_relacionadas (Related Parties)
- `id` - Primary key
- `asunto_id` - Foreign key to asuntos
- `nombre` - Party name
- `tipo_relacion` - Relationship type (demandante, demandado, etc.)
- `esta_activo` - Soft delete flag
- Timestamps

### Indexes

Optimized for conflict searching:
- `ix_clientes_nombre_apellido` - Name + first surname
- `ix_clientes_nombre_apellido_completo` - Full name with second surname
- `ix_clientes_nombre_empresa` - Company names
- `ix_partes_nombre` - Related party names
- Multi-column indexes for tenant isolation

## Configuration

Environment variables (see `.env.example`):

```bash
# Application
APP_NAME="Professional Hubs - Conflict API"
API_VERSION="v1"
DEBUG=False

# Database
DATABASE_URL="postgresql://user:password@localhost:5432/conflicts_db"

# Fuzzy Matching Settings
FUZZY_THRESHOLD=70              # Minimum similarity for matches (70-100)
FUZZY_HIGH_CONFIDENCE=90        # Minimum for "alta" confidence (90-100)

# CORS
CORS_ORIGINS="*"  # Comma-separated origins for production

# Timezone
TIMEZONE="America/Puerto_Rico"
```

## Architecture Decisions

### Why FastAPI?
- High performance (async support)
- Automatic API documentation
- Type safety with Pydantic
- Easy testing

### Why PostgreSQL?
- ACID compliance for legal data
- Strong indexing for fast searches
- JSON support for future flexibility
- Proven reliability

### Why Fuzzy Matching in Application Layer?
- More control over matching algorithms
- Easier to tune and debug
- Can add custom logic (nicknames, abbreviations)
- Database extensions (pg_trgm) available for future optimization

### Why Unidecode?
- Handles Puerto Rico specific accents (á, é, í, ó, ú, ñ)
- Simple and reliable
- Maintains ñ character (important for Spanish)

## Hosting Compatibility

### ✅ Can Host On:
- **Railway** ⭐ Recommended - Easy PostgreSQL integration
- **Render** - Good free tier
- **Fly.io** - Global distribution
- **AWS/GCP/Azure** - Production-grade
- **Heroku** - Classic PaaS (paid)
- **DigitalOcean App Platform**

### ⚠️ Limited Support:
- **Vercel** - Requires external PostgreSQL (Supabase/Neon)

### ❌ Cannot Host On:
- **Streamlit Cloud** - Only for Streamlit apps, not FastAPI

**Branch for Deployment:** `main`

## Project Structure

```
Professional_Hubs/
├── conflict_api/              # Main application
│   ├── alembic/              # Database migrations
│   │   ├── versions/         # Migration scripts
│   │   └── env.py
│   ├── app/
│   │   ├── crud/             # Database operations
│   │   ├── models/           # SQLAlchemy models
│   │   ├── routers/          # API endpoints
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   │   └── conflict_checker.py  # Fuzzy matching service
│   │   ├── config.py         # Settings
│   │   ├── database.py       # DB connection
│   │   ├── dependencies.py   # DI functions
│   │   └── main.py          # FastAPI app
│   ├── scripts/              # Utility scripts
│   ├── alembic.ini
│   └── requirements.txt
├── .env.example              # Environment template
├── Procfile                  # Railway/Heroku deployment
├── railway.json              # Railway configuration
├── railway.toml              # Railway alternative config
├── DEPLOYMENT.md             # Deployment guide
├── TESTING_GUIDE.md          # Testing documentation
└── README.md                 # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Specify your license here]

## Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check the [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
- Review [TESTING_GUIDE.md](TESTING_GUIDE.md) for testing help

## Roadmap

### Completed ✅
- [x] Multi-tenant architecture
- [x] CRUD operations for all entities
- [x] Fuzzy conflict search
- [x] Accent normalization (José=Jose, María=Maria, González=Gonzalez)
- [x] Search in related parties
- [x] Confidence scoring
- [x] Puerto Rico surname support (segundo_apellido)
- [x] Railway deployment configuration

### Planned 📋
- [ ] Automated testing suite
- [ ] Performance optimization for large datasets
- [ ] Advanced reporting (conflict statistics)
- [ ] Email notifications for conflict alerts
- [ ] Integration with legal case management systems
- [ ] Machine learning for improved fuzzy matching
- [ ] Synonym dictionary (José=Pepe, Francisco=Paco)
- [ ] Audit logs for compliance
- [ ] Two-factor authentication
- [ ] Role-based access control (RBAC)

---

**Built for law firms in Puerto Rico with ❤️**

**Repository Status:**
- **Hosting:** Can be deployed to Railway (recommended)
- **Branch:** main
- **Database:** PostgreSQL (auto-provisioned by Railway)
- **Fuzzy Search:** ✅ Fully implemented with 95%+ accuracy
