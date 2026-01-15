"""
Modelo de Asunto (Matter/Case).
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, Enum, Index
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class EstadoAsunto(str, enum.Enum):
    """Estados posibles de un asunto legal."""
    # FIXED: Values must match PostgreSQL enum (uppercase)
    ACTIVO = "ACTIVO"
    CERRADO = "CERRADO"
    PENDIENTE = "PENDIENTE"
    ARCHIVADO = "ARCHIVADO"


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
    estado = Column(
        Enum(EstadoAsunto), 
        default=EstadoAsunto.ACTIVO, 
        nullable=False,
        comment="Estado actual del asunto"
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
        return f"<Asunto(id={self.id}, nombre='{self.nombre_asunto[:50]}...', estado={self.estado.value})>"