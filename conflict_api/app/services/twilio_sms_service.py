"""
Servicio de SMS usando Twilio para recordatorios de facturación.
"""

import os
from typing import Dict
from twilio.rest import Client


class TwilioSMSService:
    """
    Servicio para enviar SMS de cobro usando Twilio.
    """
    
    def __init__(self):
        """Inicializa servicio de Twilio."""
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER")
        
        self.client = None
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                print(f"⚠️  Failed to initialize Twilio client: {e}")
        else:
            print("⚠️  TWILIO credentials not configured - SMS features disabled")
    
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
            to_phone: Número de teléfono del cliente (formato: +1234567890)
            client_name: Nombre del cliente
            invoice_number: Número de factura
            amount_due: Monto adeudado
            days_overdue: Días de atraso
            reminder_level: Nivel de recordatorio (1, 2, 3)
        
        Returns:
            Dict con resultado del envío
        """
        if not self.client:
            return {"success": False, "error": "Twilio not configured"}
        
        # Asegurar formato correcto del número
        if not to_phone.startswith('+'):
            # Asumir Puerto Rico (+1 787/939)
            to_phone = f"+1{to_phone.replace('-', '').replace(' ', '')}"
        
        # Seleccionar mensaje según nivel
        if reminder_level == 1:
            message = self._get_first_reminder_message(
                client_name, invoice_number, amount_due, days_overdue
            )
        elif reminder_level == 2:
            message = self._get_second_reminder_message(
                client_name, invoice_number, amount_due, days_overdue
            )
        elif reminder_level == 3:
            message = self._get_final_reminder_message(
                client_name, invoice_number, amount_due, days_overdue
            )
        else:
            message = f"Professional Hubs: Factura #{invoice_number} vencida. Contacte billing@professionalhubs.com"
        
        try:
            # Enviar SMS
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_phone
            )
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "status": message_obj.status,
                "to": to_phone
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send SMS: {str(e)}",
                "to": to_phone
            }
    
    def _get_first_reminder_message(
        self, client_name, invoice_number, amount_due, days_overdue
    ) -> str:
        """Primera notificación amistosa (15 días)."""
        first_name = client_name.split()[0]
        return (
            f"Hola {first_name}, este es un recordatorio amistoso de Professional Hubs. "
            f"Su factura #{invoice_number} por ${amount_due:,.2f} está vencida ({days_overdue} días). "
            f"Por favor procese el pago lo antes posible. Gracias!"
        )
    
    def _get_second_reminder_message(
        self, client_name, invoice_number, amount_due, days_overdue
    ) -> str:
        """Segunda notificación más firme (30 días)."""
        first_name = client_name.split()[0]
        return (
            f"URGENTE - {first_name}: Su factura #{invoice_number} por ${amount_due:,.2f} "
            f"lleva {days_overdue} días vencida. Si no recibimos el pago en 15 días, "
            f"aplicaremos cargos por mora. Contacte: billing@professionalhubs.com"
        )
    
    def _get_final_reminder_message(
        self, client_name, invoice_number, amount_due, days_overdue
    ) -> str:
        """Última advertencia (45 días)."""
        first_name = client_name.split()[0]
        return (
            f"ÚLTIMA ADVERTENCIA - {first_name}: Factura #{invoice_number} (${amount_due:,.2f}) "
            f"vencida hace {days_overdue} días. Acción legal inminente. "
            f"Contacte URGENTE: billing@professionalhubs.com o [TELÉFONO]"
        )
    
    def send_custom_sms(
        self,
        to_phone: str,
        message: str
    ) -> Dict:
        """
        Envía SMS personalizado.
        Útil para mensajes fuera del flujo estándar.
        """
        if not self.client:
            return {"success": False, "error": "Twilio not configured"}
        
        # Asegurar formato correcto del número
        if not to_phone.startswith('+'):
            to_phone = f"+1{to_phone.replace('-', '').replace(' ', '')}"
        
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_phone
            )
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "status": message_obj.status,
                "to": to_phone
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send SMS: {str(e)}",
                "to": to_phone
            }


# Singleton instance
twilio_sms_service = TwilioSMSService()