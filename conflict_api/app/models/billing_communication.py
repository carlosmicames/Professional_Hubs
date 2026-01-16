"""
Modelo de Billing Communication Logs.
Rastrea todas las comunicaciones de cobro enviadas a clientes.
Uses String columns instead of PostgreSQL ENUMs for deployment reliability.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


# Python classes for validation (not stored in DB as enum)
class CommunicationType:
    """Tipos de comunicación de cobro."""
    EMAIL = "EMAIL"
    SMS = "SMS"
    PHONE_CALL = "PHONE_CALL"
    LETTER = "LETTER"
    
    @classmethod
    def values(cls):
        return [cls.EMAIL, cls.SMS, cls.PHONE_CALL, cls.LETTER]


class CommunicationStatus:
    """Estado de la comunicación."""
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    BOUNCED = "BOUNCED"
    READ = "READ"
    
    @classmethod
    def values(cls):
        return [cls.SENT, cls.DELIVERED, cls.FAILED, cls.BOUNCED, cls.READ]


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
    
    # Using String instead of ENUM - no deployment issues
    type = Column(
        String(20),
        nullable=False,
        comment="Tipo de comunicación: EMAIL, SMS, PHONE_CALL, LETTER"
    )
    message_body = Column(Text, nullable=False, comment="Contenido del mensaje enviado")
    subject = Column(String(500), nullable=True, comment="Asunto (para emails)")
    
    # Using String instead of ENUM
    status = Column(
        String(20),
        default=CommunicationStatus.SENT,
        nullable=False,
        comment="Estado: SENT, DELIVERED, FAILED, BOUNCED, READ"
    )
    sent_at = Column(DateTime, nullable=False, comment="Fecha/hora de envío")
    delivered_at = Column(DateTime, nullable=True, comment="Fecha/hora de entrega")
    read_at = Column(DateTime, nullable=True, comment="Fecha/hora de lectura (si disponible)")
    
    # IDs externos para tracking
    external_id = Column(String(255), nullable=True, comment="ID de Twilio/SendGrid")
    error_message = Column(Text, nullable=True, comment="Mensaje de error si falló")
    
    # Metadatos
    days_overdue_when_sent = Column(Integer, nullable=False, comment="Días de atraso al enviar")
    reminder_sequence = Column(Integer, nullable=False, comment="Número en secuencia (1=primer recordatorio)")
    
    # Auditoría
    esta_activo = Column(Boolean, default=True, nullable=False, comment="Soft delete flag")
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Índices para búsqueda rápida
    __table_args__ = (
        Index('ix_billing_comms_invoice_date', 'invoice_id', 'sent_at'),
        Index('ix_billing_comms_status', 'status'),
        Index('ix_billing_comms_type_date', 'type', 'sent_at'),
    )
    
    def __repr__(self):
        return f"<BillingCommunicationLog(id={self.id}, invoice_id={self.invoice_id}, type={self.type}, sent_at='{self.sent_at}')>"