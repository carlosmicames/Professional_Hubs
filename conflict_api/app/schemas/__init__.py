"""
Schemas Pydantic para validación y serialización.
"""

from app.schemas.firma import FirmaCreate, FirmaUpdate, FirmaResponse
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse
from app.schemas.asunto import AsuntoCreate, AsuntoUpdate, AsuntoResponse
from app.schemas.parte_relacionada import ParteRelacionadaCreate, ParteRelacionadaUpdate, ParteRelacionadaResponse
from app.schemas.conflicto import BusquedaConflicto, ResultadoConflicto, ConflictoEncontrado

__all__ = [
    "FirmaCreate", "FirmaUpdate", "FirmaResponse",
    "ClienteCreate", "ClienteUpdate", "ClienteResponse",
    "AsuntoCreate", "AsuntoUpdate", "AsuntoResponse",
    "ParteRelacionadaCreate", "ParteRelacionadaUpdate", "ParteRelacionadaResponse",
    "BusquedaConflicto", "ResultadoConflicto", "ConflictoEncontrado",
]