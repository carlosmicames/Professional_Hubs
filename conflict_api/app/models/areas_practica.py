"""
Modelo de Areas de Practica (Practice Areas) - Linked to Firm.
Stores practice areas for the firm using JSON array.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class AreasPractica(Base):
    """
    Practice areas linked to the firm.
    Uses JSONB to store array of practice area strings.
    """

    __tablename__ = "areas_practica"

    id = Column(Integer, primary_key=True, index=True)
    firma_id = Column(
        Integer,
        ForeignKey("firmas.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="ID del bufete (one record per firm)"
    )

    # Practice areas stored as JSON array
    areas = Column(JSONB, nullable=True, default=list, comment="Array of practice area strings")

    # Audit fields
    esta_activo = Column(Boolean, default=True, nullable=False, comment="Soft delete flag")
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    firma = relationship("Firma", back_populates="areas_practica")

    def __repr__(self):
        return f"<AreasPractica(id={self.id}, firma_id={self.firma_id}, areas={self.areas})>"
