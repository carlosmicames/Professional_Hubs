"""
Schemas para Planes (Plan Selection).
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


# Plan options
PlanType = Literal["Basico", "Emprendedor", "Plus", "Enterprise"]


class PlanesBase(BaseModel):
    """Campos base de Planes."""
    selected_plan: Optional[PlanType] = Field("Basico", description="Selected plan")
    trial_days: Optional[int] = Field(14, description="Trial days (14 for Basico)")
    plan_status: Optional[str] = Field("trial", max_length=50, description="Plan status")
    stripe_placeholder: Optional[str] = Field(None, max_length=255, description="Stripe placeholder")


class PlanesCreate(PlanesBase):
    """Schema para crear planes."""
    pass


class PlanesUpdate(BaseModel):
    """Schema para actualizar planes."""
    selected_plan: Optional[PlanType] = Field(None, description="Selected plan")
    trial_days: Optional[int] = Field(None, description="Trial days")
    plan_status: Optional[str] = Field(None, max_length=50, description="Plan status")
    stripe_placeholder: Optional[str] = Field(None, max_length=255, description="Stripe placeholder")


class PlanesResponse(PlanesBase):
    """Schema de respuesta de Planes."""
    id: int
    firma_id: int
    esta_activo: bool
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class PlanSelectionResponse(BaseModel):
    """Response after selecting a plan."""
    success: bool
    message: str
    plan: Optional[PlanesResponse] = None
