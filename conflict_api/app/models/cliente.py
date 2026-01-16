"""
Modelo de Cliente.
Updated with email and telefono fields for billing automation.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Cliente(Base):
    """
    Representa un cliente del bufete.
    Puede ser persona natural (nombre/apellido) o empresa (nombre_empresa).
    """
    
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    firma_id = Column(
        Integer, 
        ForeignKey("firmas.id", ondelete="CASCADE"), 
        nullable=False,
        index=True,
        comment="ID del bufete (multi-tenant)"
    )
    
    # Datos de persona natural
    nombre = Column(String(100), nullable=True, comment="Nombre del cliente individual")
    apellido = Column(String(100), nullable=True, comment="Primer apellido del cliente individual")
    segundo_apellido = Column(String(100), nullable=True, comment="Segundo apellido (común en Puerto Rico)")
    
    # Datos de empresa
    nombre_empresa = Column(String(255), nullable=True, comment="Nombre de empresa/corporación")
    
    # Contacto (para billing automation)
    email = Column(String(255), nullable=True, comment="Email para facturación y comunicaciones")
    telefono = Column(String(50), nullable=True, comment="Teléfono para SMS de cobro")
    
    # Campos de auditoría
    esta_activo = Column(Boolean, default=True, nullable=False, comment="Soft delete flag")
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    firma = relationship("Firma", back_populates="clientes")
    asuntos = relationship("Asunto", back_populates="cliente", lazy="dynamic")
    
    # Índices para búsqueda de conflictos
    __table_args__ = (
        Index('ix_clientes_nombre_apellido', 'nombre', 'apellido'),
        Index('ix_clientes_nombre_apellido_completo', 'nombre', 'apellido', 'segundo_apellido'),
        Index('ix_clientes_nombre_empresa', 'nombre_empresa'),
        Index('ix_clientes_firma_activo', 'firma_id', 'esta_activo'),
    )
    
    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del cliente."""
        if self.nombre_empresa:
            return self.nombre_empresa
        partes = [p for p in [self.nombre, self.apellido, self.segundo_apellido] if p]
        return " ".join(partes) if partes else ""
    
    def __repr__(self):
        return f"<Cliente(id={self.id}, nombre_completo='{self.nombre_completo}')>"