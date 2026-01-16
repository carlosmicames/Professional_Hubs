"""
Modelo de Asunto (Matter/Case).
Uses String column instead of PostgreSQL ENUM for deployment reliability.
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, Index
from sqlalchemy.orm import relationship
from app.database import Base


# Python enum for validation (not stored in DB as enum)
class EstadoAsunto:
    """Estados posibles de un asunto legal."""
    ACTIVO = "ACTIVO"
    CERRADO = "CERRADO"
    PENDIENTE = "PENDIENTE"
    ARCHIVADO = "ARCHIVADO"
    
    @classmethod
    def values(cls):
        return [cls.ACTIVO, cls.CERRADO, cls.PENDIENTE, cls.ARCHIVADO]


class Asunto(Base):
    """
    Representa un asunto legal o caso.
    Vinculado a un cliente y contiene partes relacionadas.
    """
    
    __tablename__ = "asuntos"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(
        Integer, 
        ForeignKey("clientes.id", ondelete="CASCADE"), 
        nullable=False,
        index=True,
        comment="ID del cliente principal"
    )
    
    nombre_asunto = Column(String(500), nullable=False, comment="Nombre o descripción del asunto")
    fecha_apertura = Column(Date, default=date.today, nullable=False, comment="Fecha de apertura")
    
    # Using String instead of ENUM - stores same values, no deployment issues
    estado = Column(
        String(20), 
        default=EstadoAsunto.ACTIVO, 
        nullable=False,
        comment="Estado actual del asunto: ACTIVO, CERRADO, PENDIENTE, ARCHIVADO"
    )
    
    # Campos de auditoría
    esta_activo = Column(Boolean, default=True, nullable=False, comment="Soft delete flag")
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="asuntos")
    partes_relacionadas = relationship("ParteRelacionada", back_populates="asunto", lazy="dynamic")
    
    # Índices
    __table_args__ = (
        Index('ix_asuntos_cliente_estado', 'cliente_id', 'estado'),
        Index('ix_asuntos_fecha_apertura', 'fecha_apertura'),
    )
    
    def __repr__(self):
        return f"<Asunto(id={self.id}, nombre='{self.nombre_asunto[:50]}...', estado={self.estado})>"