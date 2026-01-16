"""
Schemas para Ubicacion (Geographic Location).
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class UbicacionBase(BaseModel):
    """Campos base de Ubicacion."""
    pais: Optional[str] = Field("Puerto Rico", max_length=100, description="Pais")
    municipio: Optional[str] = Field(None, max_length=100, description="Municipio")


class UbicacionCreate(UbicacionBase):
    """Schema para crear ubicacion."""
    pass


class UbicacionUpdate(UbicacionBase):
    """Schema para actualizar ubicacion."""
    pass


class UbicacionResponse(UbicacionBase):
    """Schema de respuesta de Ubicacion."""
    id: int
    firma_id: int
    esta_activo: bool
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)
