"""
Modelo de Estudios (Studies) - Linked to Firm.
Stores educational background for the firm/attorney.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Estudios(Base):
    """
    Educational background linked to the firm.
    Stores university and law school information.
    """

    __tablename__ = "estudios"

    id = Column(Integer, primary_key=True, index=True)
    firma_id = Column(
        Integer,
        ForeignKey("firmas.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="ID del bufete (one record per firm)"
    )

    # Education
    universidad = Column(String(255), nullable=True, comment="Universidad de estudios generales")
    ano_graduacion = Column(String(50), nullable=True, comment="Ano de graduacion universidad")
    escuela_derecho = Column(String(255), nullable=True, comment="Escuela de derecho")
    ano_graduacion_derecho = Column(String(50), nullable=True, comment="Ano de graduacion derecho")

    # Audit fields
    esta_activo = Column(Boolean, default=True, nullable=False, comment="Soft delete flag")
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    firma = relationship("Firma", back_populates="estudios")

    def __repr__(self):
        return f"<Estudios(id={self.id}, firma_id={self.firma_id})>"
