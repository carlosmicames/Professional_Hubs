"""
Schemas Pydantic para validacion y serializacion.
"""

from app.schemas.firma import FirmaCreate, FirmaUpdate, FirmaResponse
from app.schemas.cliente import (
    ClienteCreate, ClienteUpdate, ClienteResponse,
    ClienteBulkUpdateItem, ClienteBulkUpdateRequest
)
from app.schemas.asunto import AsuntoCreate, AsuntoUpdate, AsuntoResponse
from app.schemas.parte_relacionada import ParteRelacionadaCreate, ParteRelacionadaUpdate, ParteRelacionadaResponse
from app.schemas.conflicto import BusquedaConflicto, ResultadoConflicto, ConflictoEncontrado
from app.schemas.perfil import PerfilCreate, PerfilUpdate, PerfilResponse
from app.schemas.estudios import EstudiosCreate, EstudiosUpdate, EstudiosResponse
from app.schemas.areas_practica import AreasPracticaCreate, AreasPracticaUpdate, AreasPracticaResponse
from app.schemas.ubicacion import UbicacionCreate, UbicacionUpdate, UbicacionResponse
from app.schemas.planes import PlanesCreate, PlanesUpdate, PlanesResponse, PlanSelectionResponse

__all__ = [
    "FirmaCreate", "FirmaUpdate", "FirmaResponse",
    "ClienteCreate", "ClienteUpdate", "ClienteResponse",
    "ClienteBulkUpdateItem", "ClienteBulkUpdateRequest",
    "AsuntoCreate", "AsuntoUpdate", "AsuntoResponse",
    "ParteRelacionadaCreate", "ParteRelacionadaUpdate", "ParteRelacionadaResponse",
    "BusquedaConflicto", "ResultadoConflicto", "ConflictoEncontrado",
    "PerfilCreate", "PerfilUpdate", "PerfilResponse",
    "EstudiosCreate", "EstudiosUpdate", "EstudiosResponse",
    "AreasPracticaCreate", "AreasPracticaUpdate", "AreasPracticaResponse",
    "UbicacionCreate", "UbicacionUpdate", "UbicacionResponse",
    "PlanesCreate", "PlanesUpdate", "PlanesResponse", "PlanSelectionResponse",
]
