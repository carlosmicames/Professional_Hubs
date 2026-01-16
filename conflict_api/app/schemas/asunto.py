"""
Schemas para Asunto (Matter).
Updated to use string literals instead of PostgreSQL ENUM.
"""

from datetime import datetime, date
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


# Valid estado values (matches model)
EstadoAsuntoType = Literal["ACTIVO", "CERRADO", "PENDIENTE", "ARCHIVADO"]


class AsuntoBase(BaseModel):
    """Campos base de Asunto."""
    nombre_asunto: str = Field(..., min_length=1, max_length=500, description="Nombre o descripción del asunto")
    fecha_apertura: Optional[date] = Field(None, description="Fecha de apertura (default: hoy)")
    estado: Optional[EstadoAsuntoType] = Field("ACTIVO", description="Estado del asunto")


class AsuntoCreate(AsuntoBase):
    """Schema para crear un asunto."""
    cliente_id: int = Field(..., description="ID del cliente principal")


class AsuntoUpdate(BaseModel):
    """Schema para actualizar un asunto."""
    nombre_asunto: Optional[str] = Field(None, min_length=1, max_length=500)
    fecha_apertura: Optional[date] = None
    estado: Optional[EstadoAsuntoType] = None


class AsuntoResponse(BaseModel):
    """Schema de respuesta de Asunto."""
    id: int
    cliente_id: int
    nombre_asunto: str
    fecha_apertura: date
    estado: str  # String instead of enum
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