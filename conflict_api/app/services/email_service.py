# conflict_api/app/services/email_service.py
"""
Servicio para notificaciones por email a abogados.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class EmailService:
    """Envía notificaciones por email."""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@professionalhubs.com")
    
    def send_new_consultation_notification(
        self,
        attorney_email: str,
        client_name: str,
        client_phone: str,
        case_type: str,
        appointment_time: datetime,
        calendar_link: str,
        intake_id: int
    ) -> bool:
        """
        Notifica a abogado sobre nueva consulta agendada.
        """
        if not self.smtp_username or not self.smtp_password:
            print("Email not configured")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = attorney_email
            msg['Subject'] = f"Nueva Consulta Agendada - {client_name}"
            
            # HTML email
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; }}
        .info-box {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; 
                     border-left: 4px solid #667eea; }}
        .button {{ display: inline-block; background: #667eea; color: white; 
                   padding: 12px 24px; text-decoration: none; border-radius: 5px; 
                   margin: 10px 5px; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">⚖️ Nueva Consulta Agendada</h1>
        </div>
        
        <div class="content">
            <div class="info-box">
                <h3>📋 Información del Cliente</h3>
                <p><strong>Nombre:</strong> {client_name}</p>
                <p><strong>Teléfono:</strong> {client_phone}</p>
                <p><strong>Tipo de Caso:</strong> {case_type.upper()}</p>
            </div>
            
            <div class="info-box">
                <h3>📅 Cita Agendada</h3>
                <p><strong>Fecha/Hora:</strong> {appointment_time.strftime('%d/%m/%Y a las %I:%M %p')}</p>
                <p><strong>Duración:</strong> 30 minutos</p>
            </div>
            
            <div class="info-box">
                <h3>⚠️ Siguiente Paso</h3>
                <p>El cliente recibirá un formulario de WhatsApp para completar más detalles.</p>
                <p><strong>Estado:</strong> Pendiente de formulario completo</p>
            </div>
            
            <div style="text-align: center; margin: 20px 0;">
                <a href="{calendar_link}" class="button">📅 Ver en Calendario</a>
                <a href="https://your-app.railway.app/calls/{intake_id}" class="button">📝 Ver Detalles</a>
            </div>
            
            <p><small>Una vez el cliente complete el formulario, recibirás otra notificación con todos los detalles.</small></p>
        </div>
        
        <div class="footer">
            <p>Professional Hubs © 2025</p>
            <p>Este es un mensaje automático del sistema de intake.</p>
        </div>
    </div>
</body>
</html>
"""
            
            msg.attach(MIMEText(html, 'html'))
            
            # Enviar
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            print(f"Email sent to {attorney_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_form_completed_notification(
        self,
        attorney_email: str,
        client_name: str,
        intake_id: int
    ) -> bool:
        """Notifica que el cliente completó el formulario."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = attorney_email
            msg['Subject'] = f"✅ Formulario Completo - {client_name}"
            
            body = f"""
Hola,

{client_name} ha completado el formulario de intake.

Revisa los detalles completos y confirma o rechaza la consulta:
https://your-app.railway.app/calls/{intake_id}

Saludos,
Professional Hubs
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False


email_service = EmailService()