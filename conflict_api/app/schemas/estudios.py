"""
Schemas para Estudios (Studies/Education).
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class EstudiosBase(BaseModel):
    """Campos base de Estudios."""
    universidad: Optional[str] = Field(None, max_length=255, description="Universidad de estudios generales")
    ano_graduacion: Optional[str] = Field(None, max_length=50, description="Ano de graduacion universidad")
    escuela_derecho: Optional[str] = Field(None, max_length=255, description="Escuela de derecho")
    ano_graduacion_derecho: Optional[str] = Field(None, max_length=50, description="Ano de graduacion derecho")


class EstudiosCreate(EstudiosBase):
    """Schema para crear estudios."""
    pass


class EstudiosUpdate(EstudiosBase):
    """Schema para actualizar estudios (all fields optional)."""
    pass


class EstudiosResponse(EstudiosBase):
    """Schema de respuesta de Estudios."""
    id: int
    firma_id: int
    esta_activo: bool
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)
