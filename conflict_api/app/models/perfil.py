"""
Modelo de Perfil (Profile) - Linked to Firm.
Stores professional profile information for single-firm use.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Perfil(Base):
    """
    Professional profile linked to the firm.
    Contains attorney/professional details, social media, and invoice images.
    """

    __tablename__ = "perfiles"

    id = Column(Integer, primary_key=True, index=True)
    firma_id = Column(
        Integer,
        ForeignKey("firmas.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="ID del bufete (one profile per firm)"
    )

    # Professional info
    numero_rua = Column(Integer, nullable=True, comment="Numero de RUA")
    direccion = Column(String(500), nullable=True, comment="Direccion fisica")
    direccion_postal = Column(String(500), nullable=True, comment="Direccion postal")
    telefono_celular = Column(String(50), nullable=True, comment="Telefono celular")
    telefono = Column(String(50), nullable=True, comment="Telefono fijo")
    numero_colegiado = Column(String(100), nullable=True, comment="Numero de colegiado CAAPR")

    # Social media
    instagram = Column(String(255), nullable=True)
    facebook = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True)
    twitter = Column(String(255), nullable=True)

    # Professional services
    tarifa_entrevista_inicial_usd = Column(Numeric(10, 2), nullable=True, comment="Tarifa entrevista inicial en USD")
    formulario_contacto = Column(String(500), nullable=True, comment="URL formulario de contacto")
    descripcion_perfil_profesional = Column(Text, nullable=True, comment="Descripcion del perfil profesional")

    # Invoice images
    logo_empresa_url = Column(String(500), nullable=True, comment="URL del logo de empresa")
    firma_abogado_url = Column(String(500), nullable=True, comment="URL de la firma del abogado")

    # Audit fields
    esta_activo = Column(Boolean, default=True, nullable=False, comment="Soft delete flag")
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    firma = relationship("Firma", back_populates="perfil")

    def __repr__(self):
        return f"<Perfil(id={self.id}, firma_id={self.firma_id})>"
