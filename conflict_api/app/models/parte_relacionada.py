"""
Modelo de Parte Relacionada (Related Party).
Uses String column instead of PostgreSQL ENUM for deployment reliability.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


# Python class for validation (not stored in DB as enum)
class TipoRelacion:
    """Tipos de relación de partes en un asunto legal."""
    DEMANDANTE = "DEMANDANTE"
    DEMANDADO = "DEMANDADO"
    PARTE_CONTRARIA = "PARTE_CONTRARIA"
    CO_DEMANDADO = "CO_DEMANDADO"
    CONYUGE = "CONYUGE"
    SUBSIDIARIA = "SUBSIDIARIA"
    EMPRESA_MATRIZ = "EMPRESA_MATRIZ"
    
    @classmethod
    def values(cls):
        return [
            cls.DEMANDANTE, cls.DEMANDADO, cls.PARTE_CONTRARIA,
            cls.CO_DEMANDADO, cls.CONYUGE, cls.SUBSIDIARIA, cls.EMPRESA_MATRIZ
        ]


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
    
    # Using String instead of ENUM - stores same values, no deployment issues
    tipo_relacion = Column(
        String(30), 
        nullable=False,
        comment="Tipo de relación: DEMANDANTE, DEMANDADO, PARTE_CONTRARIA, CO_DEMANDADO, CONYUGE, SUBSIDIARIA, EMPRESA_MATRIZ"
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
        return f"<ParteRelacionada(id={self.id}, nombre='{self.nombre}', tipo={self.tipo_relacion})>"