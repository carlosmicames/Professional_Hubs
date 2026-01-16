"""
Schemas para Firma (Bufete).
Updated with additional company fields for Professional Hubs.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class FirmaBase(BaseModel):
    """Campos base de Firma."""
    nombre: Optional[str] = Field(None, max_length=255, description="Nombre del bufete/empresa")
    direccion: Optional[str] = Field(None, max_length=500, description="Direccion fisica")
    direccion_postal: Optional[str] = Field(None, max_length=500, description="Direccion postal")
    telefono: Optional[str] = Field(None, max_length=50, description="Telefono")


class FirmaCreate(FirmaBase):
    """Schema para crear una firma."""
    pass


class FirmaUpdate(BaseModel):
    """Schema para actualizar una firma (all fields optional)."""
    nombre: Optional[str] = Field(None, max_length=255, description="Nombre del bufete/empresa")
    direccion: Optional[str] = Field(None, max_length=500, description="Direccion fisica")
    direccion_postal: Optional[str] = Field(None, max_length=500, description="Direccion postal")
    telefono: Optional[str] = Field(None, max_length=50, description="Telefono")


class FirmaResponse(BaseModel):
    """Schema de respuesta de Firma."""
    id: int
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    direccion_postal: Optional[str] = None
    telefono: Optional[str] = None
    esta_activo: bool
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)
