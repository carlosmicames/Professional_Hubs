"""
Modelo de Firma (Bufete de Abogados).
Updated with additional company fields and relationships.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Firma(Base):
    """
    Representa un bufete de abogados.
    Tabla principal para aislamiento multi-tenant.
    For MVP: Single firm only (firm_id=1).
    """

    __tablename__ = "firmas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=True, comment="Nombre del bufete/empresa")

    # Company details (new fields)
    direccion = Column(String(500), nullable=True, comment="Direccion fisica de la empresa")
    direccion_postal = Column(String(500), nullable=True, comment="Direccion postal de la empresa")
    telefono = Column(String(50), nullable=True, comment="Telefono de la empresa")

    # Audit fields
    esta_activo = Column(Boolean, default=True, nullable=False, comment="Soft delete flag")
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    clientes = relationship("Cliente", back_populates="firma", lazy="dynamic")
    perfil = relationship("Perfil", back_populates="firma", uselist=False)
    estudios = relationship("Estudios", back_populates="firma", uselist=False)
    areas_practica = relationship("AreasPractica", back_populates="firma", uselist=False)
    ubicacion = relationship("Ubicacion", back_populates="firma", uselist=False)
    planes = relationship("Planes", back_populates="firma", uselist=False)

    def __repr__(self):
        return f"<Firma(id={self.id}, nombre='{self.nombre}')>"
