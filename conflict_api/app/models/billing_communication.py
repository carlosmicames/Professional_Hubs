"""
Modelo de Billing Communication Logs.
Rastrea todas las comunicaciones de cobro enviadas a clientes.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class CommunicationType(str, enum.Enum):
    """Tipos de comunicación de cobro."""
    EMAIL = "email"
    SMS = "sms"
    PHONE_CALL = "phone_call"
    LETTER = "letter"


class CommunicationStatus(str, enum.Enum):
    """Estado de la comunicación."""
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    READ = "read"


class BillingCommunicationLog(Base):
    """
    Registro de todas las comunicaciones de cobro.
    Vinculado a facturas para rastreo completo del historial.
    """
    
    __tablename__ = "billing_communication_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la factura"
    )
    
    # Tipo y contenido
    type = Column(
        Enum(CommunicationType),
        nullable=False,
        comment="Tipo de comunicación (email/sms)"
    )
    message_body = Column(Text, nullable=False, comment="Contenido del mensaje enviado")
    subject = Column(String(500), nullable=True, comment="Asunto (para emails)")
    
    # Estado y tracking
    status = Column(
        Enum(CommunicationStatus),
        default=CommunicationStatus.SENT,
        nullable=False,
        comment="Estado de la comunicación"
    )
    sent_at = Column(DateTime, nullable=False, comment="Fecha/hora de envío")
    delivered_at = Column(DateTime, nullable=True, comment="Fecha/hora de entrega")
    read_at = Column(DateTime, nullable=True, comment="Fecha/hora de lectura (si disponible)")
    
    # IDs externos para tracking
    external_id = Column(String(255), nullable=True, comment="ID de Twilio/Postmark")
    error_message = Column(Text, nullable=True, comment="Mensaje de error si falló")
    
    # Metadatos
    days_overdue_when_sent = Column(Integer, nullable=False, comment="Días de atraso al enviar")
    reminder_sequence = Column(Integer, nullable=False, comment="Número en secuencia (1=primer recordatorio)")
    
    # Auditoría
    esta_activo = Column(Boolean, default=True, nullable=False, comment="Soft delete flag")
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    # invoice = relationship("Invoice", back_populates="communication_logs")
    
    # Índices para búsqueda rápida
    __table_args__ = (
        Index('ix_billing_comms_invoice_date', 'invoice_id', 'sent_at'),
        Index('ix_billing_comms_status', 'status'),
        Index('ix_billing_comms_type_date', 'type', 'sent_at'),
    )
    
    def __repr__(self):
        return f"<BillingCommunicationLog(id={self.id}, invoice_id={self.invoice_id}, type={self.type.value}, sent_at='{self.sent_at}')>"
