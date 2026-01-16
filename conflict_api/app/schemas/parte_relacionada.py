"""
Schemas para Parte Relacionada (Related Party).
Updated to use string literals instead of PostgreSQL ENUM.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


# Valid tipo_relacion values (matches model)
TipoRelacionType = Literal[
    "DEMANDANTE", "DEMANDADO", "PARTE_CONTRARIA", 
    "CO_DEMANDADO", "CONYUGE", "SUBSIDIARIA", "EMPRESA_MATRIZ"
]


class ParteRelacionadaBase(BaseModel):
    """Campos base de Parte Relacionada."""
    nombre: str = Field(..., min_length=1, max_length=255, description="Nombre de la parte")
    tipo_relacion: TipoRelacionType = Field(..., description="Tipo de relación con el asunto")


class ParteRelacionadaCreate(ParteRelacionadaBase):
    """Schema para crear una parte relacionada."""
    asunto_id: int = Field(..., description="ID del asunto relacionado")


class ParteRelacionadaUpdate(BaseModel):
    """Schema para actualizar una parte relacionada."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    tipo_relacion: Optional[TipoRelacionType] = None


class ParteRelacionadaResponse(BaseModel):
    """Schema de respuesta de Parte Relacionada."""
    id: int
    asunto_id: int
    nombre: str
    tipo_relacion: str  # String instead of enum
    esta_activo: bool
    creado_en: datetime
    actualizado_en: datetime
    
    class Config:
        from_attributes = True


class ParteRelacionadaConAsuntoResponse(ParteRelacionadaResponse):
    """Schema con información del asunto."""
    asunto_nombre: str = Field(..., description="Nombre del asunto")
    cliente_nombre: str = Field(..., description="Nombre del cliente")
    
    class Config:
        from_attributes = True