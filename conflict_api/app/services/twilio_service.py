# conflict_api/app/services/twilio_service.py
"""
Servicio para integración con Twilio (llamadas y WhatsApp).
"""

import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from typing import Optional


class TwilioService:
    """
    Servicio para manejar llamadas y mensajes con Twilio.
    """
    
    def __init__(self):
        """Inicializa cliente de Twilio."""
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            print("⚠️ Twilio credentials not configured")
    
    def generar_twiml_respuesta(self, texto: str, continuar: bool = True) -> str:
        """
        Genera TwiML para responder al cliente con speech.
        
        Args:
            texto: Texto que el agente dirá
            continuar: Si True, espera más input del usuario
        
        Returns:
            String con XML TwiML
        """
        response = VoiceResponse()
        
        # Decir el texto al cliente
        response.say(
            texto,
            voice="Polly.Lupe",  # Voz en español de Amazon Polly
            language="es-MX"
        )
        
        if continuar:
            # Esperar respuesta del cliente (speech-to-text)
            gather = Gather(
                input='speech',
                action='/api/v1/calls/process-speech',
                method='POST',
                language='es-MX',
                speech_timeout='auto',
                timeout=10
            )
            response.append(gather)
            
            # Si no hay respuesta, repetir
            response.say(
                "¿Sigue ahí? Déjeme saber si necesita algo más.",
                voice="Polly.Lupe",
                language="es-MX"
            )
            response.redirect('/api/v1/calls/process-speech')
        else:
            # Despedida y colgar
            response.say(
                "Gracias por llamar. ¡Que tenga un excelente día!",
                voice="Polly.Lupe",
                language="es-MX"
            )
            response.hangup()
        
        return str(response)
    
    def enviar_sms(
        self,
        to: str,
        body: str
    ) -> Optional[str]:
        """
        Envía SMS de confirmación.
        
        Args:
            to: Número de destino (+1XXXXXXXXXX)
            body: Texto del mensaje
        
        Returns:
            Message SID o None si falla
        """
        if not self.client:
            print("Twilio client not initialized")
            return None
        
        try:
            message = self.client.messages.create(
                from_=self.phone_number,
                to=to,
                body=body
            )
            return message.sid
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return None
    
    def enviar_whatsapp(
        self,
        to: str,
        body: str
    ) -> Optional[str]:
        """
        Envía mensaje de WhatsApp.
        
        Args:
            to: Número de destino (whatsapp:+1XXXXXXXXXX)
            body: Texto del mensaje
        
        Returns:
            Message SID o None si falla
        """
        if not self.client:
            print("Twilio client not initialized")
            return None
        
        try:
            # Asegurar formato WhatsApp
            if not to.startswith("whatsapp:"):
                to = f"whatsapp:{to}"
            
            from_number = f"whatsapp:{self.phone_number}"
            
            message = self.client.messages.create(
                from_=from_number,
                to=to,
                body=body
            )
            return message.sid
        except Exception as e:
            print(f"Error sending WhatsApp: {e}")
            return None


# Instancia singleton del servicio
twilio_service = TwilioService()