# conflict_api/app/services/calendar_service.py
"""
Servicio para crear eventos en Google Calendar.
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build


class CalendarService:
    """
    Crea eventos en Google Calendar para consultas.
    """
    
    def __init__(self):
        """
        Inicializa con Service Account credentials.
        """
        credentials_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "credentials.json")
        
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            self.service = build('calendar', 'v3', credentials=self.credentials)
            self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        except Exception as e:
            print(f"Calendar service not initialized: {e}")
            self.service = None
    
    def get_attorney_for_case_type(self, case_type: str) -> dict:
        """
        Retorna info del abogado según tipo de caso.
        
        En producción, esto vendría de una base de datos.
        """
        attorneys = {
            "familia": {
                "name": "Lcda. María González",
                "email": "maria@professionalhubs.com",
                "calendar_id": "maria@professionalhubs.com"
            },
            "lesiones": {
                "name": "Lcdo. Carlos Pérez",
                "email": "carlos@professionalhubs.com",
                "calendar_id": "carlos@professionalhubs.com"
            },
            "laboral": {
                "name": "Lcdo. Juan Rodríguez",
                "email": "juan@professionalhubs.com",
                "calendar_id": "juan@professionalhubs.com"
            },
            "inmobiliario": {
                "name": "Lcda. Ana López",
                "email": "ana@professionalhubs.com",
                "calendar_id": "ana@professionalhubs.com"
            },
            "criminal": {
                "name": "Lcdo. Roberto Martínez",
                "email": "roberto@professionalhubs.com",
                "calendar_id": "roberto@professionalhubs.com"
            },
            "comercial": {
                "name": "Lcdo. Luis Torres",
                "email": "luis@professionalhubs.com",
                "calendar_id": "luis@professionalhubs.com"
            }
        }
        
        return attorneys.get(case_type, attorneys["familia"])  # Default a familia
    
    def find_next_available_slot(self, attorney_calendar_id: str) -> datetime:
        """
        Encuentra el próximo slot disponible (simplificado).
        
        En producción, esto verificaría el calendario real.
        """
        # Por ahora, simplemente retorna mañana a las 2 PM
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    
    def create_consultation_event(
        self,
        client_name: str,
        client_phone: str,
        case_type: str,
        client_email: Optional[str] = None
    ) -> Optional[dict]:
        """
        Crea evento de consulta en Google Calendar.
        
        Returns:
            Dict con event_id, fecha_cita, abogado_asignado
        """
        if not self.service:
            print("Calendar service not available")
            return None
        
        try:
            # Obtener abogado según tipo de caso
            attorney = self.get_attorney_for_case_type(case_type)
            
            # Encontrar slot disponible
            start_time = self.find_next_available_slot(attorney["calendar_id"])
            end_time = start_time + timedelta(minutes=30)  # 30 min consultation
            
            # Crear evento
            event = {
                'summary': f'Consulta Inicial - {client_name}',
                'description': f"""
Tipo de caso: {case_type.upper()}
Cliente: {client_name}
Teléfono: {client_phone}
Email: {client_email or 'No proporcionado'}

Este es una consulta inicial. Pendiente de confirmación del formulario completo.
""",
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Puerto_Rico',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/Puerto_Rico',
                },
                'attendees': [
                    {'email': attorney["email"]},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 30},  # 30 min before
                    ],
                },
                'colorId': '11',  # Red for pending confirmation
            }
            
            # Añadir cliente si tiene email
            if client_email:
                event['attendees'].append({'email': client_email})
            
            # Insertar en calendario
            created_event = self.service.events().insert(
                calendarId=attorney["calendar_id"],
                body=event,
                sendUpdates='all'  # Send email to attendees
            ).execute()
            
            return {
                'event_id': created_event['id'],
                'fecha_cita': start_time,
                'abogado_asignado': attorney["name"],
                'attorney_email': attorney["email"],
                'calendar_link': created_event.get('htmlLink')
            }
            
        except Exception as e:
            print(f"Error creating calendar event: {e}")
            return None


calendar_service = CalendarService()