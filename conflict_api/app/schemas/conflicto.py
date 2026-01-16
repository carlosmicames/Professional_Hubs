"""
Schemas para búsqueda de Conflictos de Interés.
Updated to use string instead of PostgreSQL ENUM.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class BusquedaConflicto(BaseModel):
    """Schema para búsqueda de conflictos."""
    nombre: Optional[str] = Field(None, description="Nombre a buscar")
    apellido: Optional[str] = Field(None, description="Primer apellido a buscar")
    segundo_apellido: Optional[str] = Field(None, description="Segundo apellido a buscar")
    nombre_empresa: Optional[str] = Field(None, description="Nombre de empresa a buscar")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "nombre": "Juan",
                    "apellido": "García",
                    "segundo_apellido": "Rivera"
                },
                {
                    "nombre": "José",
                    "apellido": "González"
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
    estado_asunto: str = Field(..., description="Estado del asunto: ACTIVO, CERRADO, PENDIENTE, ARCHIVADO")
    tipo_coincidencia: str = Field(..., description="Tipo de coincidencia encontrada")
    similitud_score: float = Field(..., ge=0.0, le=100.0, description="Porcentaje de similitud (0-100)")
    nivel_confianza: str = Field(..., description="Nivel de confianza: 'alta' (>=90%), 'media' (70-89%)")
    campo_coincidente: str = Field(..., description="Campo que generó la coincidencia (ej: 'cliente_nombre', 'parte_relacionada')")
    
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
                        "estado_asunto": "ACTIVO",
                        "tipo_coincidencia": "cliente_existente",
                        "similitud_score": 95.5,
                        "nivel_confianza": "alta",
                        "campo_coincidente": "cliente_nombre"
                    }
                ],
                "mensaje": "Se encontraron 2 posibles conflictos de interés"
            }
        }