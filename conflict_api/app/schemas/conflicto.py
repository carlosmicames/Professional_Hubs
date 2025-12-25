"""
Schemas para búsqueda de Conflictos de Interés.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.asunto import EstadoAsunto


class BusquedaConflicto(BaseModel):
    """Schema para búsqueda de conflictos."""
    nombre: Optional[str] = Field(None, description="Nombre a buscar")
    apellido: Optional[str] = Field(None, description="Apellido a buscar")
    nombre_empresa: Optional[str] = Field(None, description="Nombre de empresa a buscar")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "nombre": "Juan",
                    "apellido": "García"
                },
                {
                    "nombre_empresa": "Corporación ABC"
                }
            ]
        }


class ConflictoEncontrado(BaseModel):
    """Representa un conflicto encontrado."""
    cliente_id: int = Field(..., description="ID del cliente")
    cliente_nombre: str = Field(..., description="Nombre completo del cliente")
    asunto_id: int = Field(..., description="ID del asunto")
    asunto_nombre: str = Field(..., description="Nombre del asunto")
    estado_asunto: EstadoAsunto = Field(..., description="Estado del asunto")
    tipo_coincidencia: str = Field(..., description="Tipo de coincidencia encontrada")
    
    class Config:
        from_attributes = True


class ResultadoConflicto(BaseModel):
    """Resultado completo de búsqueda de conflictos."""
    termino_busqueda: str = Field(..., description="Término usado en la búsqueda")
    total_conflictos: int = Field(..., description="Total de conflictos encontrados")
    conflictos: List[ConflictoEncontrado] = Field(
        default_factory=list, 
        description="Lista de conflictos encontrados"
    )
    mensaje: str = Field(..., description="Mensaje descriptivo del resultado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "termino_busqueda": "Juan García",
                "total_conflictos": 2,
                "conflictos": [
                    {
                        "cliente_id": 1,
                        "cliente_nombre": "Juan García",
                        "asunto_id": 5,
                        "asunto_nombre": "García vs. Pérez",
                        "estado_asunto": "activo",
                        "tipo_coincidencia": "cliente_existente"
                    }
                ],
                "mensaje": "Se encontraron 2 posibles conflictos de interés"
            }
        }