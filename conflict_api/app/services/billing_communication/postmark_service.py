"""
Servicio de Email usando Postmark para recordatorios de facturación.
"""

import os
from typing import Optional, Dict
import requests
from datetime import datetime


class PostmarkEmailService:
    """
    Servicio para enviar emails de cobro usando Postmark.
    """
    
    def __init__(self):
        """Inicializa servicio de Postmark."""
        self.api_key = os.getenv("POSTMARK_API_KEY")
        self.from_email = os.getenv("POSTMARK_FROM_EMAIL", "billing@professionalhubs.com")
        self.api_url = "https://api.postmarkapp.com/email"
        
        if not self.api_key:
            print("POSTMARK_API_KEY not configured")
    
    def send_payment_reminder(
        self,
        to_email: str,
        client_name: str,
        invoice_number: str,
        amount_due: float,
        days_overdue: int,
        due_date: str,
        reminder_level: int = 1
    ) -> Dict:
        """
        Envía recordatorio de pago por email.
        
        Args:
            to_email: Email del cliente
            client_name: Nombre del cliente
            invoice_number: Número de factura
            amount_due: Monto adeudado
            days_overdue: Días de atraso
            due_date: Fecha de vencimiento
            reminder_level: Nivel de recordatorio (1=primer aviso, 2=segundo, etc.)
        
        Returns:
            Dict con resultado del envío
        """
        if not self.api_key:
            return {"success": False, "error": "Postmark not configured"}
        
        # Seleccionar plantilla según nivel de recordatorio
        if reminder_level == 1:
            subject, body = self._get_first_reminder_template(
                client_name, invoice_number, amount_due, days_overdue, due_date
            )
        elif reminder_level == 2:
            subject, body = self._get_second_reminder_template(
                client_name, invoice_number, amount_due, days_overdue, due_date
            )
        elif reminder_level == 3:
            subject, body = self._get_final_reminder_template(
                client_name, invoice_number, amount_due, days_overdue, due_date
            )
        else:
            subject, body = self._get_danger_zone_template(
                client_name, invoice_number, amount_due, days_overdue, due_date
            )
        
        # Preparar request a Postmark
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Postmark-Server-Token": self.api_key
        }
        
        payload = {
            "From": self.from_email,
            "To": to_email,
            "Subject": subject,
            "HtmlBody": body,
            "TextBody": self._html_to_text(body),
            "MessageStream": "outbound"
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "message_id": result.get("MessageID"),
                    "submitted_at": result.get("SubmittedAt"),
                    "to": result.get("To")
                }
            else:
                return {
                    "success": False,
                    "error": f"Postmark API error: {response.status_code}",
                    "details": response.text
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send email: {str(e)}"
            }
    
    def _get_first_reminder_template(
        self, client_name, invoice_number, amount_due, days_overdue, due_date
    ) -> tuple:
        """Primera notificación amistosa (15 días)."""
        subject = f"Recordatorio de Pago - Factura #{invoice_number}"
        
        body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #667eea; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; }}
        .amount {{ font-size: 24px; font-weight: bold; color: #667eea; }}
        .button {{ display: inline-block; background: #667eea; color: white; 
                   padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Recordatorio de Pago</h1>
        </div>
        <div class="content">
            <p>Estimado(a) {client_name},</p>
            
            <p>Este es un recordatorio amistoso de que su factura está pendiente de pago.</p>
            
            <div style="background: white; padding: 15px; margin: 20px 0; border-left: 4px solid #667eea;">
                <p><strong>Factura:</strong> #{invoice_number}</p>
                <p><strong>Monto:</strong> <span class="amount">${amount_due:,.2f}</span></p>
                <p><strong>Fecha de Vencimiento:</strong> {due_date}</p>
                <p><strong>Días de Atraso:</strong> {days_overdue} días</p>
            </div>
            
            <p>Para evitar cargos adicionales y mantener su cuenta al día, le solicitamos procesar el pago lo antes posible.</p>
            
            <p><strong>Opciones de Pago:</strong></p>
            <ul>
                <li>Transferencia bancaria (detalles al final)</li>
                <li>Cheque a nombre de Professional Hubs</li>
                <li>ATH Móvil: [NÚMERO]</li>
            </ul>
            
            <p>Si ya realizó el pago, por favor ignore este mensaje y acepte nuestras disculpas por el inconveniente.</p>
            
            <p>Si tiene alguna pregunta o necesita hacer arreglos de pago, no dude en contactarnos.</p>
            
            <p>Cordialmente,<br>
            <strong>Professional Hubs</strong><br>
            Departamento de Facturación</p>
            
            <hr>
            <p style="font-size: 12px; color: #666;">
                <strong>Información Bancaria:</strong><br>
                Banco: [BANCO]<br>
                Cuenta: [NÚMERO]<br>
                Routing: [ROUTING]
            </p>
        </div>
    </div>
</body>
</html>
"""
        return subject, body
    
    def _get_second_reminder_template(
        self, client_name, invoice_number, amount_due, days_overdue, due_date
    ) -> tuple:
        """Segunda notificación más firme (30 días)."""
        subject = f"URGENTE: Pago Vencido - Factura #{invoice_number}"
        
        body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #d69e2e; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; }}
        .amount {{ font-size: 24px; font-weight: bold; color: #d69e2e; }}
        .warning {{ background: #fefcbf; border-left: 4px solid #d69e2e; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Segundo Recordatorio de Pago</h1>
        </div>
        <div class="content">
            <p>Estimado(a) {client_name},</p>
            
            <p>Nuestros registros indican que aún no hemos recibido el pago de la siguiente factura:</p>
            
            <div class="warning">
                <p><strong>Factura:</strong> #{invoice_number}</p>
                <p><strong>Monto:</strong> <span class="amount">${amount_due:,.2f}</span></p>
                <p><strong>Vencida hace:</strong> {days_overdue} días</p>
                <p><strong>Fecha Original:</strong> {due_date}</p>
            </div>
            
            <p><strong>Es importante que atienda este asunto de inmediato.</strong></p>
            
            <p>Si no recibimos el pago o una comunicación de su parte en los próximos 15 días, nos veremos obligados a:</p>
            <ul>
                <li>Aplicar cargos por mora según nuestros términos de servicio</li>
                <li>Suspender servicios adicionales hasta regularizar su cuenta</li>
                <li>Iniciar proceso de cobro formal</li>
            </ul>
            
            <p>Entendemos que pueden surgir circunstancias imprevistas. Si necesita establecer un plan de pago o discutir su situación, por favor contáctenos de inmediato.</p>
            
            <p><strong>Contacto Directo:</strong><br>
            Email: billing@professionalhubs.com<br>
            Teléfono: [NÚMERO]</p>
            
            <p>Cordialmente,<br>
            <strong>Professional Hubs</strong><br>
            Departamento de Facturación</p>
        </div>
    </div>
</body>
</html>
"""
        return subject, body
    
    def _get_final_reminder_template(
        self, client_name, invoice_number, amount_due, days_overdue, due_date
    ) -> tuple:
        """Última advertencia antes de acción legal (45 días)."""
        subject = f"ÚLTIMA NOTIFICACIÓN: Factura #{invoice_number} - Acción Inminente"
        
        body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #e53e3e; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; }}
        .amount {{ font-size: 28px; font-weight: bold; color: #e53e3e; }}
        .critical {{ background: #fed7d7; border-left: 4px solid #e53e3e; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ÚLTIMA ADVERTENCIA</h1>
        </div>
        <div class="content">
            <p>Estimado(a) {client_name},</p>
            
            <p><strong>Esta es nuestra última comunicación antes de proceder con acciones legales.</strong></p>
            
            <div class="critical">
                <p><strong>Factura:</strong> #{invoice_number}</p>
                <p><strong>Monto Total Adeudado:</strong> <span class="amount">${amount_due:,.2f}</span></p>
                <p><strong>Días de Atraso:</strong> {days_overdue} días</p>
            </div>
            
            <p>A pesar de nuestras múltiples comunicaciones, su cuenta permanece sin pagar. Lamentablemente, nos vemos obligados a tomar las siguientes medidas:</p>
            
            <ol>
                <li><strong>Plazo Final:</strong> 7 días calendario para regularizar el pago</li>
                <li><strong>Después del plazo:</strong> Iniciaremos proceso de cobro judicial</li>
                <li><strong>Costos adicionales:</strong> Usted será responsable de todos los costos legales y de cobranza</li>
                <li><strong>Reporte crediticio:</strong> Su cuenta será reportada a las agencias de crédito</li>
            </ol>
            
            <p style="color: #e53e3e; font-weight: bold;">ESTA ES SU ÚLTIMA OPORTUNIDAD DE RESOLVER ESTO AMIGABLEMENTE.</p>
            
            <p>Si hay circunstancias atenuantes que le han impedido realizar el pago, debe comunicarse con nosotros INMEDIATAMENTE.</p>
            
            <p><strong>Contacto Urgente:</strong><br>
            Email: billing@professionalhubs.com<br>
            Teléfono: [NÚMERO]<br>
            Horario: Lunes a Viernes, 9:00 AM - 5:00 PM</p>
            
            <p>Cordialmente,<br>
            <strong>Professional Hubs</strong><br>
            Departamento Legal y de Cobranzas</p>
            
            <hr>
            <p style="font-size: 11px; color: #666;">
                Este mensaje constituye una notificación formal de cobro según las leyes de Puerto Rico.
            </p>
        </div>
    </div>
</body>
</html>
"""
        return subject, body
    
    def _get_danger_zone_template(
        self, client_name, invoice_number, amount_due, days_overdue, due_date
    ) -> tuple:
        """Notificación de zona de peligro (60+ días) - solo informativa."""
        subject = f"Cuenta Crítica - Factura #{invoice_number}"
        
        body = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial; padding: 20px;">
    <h2 style="color: #e53e3e;">Estado de Cuenta Crítico</h2>
    
    <p>{client_name},</p>
    
    <p>Su factura #{invoice_number} por ${amount_due:,.2f} lleva {days_overdue} días vencida.</p>
    
    <p>Este mensaje es solo informativo. Nuestro departamento legal tomará las acciones apropiadas.</p>
    
    <p>Professional Hubs</p>
</body>
</html>
"""
        return subject, body
    
    def _html_to_text(self, html: str) -> str:
        """Convierte HTML a texto plano para clientes que no soportan HTML."""
        # Implementación básica - en producción usar librería como html2text
        import re
        text = re.sub('<[^<]+?>', '', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


postmark_service = PostmarkEmailService()