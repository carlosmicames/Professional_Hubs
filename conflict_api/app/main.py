"""
Aplicación principal FastAPI - Professional Hubs Conflict API.
Sistema de verificación de conflictos de interés para bufetes de abogados.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import firmas, clientes, asuntos, partes_relacionadas, conflictos

settings = get_settings()

# Inicializar aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description="API para verificación de conflictos de interés en bufetes de abogados de Puerto Rico",
    version=settings.api_version,
    docs_url=f"/api/{settings.api_version}/docs",
    redoc_url=f"/api/{settings.api_version}/redoc",
    openapi_url=f"/api/{settings.api_version}/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
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


@app.get("/")
async def root():
    """Endpoint raíz - información básica de la API."""
    return {
        "app": settings.app_name,
        "version": settings.api_version,
        "docs": f"/api/{settings.api_version}/docs",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check para monitoreo."""
    return {
        "status": "healthy",
        "service": "conflict-api"
    }
