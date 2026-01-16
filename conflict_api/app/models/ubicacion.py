"""
Modelo de Ubicacion (Geographic Location) - Linked to Firm.
Stores geographic location for the firm.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Ubicacion(Base):
    """
    Geographic location linked to the firm.
    Stores country and municipality information.
    """

    __tablename__ = "ubicaciones"

    id = Column(Integer, primary_key=True, index=True)
    firma_id = Column(
        Integer,
        ForeignKey("firmas.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="ID del bufete (one record per firm)"
    )

    # Location
    pais = Column(String(100), nullable=True, default="Puerto Rico", comment="Pais")
    municipio = Column(String(100), nullable=True, comment="Municipio")

    # Audit fields
    esta_activo = Column(Boolean, default=True, nullable=False, comment="Soft delete flag")
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    firma = relationship("Firma", back_populates="ubicacion")

    def __repr__(self):
        return f"<Ubicacion(id={self.id}, firma_id={self.firma_id}, municipio={self.municipio})>"
