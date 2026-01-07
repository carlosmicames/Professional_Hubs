"""
Servicio de IA para generar cartas de renuncia de representación.
Usa Anthropic Claude API para sintetizar logs de comunicación.
"""

import os
from typing import List, Optional, Dict
from datetime import datetime


class AIResignationService:
    """
    Genera cartas formales de renuncia de representación usando IA.
    Analiza historial de comunicaciones de cobro.
    """
    
    def __init__(self):
        """Inicializa cliente de Anthropic (lazy loading)."""
        self._client = None
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = "claude-sonnet-4-20250514"
    
    @property
    def client(self):
        """Lazy initialization of Anthropic client."""
        if self._client is None and self.api_key:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as e:
                print(f"Failed to initialize Anthropic client: {e}")
                return None
        return self._client
    
    def generate_resignation_letter(
        self,
        client_name: str,
        invoice_number: str,
        amount_due: float,
        days_overdue: int,
        communication_logs: List[Dict],
        case_details: Optional[str] = None,
        attorney_name: str = "Professional Hubs"
    ) -> Dict:
        """
        Genera carta formal de renuncia de representación.
        
        Args:
            client_name: Nombre del cliente
            invoice_number: Número de factura
            amount_due: Monto adeudado
            days_overdue: Días de atraso
            communication_logs: Lista de logs de comunicación
            case_details: Detalles opcionales del caso
            attorney_name: Nombre del abogado/bufete
        
        Returns:
            Dict con la carta generada y metadata
        """
        if not self.client:
            return {
                "success": False,
                "error": "Anthropic API not configured. Set ANTHROPIC_API_KEY environment variable."
            }
        
        try:
            # Construir prompt con toda la información
            system_prompt = self._get_system_prompt()
            user_prompt = self._build_user_prompt(
                client_name, invoice_number, amount_due, days_overdue,
                communication_logs, case_details, attorney_name
            )
            
            # Llamar a Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2500,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extraer texto de respuesta
            letter_text = response.content[0].text
            
            return {
                "success": True,
                "letter": letter_text,
                "generated_at": datetime.utcnow().isoformat(),
                "model_used": self.model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate letter: {str(e)}"
            }
    
    def _get_system_prompt(self) -> str:
        """
        System prompt para Claude - define rol y restricciones.
        """
        return """Eres un asistente legal profesional especializado en derecho de Puerto Rico.

Tu tarea es redactar cartas formales de renuncia de representación (withdrawal of representation) que cumplan con:

1. **Ética Profesional del Colegio de Abogados de Puerto Rico**
2. **Reglas de Conducta Profesional de PR**
3. **Estándar formal de comunicación legal**

FORMATO REQUERIDO:
- Encabezado con fecha
- Destinatario formal
- Referencia al caso/cliente
- Exposición cronológica de hechos
- Fundamento legal para la renuncia
- Notificación de plazos y responsabilidades del cliente
- Cierre profesional
- Firma del abogado

TONO:
- Profesional, respetuoso pero firme
- Sin lenguaje emocional o acusatorio
- Enfocado en hechos verificables
- Cita fechas específicas de comunicaciones
- Menciona montos exactos

FUNDAMENTOS LEGALES:
- Regla 1.16 del Código de Ética Profesional (retiro de representación)
- Incumplimiento de obligaciones contractuales del cliente
- Falta de cooperación que impide representación efectiva
- Derecho del abogado a cobrar honorarios devengados

La carta debe ser lista para imprimir en papel membretado sin necesidad de edición."""
    
    def _build_user_prompt(
        self,
        client_name: str,
        invoice_number: str,
        amount_due: float,
        days_overdue: int,
        communication_logs: List[Dict],
        case_details: Optional[str],
        attorney_name: str
    ) -> str:
        """
        Construye prompt detallado para Claude con todos los datos.
        """
        # Organizar logs cronológicamente
        sorted_logs = sorted(communication_logs, key=lambda x: x.get('sent_at', ''))
        
        # Construir lista de comunicaciones
        communications_summary = []
        for i, log in enumerate(sorted_logs, 1):
            comm_type = log.get('type', 'unknown').upper()
            sent_at = log.get('sent_at', '')
            status = log.get('status', 'sent')
            
            # Formatear fecha
            try:
                date_obj = datetime.fromisoformat(sent_at.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%d de %B de %Y')
            except:
                formatted_date = sent_at
            
            communications_summary.append(
                f"   {i}. {formatted_date} - {comm_type} ({status})"
            )
        
        communications_text = "\n".join(communications_summary)
        
        # Construir prompt completo
        prompt = f"""Redacta una carta formal de renuncia de representación con la siguiente información:

**INFORMACIÓN DEL CLIENTE:**
- Nombre: {client_name}
- Factura: #{invoice_number}
- Monto Adeudado: ${amount_due:,.2f}
- Días de Atraso: {days_overdue} días

**DETALLES DEL CASO (si aplica):**
{case_details or 'Servicios legales generales'}

**HISTORIAL DE COMUNICACIONES:**
Hemos intentado contactar al cliente mediante los siguientes medios:

{communications_text}

Total de intentos de comunicación: {len(communication_logs)}

**ABOGADO/BUFETE:**
{attorney_name}

**INSTRUCCIONES ESPECÍFICAS:**
1. Inicia con la fecha de hoy: {datetime.now().strftime('%d de %B de %Y')}
2. Menciona TODAS las fechas de comunicación listadas arriba
3. Explica que a pesar de múltiples intentos, no hemos recibido:
   - Pago de honorarios
   - Respuesta del cliente
   - Cooperación necesaria para representación efectiva
4. Cita la Regla 1.16 del Código de Ética Profesional de PR
5. Notifica que:
   - La representación termina 15 días después de recibir esta carta
   - El cliente debe buscar nuevo abogado de inmediato
   - Hay plazos pendientes que el cliente debe atender
   - Professional Hubs retiene derecho a cobrar honorarios devengados
6. Ofrece entregar expediente al nuevo abogado (una vez pagados honorarios)
7. Incluye línea para firma del abogado

**IMPORTANTE:** 
- Usa tono profesional y respetuoso
- No uses lenguaje amenazante
- Enfócate en incumplimiento de obligaciones contractuales
- La carta debe ser lista para imprimir y enviar por correo certificado

Redacta SOLO la carta, sin comentarios adicionales."""
        
        return prompt
    
    def generate_summary_for_dashboard(
        self,
        client_name: str,
        days_overdue: int,
        communication_count: int,
        last_contact_date: Optional[str]
    ) -> str:
        """
        Genera resumen breve para mostrar en dashboard.
        """
        if not self.client:
            return f"Cliente: {client_name} | {days_overdue} días vencido | {communication_count} intentos"
        
        try:
            prompt = f"""Resume en 2-3 líneas la situación de cobro:
- Cliente: {client_name}
- Días vencido: {days_overdue}
- Intentos de contacto: {communication_count}
- Último contacto: {last_contact_date or 'N/A'}

Responde SOLO con el resumen, sin preámbulos."""
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
        
        except:
            return f"{client_name}: {days_overdue} días vencido, {communication_count} recordatorios sin respuesta"


ai_resignation_service = AIResignationService()