"""
Schemas para Firma (Bufete).
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FirmaBase(BaseModel):
    """Campos base de Firma."""
    nombre: str = Field(..., min_length=1, max_length=255, description="Nombre del bufete")


class FirmaCreate(FirmaBase):
    """Schema para crear una firma."""
    pass


class FirmaUpdate(BaseModel):
    """Schema para actualizar una firma."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=255, description="Nombre del bufete")


class FirmaResponse(FirmaBase):
    """Schema de respuesta de Firma."""
    id: int
    esta_activo: bool
    creado_en: datetime
    actualizado_en: datetime
    
    class Config:
        from_attributes = True