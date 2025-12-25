"""
Modelo de Parte Relacionada (Related Party).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class TipoRelacion(str, enum.Enum):
    """Tipos de relación de partes en un asunto legal."""
    DEMANDANTE = "demandante"
    DEMANDADO = "demandado"
    PARTE_CONTRARIA = "parte_contraria"
    CO_DEMANDADO = "co_demandado"
    CONYUGE = "conyuge"
    SUBSIDIARIA = "subsidiaria"
    EMPRESA_MATRIZ = "empresa_matriz"


class ParteRelacionada(Base):
    """
    Representa una parte relacionada a un asunto legal.
    Incluye partes contrarias, testigos, co-demandados, etc.
    """
    
    __tablename__ = "partes_relacionadas"
    
    id = Column(Integer, primary_key=True, index=True)
    asunto_id = Column(
        Integer, 
        ForeignKey("asuntos.id", ondelete="CASCADE"), 
        nullable=False,
        index=True,
        comment="ID del asunto relacionado"
    )
    
    nombre = Column(String(255), nullable=False, comment="Nombre de la parte relacionada")
    tipo_relacion = Column(
        Enum(TipoRelacion), 
        nullable=False,
        comment="Tipo de relación con el asunto"
    )
    
    # Campos de auditoría
    esta_activo = Column(Boolean, default=True, nullable=False, comment="Soft delete flag")
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    asunto = relationship("Asunto", back_populates="partes_relacionadas")
    
    # Índices para búsqueda de conflictos
    __table_args__ = (
        Index('ix_partes_nombre', 'nombre'),
        Index('ix_partes_asunto_activo', 'asunto_id', 'esta_activo'),
    )
    
    def __repr__(self):
        return f"<ParteRelacionada(id={self.id}, nombre='{self.nombre}', tipo={self.tipo_relacion.value})>"