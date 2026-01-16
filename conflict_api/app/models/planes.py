"""
Modelo de Planes (Plan Selection) - Linked to Firm.
Stores subscription plan selection for the firm.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


# Plan options
PLAN_OPTIONS = ["Basico", "Emprendedor", "Plus", "Enterprise"]


class Planes(Base):
    """
    Plan selection linked to the firm.
    Tracks selected subscription plan and trial status.
    """

    __tablename__ = "planes"

    id = Column(Integer, primary_key=True, index=True)
    firma_id = Column(
        Integer,
        ForeignKey("firmas.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="ID del bufete (one record per firm)"
    )

    # Plan selection
    selected_plan = Column(String(50), nullable=True, default="Basico", comment="Selected plan: Basico, Emprendedor, Plus, Enterprise")
    trial_days = Column(Integer, nullable=True, default=14, comment="Trial days (14 for Basico)")
    plan_status = Column(String(50), nullable=True, default="trial", comment="Plan status placeholder")
    stripe_placeholder = Column(String(255), nullable=True, comment="Stripe integration placeholder")

    # Audit fields
    esta_activo = Column(Boolean, default=True, nullable=False, comment="Soft delete flag")
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    firma = relationship("Firma", back_populates="planes")

    def __repr__(self):
        return f"<Planes(id={self.id}, firma_id={self.firma_id}, selected_plan={self.selected_plan})>"
