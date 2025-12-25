"""
Schemas para Parte Relacionada (Related Party).
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.parte_relacionada import TipoRelacion


class ParteRelacionadaBase(BaseModel):
    """Campos base de Parte Relacionada."""
    nombre: str = Field(..., min_length=1, max_length=255, description="Nombre de la parte")
    tipo_relacion: TipoRelacion = Field(..., description="Tipo de relación con el asunto")


class ParteRelacionadaCreate(ParteRelacionadaBase):
    """Schema para crear una parte relacionada."""
    asunto_id: int = Field(..., description="ID del asunto relacionado")


class ParteRelacionadaUpdate(BaseModel):
    """Schema para actualizar una parte relacionada."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    tipo_relacion: Optional[TipoRelacion] = None


class ParteRelacionadaResponse(BaseModel):
    """Schema de respuesta de Parte Relacionada."""
    id: int
    asunto_id: int
    nombre: str
    tipo_relacion: TipoRelacion
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