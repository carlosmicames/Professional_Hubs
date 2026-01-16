"""
Schemas para Perfil (Profile).
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PerfilBase(BaseModel):
    """Campos base de Perfil."""
    numero_rua: Optional[int] = Field(None, description="Numero de RUA")
    direccion: Optional[str] = Field(None, max_length=500, description="Direccion fisica")
    direccion_postal: Optional[str] = Field(None, max_length=500, description="Direccion postal")
    telefono_celular: Optional[str] = Field(None, max_length=50, description="Telefono celular")
    telefono: Optional[str] = Field(None, max_length=50, description="Telefono fijo")
    numero_colegiado: Optional[str] = Field(None, max_length=100, description="Numero de colegiado CAAPR")
    instagram: Optional[str] = Field(None, max_length=255, description="Instagram URL/handle")
    facebook: Optional[str] = Field(None, max_length=255, description="Facebook URL/handle")
    linkedin: Optional[str] = Field(None, max_length=255, description="LinkedIn URL/handle")
    twitter: Optional[str] = Field(None, max_length=255, description="Twitter URL/handle")
    tarifa_entrevista_inicial_usd: Optional[Decimal] = Field(None, description="Tarifa entrevista inicial USD")
    formulario_contacto: Optional[str] = Field(None, max_length=500, description="URL formulario de contacto")
    descripcion_perfil_profesional: Optional[str] = Field(None, description="Descripcion del perfil profesional")
    logo_empresa_url: Optional[str] = Field(None, max_length=500, description="URL del logo de empresa")
    firma_abogado_url: Optional[str] = Field(None, max_length=500, description="URL de la firma del abogado")


class PerfilCreate(PerfilBase):
    """Schema para crear un perfil."""
    pass


class PerfilUpdate(PerfilBase):
    """Schema para actualizar un perfil (all fields optional)."""
    pass


class PerfilResponse(PerfilBase):
    """Schema de respuesta de Perfil."""
    id: int
    firma_id: int
    esta_activo: bool
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)
