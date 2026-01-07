# conflict_api/app/services/call_agent.py
"""
AI Agent simplificado - Solo recopila info mínima.
"""

import json
import os
from typing import Dict, List, Optional
import anthropic


class SimpleCallAgent:
    """
    Agente AI simplificado para llamadas.
    Solo pregunta: ¿Consulta? → Nombre → Tipo de caso → Teléfono
    """
    
    def __init__(self):
        # Lazy initialization - don't create client until needed
        self._client = None
        self._api_key = os.getenv("ANTHROPIC_API_KEY")
        
        self.system_prompt_es = """Eres la recepcionista virtual de Professional Hubs, un bufete de abogados en Puerto Rico.

Tu trabajo es MUY SIMPLE:

1. **Saludo:** "Buenos días/tardes, gracias por llamar a Professional Hubs. ¿Está llamando para solicitar una consulta legal?"

2. **Si dice SÍ:**
   - "Perfecto, con gusto le ayudo. ¿Cuál es su nombre?"
   - "¿Qué tipo de caso necesita? Por ejemplo: divorcio, accidente, caso laboral, etc."
   - "¿Cuál es su número de teléfono para contactarle?"
   - "Excelente [Nombre]. Le estaremos enviando un mensaje de WhatsApp con un formulario breve para completar más detalles. Un abogado especializado en [tipo de caso] se comunicará con usted para coordinar la consulta. ¿Tiene alguna pregunta?"

3. **Si dice NO o pregunta otra cosa:**
   - "Entiendo. ¿En qué puedo ayudarle entonces?"
   - Si pide información general: dar info básica y sugerir visitar website
   - Si pide hablar con alguien: "Por favor llame en horario de oficina o deje un mensaje"

**IMPORTANTE:**
- Sé breve y eficiente
- NO preguntes más de lo necesario (solo nombre, tipo caso, teléfono)
- NO des consejos legales
- Habla como recepcionista humana, cálida pero profesional

**RESPONDE EN JSON:**
```json
{
    "respuesta": "lo que dirías al cliente",
    "solicita_consulta": true/false,
    "nombre": "si lo obtuviste",
    "tipo_caso": "familia/lesiones/laboral/inmobiliario/criminal/comercial/otro",
    "telefono": "si lo obtuviste",
    "conversacion_completa": true/false,
    "siguiente_accion": "que hacer ahora"
}
```
"""
        
        self.system_prompt_en = """You are the virtual receptionist for Professional Hubs, a law firm in Puerto Rico.

Your job is VERY SIMPLE:

1. **Greeting:** "Good morning/afternoon, thank you for calling Professional Hubs. Are you calling to request a legal consultation?"

2. **If YES:**
   - "Perfect, I'm happy to help. What is your name?"
   - "What type of case do you need help with? For example: divorce, accident, employment case, etc."
   - "What is your phone number so we can contact you?"
   - "Excellent [Name]. We'll be sending you a WhatsApp message with a brief form to complete more details. An attorney specializing in [case type] will contact you to schedule the consultation. Do you have any questions?"

3. **If NO or asks something else:**
   - "I understand. How else can I help you?"
   - If asks for general info: provide basic info and suggest visiting website
   - If wants to speak to someone: "Please call during office hours or leave a message"

**IMPORTANT:**
- Be brief and efficient
- DON'T ask more than necessary (only name, case type, phone)
- DON'T give legal advice
- Speak like a human receptionist, warm but professional

**RESPOND IN JSON:**
```json
{
    "response": "what you would say to client",
    "requesting_consultation": true/false,
    "name": "if obtained",
    "case_type": "family/injury/labor/real_estate/criminal/commercial/other",
    "phone": "if obtained",
    "conversation_complete": true/false,
    "next_action": "what to do now"
}
```
"""
    
    @property
    def client(self):
        """Lazy initialization of Anthropic client."""
        if self._client is None:
            if not self._api_key:
                print("⚠️  ANTHROPIC_API_KEY not set - AI call features disabled")
                return None
            
            try:
                self._client = anthropic.Anthropic(api_key=self._api_key)
            except Exception as e:
                print(f"⚠️  Failed to initialize Anthropic client: {e}")
                return None
        
        return self._client
    
    def detect_language(self, text: str) -> str:
        """
        Detecta idioma del caller (español o inglés).
        """
        english_words = ['hello', 'hi', 'yes', 'no', 'please', 'thank', 'you', 'need', 'help', 'lawyer', 'attorney']
        spanish_words = ['hola', 'buenos', 'días', 'tardes', 'sí', 'si', 'gracias', 'necesito', 'ayuda', 'abogado']
        
        text_lower = text.lower()
        
        english_count = sum(1 for word in english_words if word in text_lower)
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        
        return "en" if english_count > spanish_count else "es"
    
    def process_message(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        detected_language: str = "es"
    ) -> Dict:
        """
        Procesa mensaje del usuario.
        """
        if conversation_history is None:
            conversation_history = []
        
        # Check if client is available
        if not self.client:
            # Fallback response when API is not configured
            return {
                "respuesta" if detected_language == "es" else "response": 
                    "Lo siento, el servicio de asistencia virtual no está disponible en este momento. Por favor contacte directamente a nuestra oficina." if detected_language == "es" 
                    else "Sorry, the virtual assistant service is not available at this time. Please contact our office directly.",
                "solicita_consulta" if detected_language == "es" else "requesting_consultation": False,
                "conversacion_completa" if detected_language == "es" else "conversation_complete": True,
                "error": "Anthropic API not configured"
            }
        
        try:
            system_prompt = self.system_prompt_es if detected_language == "es" else self.system_prompt_en
            
            messages = conversation_history + [{"role": "user", "content": user_message}]
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                system=system_prompt,
                messages=messages
            )
            
            response_text = response.content[0].text
            
            try:
                # Extract JSON from response
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback
                result = {
                    "respuesta" if detected_language == "es" else "response": response_text,
                    "solicita_consulta" if detected_language == "es" else "requesting_consultation": False,
                    "conversacion_completa" if detected_language == "es" else "conversation_complete": False
                }
            
            return result
            
        except Exception as e:
            print(f"Error in process_message: {e}")
            return {
                "respuesta" if detected_language == "es" else "response": 
                    "Disculpe, tuve un problema. ¿Puede repetir?" if detected_language == "es" 
                    else "Sorry, I had an issue. Can you repeat?",
                "error": str(e)
            }
    
    def initial_greeting(self, language: str = "es") -> Dict:
        """Saludo inicial."""
        if language == "es":
            return {
                "respuesta": "Buenos días, gracias por llamar a Professional Hubs. ¿Está llamando para solicitar una consulta legal?",
                "conversacion_completa": False
            }
        else:
            return {
                "response": "Good morning, thank you for calling Professional Hubs. Are you calling to request a legal consultation?",
                "conversation_complete": False
            }


# Singleton instance - will only initialize client when actually used
simple_agent = SimpleCallAgent()