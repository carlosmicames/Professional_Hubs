"""
Schemas para Cliente.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class ClienteBase(BaseModel):
    """Campos base de Cliente."""
    nombre: Optional[str] = Field(None, max_length=100, description="Nombre del cliente individual")
    apellido: Optional[str] = Field(None, max_length=100, description="Apellido del cliente individual")
    nombre_empresa: Optional[str] = Field(None, max_length=255, description="Nombre de empresa/corporación")
    
    @model_validator(mode='after')
    def validar_tipo_cliente(self):
        """Valida que se proporcione nombre/apellido O nombre_empresa."""
        tiene_nombre_personal = bool(self.nombre or self.apellido)
        tiene_empresa = bool(self.nombre_empresa)
        
        if not tiene_nombre_personal and not tiene_empresa:
            raise ValueError(
                "Debe proporcionar nombre/apellido para persona natural "
                "o nombre_empresa para empresa"
            )
        
        return self


class ClienteCreate(ClienteBase):
    """Schema para crear un cliente."""
    pass


class ClienteUpdate(BaseModel):
    """Schema para actualizar un cliente."""
    nombre: Optional[str] = Field(None, max_length=100, description="Nombre del cliente individual")
    apellido: Optional[str] = Field(None, max_length=100, description="Apellido del cliente individual")
    nombre_empresa: Optional[str] = Field(None, max_length=255, description="Nombre de empresa/corporación")


class ClienteResponse(BaseModel):
    """Schema de respuesta de Cliente."""
    id: int
    firma_id: int
    nombre: Optional[str]
    apellido: Optional[str]
    nombre_empresa: Optional[str]
    nombre_completo: str = Field(..., description="Nombre completo calculado")
    esta_activo: bool
    creado_en: datetime
    actualizado_en: datetime
    
    class Config:
        from_attributes = True