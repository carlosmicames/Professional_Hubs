"""
Scheduler automático para recordatorios de facturación.
Escanea facturas vencidas y envía recordatorios según reglas de negocio.
"""

import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.billing_communication import CommunicationType, CommunicationStatus
from app.crud.billing_communication import crud_billing_communication
from app.services.billing_communication.sendgrid_service import sendgrid_service
from app.services.twilio_sms_service import twilio_sms_service


class BillingReminderScheduler:
    """
    Scheduler para envío automático de recordatorios de pago.
    
    Reglas:
    - 15 días vencido: Primer recordatorio (Email + SMS)
    - 30 días vencido: Segundo recordatorio (Email + SMS)
    - 45 días vencido: Última advertencia (Email + SMS)
    - 60+ días vencido: "Danger Zone" - se detiene automatización
    """
    
    def __init__(self):
        """Inicializa el scheduler."""
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        
        # Configuración de días para recordatorios
        self.reminder_days = [15, 30, 45]
        self.danger_zone_days = 60
    
    def start(self):
        """Inicia el scheduler."""
        if not self.is_running:
            # Configurar job para ejecutar diariamente a las 9 AM
            self.scheduler.add_job(
                func=self.process_overdue_invoices,
                trigger=CronTrigger(hour=9, minute=0),
                id='billing_reminders',
                name='Process Overdue Invoices',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            print("Billing Reminder Scheduler started - Daily at 9:00 AM")
    
    def stop(self):
        """Detiene el scheduler."""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            print("⏹ Billing Reminder Scheduler stopped")
    
    def process_overdue_invoices(self):
        """
        Procesa todas las facturas vencidas y envía recordatorios apropiados.
        Este método se ejecuta automáticamente cada día.
        """
        print(f"\n{'='*60}")
        print(f"Processing Overdue Invoices - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        db = SessionLocal()
        
        try:
            # Obtener facturas no pagadas
            overdue_invoices = self._get_overdue_invoices(db)
            
            print(f"Found {len(overdue_invoices)} overdue invoices")
            
            for invoice in overdue_invoices:
                days_overdue = (date.today() - invoice['due_date']).days
                
                print(f"\n Processing Invoice #{invoice['invoice_number']}")
                print(f"   Client: {invoice['client_name']}")
                print(f"   Amount: ${invoice['amount']:,.2f}")
                print(f"   Days Overdue: {days_overdue}")
                
                # Determinar si debe enviar recordatorio
                if days_overdue >= self.danger_zone_days:
                    print(f"DANGER ZONE - No automated action")
                    self._mark_as_danger_zone(db, invoice)
                
                elif days_overdue in self.reminder_days:
                    # Verificar si ya se envió recordatorio hoy
                    if self._should_send_reminder(db, invoice['id'], days_overdue):
                        print(f"   Sending reminder (level {self._get_reminder_level(days_overdue)})")
                        self._send_multi_channel_reminder(db, invoice, days_overdue)
                    else:
                        print(f"   ✓ Reminder already sent today")
                
                else:
                    print(f"   ⏸ Not at reminder threshold yet")
            
            print(f"\n{'='*60}")
            print(f"Processing complete")
            print(f"{'='*60}\n")
        
        except Exception as e:
            print(f"Error processing invoices: {e}")
        
        finally:
            db.close()
    
    def _get_overdue_invoices(self, db: Session) -> List[Dict]:
        """
        Obtiene todas las facturas vencidas y no pagadas.
        
        NOTA: Esta función asume que existe una tabla 'invoices' en la base de datos.
        Ajustar según tu esquema real.
        """
        # Query SQL directo (ajustar según tu modelo real)
        query = """
            SELECT 
                i.id,
                i.invoice_number,
                i.amount,
                i.due_date,
                i.client_id,
                c.nombre || ' ' || c.apellido as client_name,
                c.email as client_email,
                c.telefono as client_phone
            FROM invoices i
            JOIN clients c ON i.client_id = c.id
            WHERE i.status = 'pending'
            AND i.due_date < CURRENT_DATE
            AND i.esta_activo = true
            ORDER BY i.due_date ASC
        """
        
        result = db.execute(query)
        
        invoices = []
        for row in result:
            invoices.append({
                'id': row[0],
                'invoice_number': row[1],
                'amount': row[2],
                'due_date': row[3],
                'client_id': row[4],
                'client_name': row[5],
                'client_email': row[6],
                'client_phone': row[7]
            })
        
        return invoices
    
    def _should_send_reminder(
        self,
        db: Session,
        invoice_id: int,
        days_overdue: int
    ) -> bool:
        """
        Verifica si debe enviar recordatorio hoy.
        Evita enviar múltiples recordatorios el mismo día.
        """
        # Obtener último recordatorio
        last_log = crud_billing_communication.get_last_communication(db, invoice_id)
        
        if not last_log:
            return True  # Nunca se ha enviado recordatorio
        
        # Verificar si el último recordatorio fue hoy
        today = date.today()
        last_sent_date = last_log.sent_at.date()
        
        if last_sent_date == today:
            return False  # Ya se envió hoy
        
        # Verificar si es el momento correcto para este nivel
        reminder_level = self._get_reminder_level(days_overdue)
        
        # Si ya se envió este nivel de recordatorio, no enviar de nuevo
        existing_count = crud_billing_communication.get_communication_count(
            db, invoice_id
        )
        
        return existing_count < reminder_level
    
    def _get_reminder_level(self, days_overdue: int) -> int:
        """Determina el nivel de recordatorio basado en días de atraso."""
        if days_overdue >= 45:
            return 3  # Última advertencia
        elif days_overdue >= 30:
            return 2  # Segundo recordatorio
        elif days_overdue >= 15:
            return 1  # Primer recordatorio
        else:
            return 0  # No enviar aún
    
    def _send_multi_channel_reminder(
        self,
        db: Session,
        invoice: Dict,
        days_overdue: int
    ):
        """
        Envía recordatorio por múltiples canales (Email + SMS).
        """
        reminder_level = self._get_reminder_level(days_overdue)
        
        # Enviar Email
        if invoice.get('client_email'):
            email_result = sendgrid_service.send_payment_reminder(
                to_email=invoice['client_email'],
                client_name=invoice['client_name'],
                invoice_number=invoice['invoice_number'],
                amount_due=invoice['amount'],
                days_overdue=days_overdue,
                due_date=invoice['due_date'].strftime('%d/%m/%Y'),
                reminder_level=reminder_level
            )
            
            if email_result.get('success'):
                print(f"      ✓ Email sent successfully")
                crud_billing_communication.create_log(
                    db=db,
                    invoice_id=invoice['id'],
                    type=CommunicationType.EMAIL,
                    message_body=f"Payment reminder level {reminder_level}",
                    days_overdue=days_overdue,
                    reminder_sequence=reminder_level,
                    subject=f"Payment Reminder - Invoice #{invoice['invoice_number']}",
                    status=CommunicationStatus.SENT,
                    external_id=email_result.get('message_id')
                )
            else:
                print(f"      ✗ Email failed: {email_result.get('error')}")
                crud_billing_communication.create_log(
                    db=db,
                    invoice_id=invoice['id'],
                    type=CommunicationType.EMAIL,
                    message_body=f"Payment reminder level {reminder_level}",
                    days_overdue=days_overdue,
                    reminder_sequence=reminder_level,
                    status=CommunicationStatus.FAILED
                )
        
        # Enviar SMS
        if invoice.get('client_phone'):
            sms_result = twilio_sms_service.send_payment_reminder_sms(
                to_phone=invoice['client_phone'],
                client_name=invoice['client_name'],
                invoice_number=invoice['invoice_number'],
                amount_due=invoice['amount'],
                days_overdue=days_overdue,
                reminder_level=reminder_level
            )
            
            if sms_result.get('success'):
                print(f"      ✓ SMS sent successfully")
                crud_billing_communication.create_log(
                    db=db,
                    invoice_id=invoice['id'],
                    type=CommunicationType.SMS,
                    message_body=f"SMS reminder level {reminder_level}",
                    days_overdue=days_overdue,
                    reminder_sequence=reminder_level,
                    status=CommunicationStatus.SENT,
                    external_id=sms_result.get('message_sid')
                )
            else:
                print(f"      ✗ SMS failed: {sms_result.get('error')}")
                crud_billing_communication.create_log(
                    db=db,
                    invoice_id=invoice['id'],
                    type=CommunicationType.SMS,
                    message_body=f"SMS reminder level {reminder_level}",
                    days_overdue=days_overdue,
                    reminder_sequence=reminder_level,
                    status=CommunicationStatus.FAILED
                )
    
    def _mark_as_danger_zone(self, db: Session, invoice: Dict):
        """
        Marca factura como zona de peligro (60+ días).
        No envía recordatorios automáticos.
        """
        # Verificar si ya está marcada
        last_log = crud_billing_communication.get_last_communication(db, invoice['id'])
        
        if last_log and last_log.days_overdue_when_sent >= self.danger_zone_days:
            return  # Ya está marcada
        
        # Crear log de danger zone
        crud_billing_communication.create_log(
            db=db,
            invoice_id=invoice['id'],
            type=CommunicationType.EMAIL,
            message_body="Invoice entered danger zone (60+ days overdue)",
            days_overdue=(date.today() - invoice['due_date']).days,
            reminder_sequence=4,
            status=CommunicationStatus.SENT
        )
        
        print(f"Marked as DANGER ZONE")
    
    def manual_trigger(self):
        """
        Trigger manual para testing.
        Ejecuta el proceso inmediatamente.
        """
        print("Manual trigger activated")
        self.process_overdue_invoices()


# Instancia global del scheduler
billing_scheduler = BillingReminderScheduler()