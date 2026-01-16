"""
Schemas para Cliente.
Updated with address fields and billing flags for Professional Hubs.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ClienteBase(BaseModel):
    """Campos base de Cliente."""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del cliente")
    apellido: str = Field(..., min_length=1, max_length=100, description="Apellido del cliente")
    email: str = Field(..., min_length=1, max_length=255, description="Email del cliente")
    telefono: str = Field(..., min_length=1, max_length=50, description="Telefono del cliente")
    direccion: str = Field(..., min_length=1, max_length=500, description="Direccion fisica")
    segundo_apellido: Optional[str] = Field(None, max_length=100, description="Segundo apellido")
    nombre_empresa: Optional[str] = Field(None, max_length=255, description="Nombre de empresa")
    direccion_postal: Optional[str] = Field(None, max_length=500, description="Direccion postal")


class ClienteCreate(ClienteBase):
    """Schema para crear un cliente."""
    pass


class ClienteUpdate(BaseModel):
    """Schema para actualizar un cliente (all fields optional)."""
    nombre: Optional[str] = Field(None, max_length=100, description="Nombre del cliente")
    apellido: Optional[str] = Field(None, max_length=100, description="Apellido del cliente")
    email: Optional[str] = Field(None, max_length=255, description="Email del cliente")
    telefono: Optional[str] = Field(None, max_length=50, description="Telefono del cliente")
    direccion: Optional[str] = Field(None, max_length=500, description="Direccion fisica")
    segundo_apellido: Optional[str] = Field(None, max_length=100, description="Segundo apellido")
    nombre_empresa: Optional[str] = Field(None, max_length=255, description="Nombre de empresa")
    direccion_postal: Optional[str] = Field(None, max_length=500, description="Direccion postal")
    has_late_invoices: Optional[bool] = Field(None, description="Flag for late invoices")
    has_potential_conflict: Optional[bool] = Field(None, description="Flag for potential conflict")


class ClienteResponse(BaseModel):
    """Schema de respuesta de Cliente."""
    id: int
    firma_id: int
    nombre: str
    apellido: str
    email: str
    telefono: str
    direccion: str
    segundo_apellido: Optional[str] = None
    nombre_empresa: Optional[str] = None
    direccion_postal: Optional[str] = None
    has_late_invoices: bool = False
    has_potential_conflict: bool = False
    nombre_completo: str = Field(..., description="Nombre completo calculado")
    esta_activo: bool
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class ClienteBulkUpdateItem(BaseModel):
    """Single item for bulk update."""
    id: int
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    segundo_apellido: Optional[str] = None
    nombre_empresa: Optional[str] = None
    direccion_postal: Optional[str] = None


class ClienteBulkUpdateRequest(BaseModel):
    """Request for bulk update of clients."""
    updates: List[ClienteBulkUpdateItem]
