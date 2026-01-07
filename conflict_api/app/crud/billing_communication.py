"""
CRUD para Billing Communication Logs.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.crud.base import CRUDBase
from app.models.billing_communication import BillingCommunicationLog, CommunicationType, CommunicationStatus
from pydantic import BaseModel


class BillingCommunicationCreate(BaseModel):
    """Schema para crear log de comunicación."""
    invoice_id: int
    type: CommunicationType
    message_body: str
    subject: Optional[str] = None
    days_overdue_when_sent: int
    reminder_sequence: int


class BillingCommunicationUpdate(BaseModel):
    """Schema para actualizar log de comunicación."""
    status: Optional[CommunicationStatus] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    external_id: Optional[str] = None
    error_message: Optional[str] = None


class CRUDBillingCommunication(CRUDBase[BillingCommunicationLog, BillingCommunicationCreate, BillingCommunicationUpdate]):
    """
    CRUD para operaciones de Billing Communication Logs.
    """
    
    def get_by_invoice(
        self,
        db: Session,
        invoice_id: int,
        include_inactive: bool = False
    ) -> List[BillingCommunicationLog]:
        """
        Obtiene todos los logs de comunicación para una factura.
        
        Args:
            db: Sesión de base de datos
            invoice_id: ID de la factura
            include_inactive: Incluir registros inactivos
        
        Returns:
            Lista de logs ordenados por fecha (más reciente primero)
        """
        query = db.query(BillingCommunicationLog).filter(
            BillingCommunicationLog.invoice_id == invoice_id
        )
        
        if not include_inactive:
            query = query.filter(BillingCommunicationLog.esta_activo == True)
        
        return query.order_by(desc(BillingCommunicationLog.sent_at)).all()
    
    def get_last_communication(
        self,
        db: Session,
        invoice_id: int
    ) -> Optional[BillingCommunicationLog]:
        """
        Obtiene la última comunicación enviada para una factura.
        """
        return db.query(BillingCommunicationLog).filter(
            BillingCommunicationLog.invoice_id == invoice_id,
            BillingCommunicationLog.esta_activo == True
        ).order_by(desc(BillingCommunicationLog.sent_at)).first()
    
    def get_communication_count(
        self,
        db: Session,
        invoice_id: int,
        type: Optional[CommunicationType] = None
    ) -> int:
        """
        Cuenta las comunicaciones enviadas para una factura.
        """
        query = db.query(BillingCommunicationLog).filter(
            BillingCommunicationLog.invoice_id == invoice_id,
            BillingCommunicationLog.esta_activo == True
        )
        
        if type:
            query = query.filter(BillingCommunicationLog.type == type)
        
        return query.count()
    
    def create_log(
        self,
        db: Session,
        invoice_id: int,
        type: CommunicationType,
        message_body: str,
        days_overdue: int,
        reminder_sequence: int,
        subject: Optional[str] = None,
        status: CommunicationStatus = CommunicationStatus.SENT,
        external_id: Optional[str] = None
    ) -> BillingCommunicationLog:
        """
        Crea un nuevo log de comunicación.
        
        Helper method con parámetros directos para facilitar uso.
        """
        log = BillingCommunicationLog(
            invoice_id=invoice_id,
            type=type,
            message_body=message_body,
            subject=subject,
            status=status,
            sent_at=datetime.utcnow(),
            days_overdue_when_sent=days_overdue,
            reminder_sequence=reminder_sequence,
            external_id=external_id
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    def update_status(
        self,
        db: Session,
        log_id: int,
        status: CommunicationStatus,
        delivered_at: Optional[datetime] = None,
        error_message: Optional[str] = None
    ) -> Optional[BillingCommunicationLog]:
        """
        Actualiza el estado de una comunicación.
        """
        log = db.query(BillingCommunicationLog).filter(
            BillingCommunicationLog.id == log_id
        ).first()
        
        if not log:
            return None
        
        log.status = status
        if delivered_at:
            log.delivered_at = delivered_at
        if error_message:
            log.error_message = error_message
        
        db.commit()
        db.refresh(log)
        return log
    
    def get_failed_communications(
        self,
        db: Session,
        hours: int = 24
    ) -> List[BillingCommunicationLog]:
        """
        Obtiene comunicaciones fallidas en las últimas N horas.
        Útil para reintento automático.
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return db.query(BillingCommunicationLog).filter(
            BillingCommunicationLog.status == CommunicationStatus.FAILED,
            BillingCommunicationLog.sent_at >= cutoff_time,
            BillingCommunicationLog.esta_activo == True
        ).all()


crud_billing_communication = CRUDBillingCommunication(BillingCommunicationLog)