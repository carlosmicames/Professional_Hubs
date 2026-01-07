"""
Servicio de SMS usando Twilio para recordatorios de facturación.
"""

import os
from typing import Optional, Dict
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


class TwilioSMSService:
    """
    Servicio para enviar SMS de cobro usando Twilio.
    """
    
    def __init__(self):
        """Inicializa cliente de Twilio."""
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            print("Twilio credentials not configured")
    
    def send_payment_reminder_sms(
        self,
        to_phone: str,
        client_name: str,
        invoice_number: str,
        amount_due: float,
        days_overdue: int,
        reminder_level: int = 1
    ) -> Dict:
        """
        Envía recordatorio de pago por SMS.
        
        Args:
            to_phone: Número de teléfono del cliente
            client_name: Nombre del cliente
            invoice_number: Número de factura
            amount_due: Monto adeudado
            days_overdue: Días de atraso
            reminder_level: Nivel de recordatorio (1, 2, 3, 4)
        
        Returns:
            Dict con resultado del envío
        """
        if not self.client:
            return {"success": False, "error": "Twilio not configured"}
        
        # Seleccionar mensaje según nivel
        message_body = self._get_sms_message(
            client_name, invoice_number, amount_due, days_overdue, reminder_level
        )
        
        try:
            message = self.client.messages.create(
                from_=self.from_number,
                to=to_phone,
                body=message_body
            )
            
            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status,
                "to": message.to
            }
        
        except TwilioRestException as e:
            return {
                "success": False,
                "error": f"Twilio error: {e.msg}",
                "code": e.code
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send SMS: {str(e)}"
            }
    
    def _get_sms_message(
        self,
        client_name: str,
        invoice_number: str,
        amount_due: float,
        days_overdue: int,
        level: int
    ) -> str:
        """
        Genera mensaje SMS según nivel de recordatorio.
        Mantiene mensajes dentro de límite de caracteres.
        """
        if level == 1:
            # Primera notificación - amistosa
            return f"""Hola {client_name}. Recordatorio: Factura #{invoice_number} por ${amount_due:,.2f} vencida hace {days_overdue} días. Por favor procese el pago. Professional Hubs."""
        
        elif level == 2:
            # Segunda notificación - más urgente
            return f"""URGENTE {client_name}: Factura #{invoice_number} (${amount_due:,.2f}) vencida {days_overdue} días. Evite cargos adicionales - pague ahora. Professional Hubs. billing@professionalhubs.com"""
        
        elif level == 3:
            # Última advertencia
            return f"""ÚLTIMA ADVERTENCIA {client_name}: Factura #{invoice_number} (${amount_due:,.2f}) - {days_overdue} días vencida. Acción legal inminente. Contacte YA: [PHONE]. Professional Hubs"""
        
        else:
            # Danger zone - muy breve
            return f"""{client_name}: Factura #{invoice_number} crítica ({days_overdue} días). Departamento legal contactará. Professional Hubs"""
    
    def check_delivery_status(self, message_sid: str) -> Dict:
        """
        Verifica el estado de entrega de un mensaje SMS.
        
        Args:
            message_sid: SID del mensaje de Twilio
        
        Returns:
            Dict con estado actualizado
        """
        if not self.client:
            return {"success": False, "error": "Twilio not configured"}
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                "success": True,
                "status": message.status,
                "error_code": message.error_code,
                "error_message": message.error_message,
                "date_sent": message.date_sent,
                "date_updated": message.date_updated
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to check status: {str(e)}"
            }


twilio_sms_service = TwilioSMSService()