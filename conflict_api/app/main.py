"""
Aplicación principal FastAPI - Professional Hubs Conflict API.
Sistema de verificación de conflictos de interés para bufetes de abogados.
PLUS: Sistema automatizado de facturación y cobros.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.routers import firmas, clientes, asuntos, partes_relacionadas, conflictos, calls, billing
from app.services.billing_scheduler import billing_scheduler

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager para iniciar/detener servicios de background.
    """
    # Startup: Iniciar el billing scheduler
    print("\n" + "="*60)
    print("Starting Professional Hubs API")
    print("="*60)
    
    billing_scheduler.start()
    print("Billing Reminder Scheduler started")
    
    yield
    
    # Shutdown: Detener scheduler
    billing_scheduler.stop()
    print("Billing Reminder Scheduler stopped")
    print("="*60 + "\n")


# Inicializar aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description="API para verificación de conflictos de interés y gestión automatizada de facturación para bufetes de abogados de Puerto Rico",
    version=settings.api_version,
    docs_url=f"/api/{settings.api_version}/docs",
    redoc_url=f"/api/{settings.api_version}/redoc",
    openapi_url=f"/api/{settings.api_version}/openapi.json",
    lifespan=lifespan  # Enable lifespan events
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers existentes
app.include_router(
    firmas.router,
    prefix=f"/api/{settings.api_version}",
    tags=["Firmas"]
)

app.include_router(
    clientes.router,
    prefix=f"/api/{settings.api_version}",
    tags=["Clientes"]
)

app.include_router(
    asuntos.router,
    prefix=f"/api/{settings.api_version}",
    tags=["Asuntos"]
)

app.include_router(
    partes_relacionadas.router,
    prefix=f"/api/{settings.api_version}",
    tags=["Partes Relacionadas"]
)

app.include_router(
    conflictos.router,
    prefix=f"/api/{settings.api_version}",
    tags=["Verificación de Conflictos"]
)

app.include_router(
    calls.router,
    prefix=f"/api/{settings.api_version}",
    tags=["AI Call Agent"]
)

# NEW: Registrar billing router
app.include_router(
    billing.router,
    prefix=f"/api/{settings.api_version}",
    tags=["Billing & Collections"]
)


@app.get("/")
async def root():
    """Endpoint raíz - información básica de la API."""
    return {
        "app": settings.app_name,
        "version": settings.api_version,
        "features": [
            "Conflict of Interest Checking",
            "AI Call Agent",
            "Automated Billing & Collections",
            "AI-Powered Resignation Letters"
        ],
        "docs": f"/api/{settings.api_version}/docs",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check para monitoreo."""
    return {
        "status": "healthy",
        "service": "professional-hubs-api",
        "billing_scheduler": "running" if billing_scheduler.is_running else "stopped"
    }