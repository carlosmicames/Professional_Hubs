# conflict_api/app/services/whatsapp_forms.py
"""
Servicio para enviar formularios via WhatsApp usando Jotform o Google Forms.
"""

import os
from typing import Optional


class WhatsAppFormService:
    """
    Envía enlaces a formularios via WhatsApp.
    """
    
    def __init__(self):
        # Lazy initialization - don't create Twilio client until needed
        self._twilio_client = None
        self._account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self._auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_from = f"whatsapp:{os.getenv('TWILIO_PHONE_NUMBER')}" if os.getenv('TWILIO_PHONE_NUMBER') else None
        
        # URL del formulario (puedes usar Jotform, Google Forms, Typeform, etc.)
        self.form_url = os.getenv("INTAKE_FORM_URL", "https://forms.gle/PLACEHOLDER")
    
    @property
    def twilio_client(self):
        """Lazy initialization of Twilio client."""
        if self._twilio_client is None:
            if not self._account_sid or not self._auth_token:
                print("⚠️  TWILIO credentials not set - WhatsApp form service disabled")
                return None
            
            try:
                from twilio.rest import Client
                self._twilio_client = Client(self._account_sid, self._auth_token)
            except Exception as e:
                print(f"⚠️  Failed to initialize Twilio client: {e}")
                return None
        
        return self._twilio_client
    
    def send_intake_form(
        self,
        to_phone: str,
        nombre: str,
        tipo_caso: str,
        intake_id: int,
        language: str = "es"
    ) -> bool:
        """
        Envía enlace al formulario de intake via WhatsApp.
        """
        if not self.twilio_client:
            print(f"⚠️  Cannot send WhatsApp form - Twilio not configured")
            return False
        
        try:
            # Asegurar formato WhatsApp
            if not to_phone.startswith("whatsapp:"):
                to_phone = f"whatsapp:{to_phone}"
            
            # Crear URL con prefill (si tu formulario lo soporta)
            form_link = f"{self.form_url}?intake_id={intake_id}&nombre={nombre}&tipo={tipo_caso}"
            
            if language == "es":
                message_body = f"""
Hola {nombre},

Gracias por contactar a Professional Hubs.

Para programar su consulta sobre {tipo_caso}, por favor complete este breve formulario:

{form_link}

El formulario toma solo 2 minutos. Una vez completado, nuestro equipo le contactará para confirmar su cita.

¿Preguntas? Responda a este mensaje.

Professional Hubs
"""
            else:
                message_body = f"""
Hello {nombre},

Thank you for contacting Professional Hubs.

To schedule your consultation about {tipo_caso}, please complete this brief form:

{form_link}

The form takes only 2 minutes. Once completed, our team will contact you to confirm your appointment.

Questions? Reply to this message.

Professional Hubs
"""
            
            message = self.twilio_client.messages.create(
                from_=self.whatsapp_from,
                to=to_phone,
                body=message_body
            )
            
            print(f"✓ WhatsApp form sent: {message.sid}")
            return True
            
        except Exception as e:
            print(f"⚠️  Error sending WhatsApp form: {e}")
            # Fallback to SMS
            return self._send_sms_form(to_phone.replace("whatsapp:", ""), nombre, form_link, language)
    
    def _send_sms_form(self, to_phone: str, nombre: str, form_link: str, language: str) -> bool:
        """Fallback: enviar por SMS si WhatsApp falla."""
        if not self.twilio_client:
            return False
        
        try:
            from_number = os.getenv("TWILIO_PHONE_NUMBER")
            if not from_number:
                return False
            
            message = self.twilio_client.messages.create(
                from_=from_number,
                to=to_phone,
                body=f"Hola {nombre}, complete su formulario de consulta: {form_link}"
            )
            print(f"✓ SMS form sent (fallback): {message.sid}")
            return True
        except Exception as e:
            print(f"⚠️  Error sending SMS: {e}")
            return False
    
    def send_confirmation_message(
        self,
        to_phone: str,
        client_name: str,
        appointment_time,
        attorney_name: str,
        language: str = "es"
    ):
        """Envía mensaje de confirmación."""
        if not self.twilio_client:
            print("⚠️  Cannot send confirmation - Twilio not configured")
            return False
        
        # Implementation here
        return True


whatsapp_form_service = WhatsAppFormService()