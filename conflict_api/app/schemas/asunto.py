"""
Schemas para Asunto (Matter).
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.asunto import EstadoAsunto


class AsuntoBase(BaseModel):
    """Campos base de Asunto."""
    nombre_asunto: str = Field(..., min_length=1, max_length=500, description="Nombre o descripción del asunto")
    fecha_apertura: Optional[date] = Field(None, description="Fecha de apertura (default: hoy)")
    estado: Optional[EstadoAsunto] = Field(EstadoAsunto.ACTIVO, description="Estado del asunto")


class AsuntoCreate(AsuntoBase):
    """Schema para crear un asunto."""
    cliente_id: int = Field(..., description="ID del cliente principal")


class AsuntoUpdate(BaseModel):
    """Schema para actualizar un asunto."""
    nombre_asunto: Optional[str] = Field(None, min_length=1, max_length=500)
    fecha_apertura: Optional[date] = None
    estado: Optional[EstadoAsunto] = None


class AsuntoResponse(BaseModel):
    """Schema de respuesta de Asunto."""
    id: int
    cliente_id: int
    nombre_asunto: str
    fecha_apertura: date
    estado: EstadoAsunto
    esta_activo: bool
    creado_en: datetime
    actualizado_en: datetime
    
    class Config:
        from_attributes = True


class AsuntoConClienteResponse(AsuntoResponse):
    """Schema de Asunto con información del cliente."""
    cliente_nombre: str = Field(..., description="Nombre del cliente")
    
    class Config:
        from_attributes = True