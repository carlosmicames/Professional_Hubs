# conflict_api/app/schemas/intake.py
"""
Schemas para Intake Calls.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from app.models.intake import IdiomaLlamada, EstadoIntake, TipoCaso, UrgenciaCase


class IntakeCallBase(BaseModel):
    """Campos base de Intake Call."""
    numero_llamante: str = Field(..., description="Número de teléfono del llamante")
    idioma: Optional[IdiomaLlamada] = Field(IdiomaLlamada.ESPANOL, description="Idioma de la conversación")
    nombre_completo: Optional[str] = Field(None, description="Nombre completo del llamante")
    email: Optional[EmailStr] = Field(None, description="Email del llamante")
    telefono_contacto: Optional[str] = Field(None, description="Teléfono preferido")
    tipo_caso: Optional[TipoCaso] = Field(None, description="Tipo de caso legal")
    descripcion_caso: Optional[str] = Field(None, description="Descripción del problema")
    urgencia: Optional[UrgenciaCase] = Field(UrgenciaCase.MEDIA, description="Nivel de urgencia")


class IntakeCallCreate(IntakeCallBase):
    """Schema para crear un intake call."""
    twilio_call_sid: Optional[str] = Field(None, description="Twilio Call SID")
    transcripcion_completa: Optional[str] = Field(None, description="Transcripción completa")


class IntakeCallUpdate(BaseModel):
    """Schema para actualizar un intake call."""
    nombre_completo: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono_contacto: Optional[str] = None
    tipo_caso: Optional[TipoCaso] = None
    descripcion_caso: Optional[str] = None
    urgencia: Optional[UrgenciaCase] = None
    estado: Optional[EstadoIntake] = None
    asignado_a_abogado: Optional[str] = None
    conflicto_verificado: Optional[bool] = None


class IntakeCallResponse(BaseModel):
    """Schema de respuesta de Intake Call."""
    id: int
    firma_id: int
    twilio_call_sid: Optional[str]
    numero_llamante: str
    duracion_segundos: Optional[int]
    idioma: IdiomaLlamada
    nombre_completo: Optional[str]
    email: Optional[str]
    telefono_contacto: Optional[str]
    tipo_caso: Optional[TipoCaso]
    descripcion_caso: Optional[str]
    urgencia: UrgenciaCase
    estado: EstadoIntake
    requiere_conflicto_check: bool
    conflicto_verificado: bool
    asignado_a_abogado: Optional[str]
    creado_en: datetime
    actualizado_en: datetime
    
    class Config:
        from_attributes = True