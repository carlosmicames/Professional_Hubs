"""
Modelo de Firma (Bufete de Abogados).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Firma(Base):
    """
    Representa un bufete de abogados.
    Tabla principal para aislamiento multi-tenant.
    """
    
    __tablename__ = "firmas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, comment="Nombre del bufete")
    
    # Campos de auditoría
    esta_activo = Column(Boolean, default=True, nullable=False, comment="Soft delete flag")
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    clientes = relationship("Cliente", back_populates="firma", lazy="dynamic")
    
    def __repr__(self):
        return f"<Firma(id={self.id}, nombre='{self.nombre}')>"