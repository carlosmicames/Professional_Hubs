"""
Modelo de Cliente.
Updated with address fields and billing flags for Professional Hubs.
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

    # Required client info
    nombre = Column(String(100), nullable=False, comment="Nombre del cliente")
    apellido = Column(String(100), nullable=False, comment="Apellido del cliente")
    email = Column(String(255), nullable=False, comment="Email del cliente (required)")
    telefono = Column(String(50), nullable=False, comment="Telefono del cliente (required)")
    direccion = Column(String(500), nullable=False, comment="Direccion fisica (required)")

    # Optional fields
    segundo_apellido = Column(String(100), nullable=True, comment="Segundo apellido (comun en Puerto Rico)")
    nombre_empresa = Column(String(255), nullable=True, comment="Nombre de empresa/corporacion")
    direccion_postal = Column(String(500), nullable=True, comment="Direccion postal")

    # Billing/Status flags
    has_late_invoices = Column(Boolean, default=False, nullable=False, comment="Flag for late invoices")
    has_potential_conflict = Column(Boolean, default=False, nullable=False, comment="Flag for potential conflict")

    # Audit fields
    esta_activo = Column(Boolean, default=True, nullable=False, comment="Soft delete flag")
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    firma = relationship("Firma", back_populates="clientes")
    asuntos = relationship("Asunto", back_populates="cliente", lazy="dynamic")

    # Indexes for search
    __table_args__ = (
        Index('ix_clientes_nombre_apellido', 'nombre', 'apellido'),
        Index('ix_clientes_nombre_apellido_completo', 'nombre', 'apellido', 'segundo_apellido'),
        Index('ix_clientes_nombre_empresa', 'nombre_empresa'),
        Index('ix_clientes_firma_activo', 'firma_id', 'esta_activo'),
        Index('ix_clientes_email', 'email'),
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
