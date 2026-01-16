"""
Schemas para Areas de Practica (Practice Areas).
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class AreasPracticaBase(BaseModel):
    """Campos base de Areas de Practica."""
    areas: Optional[List[str]] = Field(default_factory=list, description="Lista de areas de practica")


class AreasPracticaCreate(AreasPracticaBase):
    """Schema para crear areas de practica."""
    pass


class AreasPracticaUpdate(AreasPracticaBase):
    """Schema para actualizar areas de practica."""
    pass


class AreasPracticaResponse(AreasPracticaBase):
    """Schema de respuesta de Areas de Practica."""
    id: int
    firma_id: int
    esta_activo: bool
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)
