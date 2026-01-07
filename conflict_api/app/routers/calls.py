# conflict_api/app/routers/calls_simple.py
"""
Endpoints simplificados para AI Call Agent.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_firm_id
from app.services.call_agent import simple_agent
from app.services.whatsapp_forms import whatsapp_form_service
from app.services.calendar_service import calendar_service
from app.services.email_service import email_service
from app.models.intake import IntakeCallSimple, EstadoConsulta
from app.crud.intake_simple import crud_intake_simple

router = APIRouter(
    prefix="/calls",
    tags=["AI Call Agent - Simple"]
)


@router.post("/incoming", response_class=Response)
async def incoming_call_handler(
    From: str = Form(...),
    CallSid: str = Form(...),
    SpeechResult: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Maneja llamada entrante de Twilio.
    
    Este endpoint se llama 2 veces:
    1. Primera llamada: cuando entra la llamada (sin SpeechResult)
    2. Llamadas subsecuentes: cada vez que el cliente habla (con SpeechResult)
    """
    
    # Buscar o crear intake call
    intake = crud_intake_simple.get_by_call_sid(db, CallSid)
    
    if not intake:
        # Primera llamada - crear registro
        intake = crud_intake_simple.create(
            db=db,
            obj_in={
                "numero_llamante": From,
                "twilio_call_sid": CallSid,
                "idioma_detectado": "es"  # Default español, se detecta después
            },
            firm_id=1  # TODO: Obtener de configuración
        )
        
        # Saludo inicial
        response_data = simple_agent.initial_greeting("es")
        response_text = response_data.get("respuesta", "")
        
    else:
        # Llamada subsecuente - procesar respuesta
        if not SpeechResult:
            response_text = "¿Sigue ahí? ¿En qué puedo ayudarle?"
        else:
            # Detectar idioma si es primera interacción
            if not intake.nombre:
                detected_lang = simple_agent.detect_language(SpeechResult)
                intake.idioma_detectado = detected_lang
                db.commit()
            
            # Procesar mensaje con AI
            response_data = simple_agent.process_message(
                user_message=SpeechResult,
                detected_language=intake.idioma_detectado.value
            )
            
            # Extraer datos según idioma
            if intake.idioma_detectado.value == "es":
                response_text = response_data.get("respuesta", "")
                solicita_consulta = response_data.get("solicita_consulta", False)
                nombre = response_data.get("nombre")
                tipo_caso = response_data.get("tipo_caso")
                telefono = response_data.get("telefono")
                completa = response_data.get("conversacion_completa", False)
            else:
                response_text = response_data.get("response", "")
                solicita_consulta = response_data.get("requesting_consultation", False)
                nombre = response_data.get("name")
                tipo_caso = response_data.get("case_type")
                telefono = response_data.get("phone")
                completa = response_data.get("conversation_complete", False)
            
            # Actualizar datos en DB
            if nombre and not intake.nombre:
                intake.nombre = nombre
            if tipo_caso and not intake.tipo_caso:
                # Mapear tipo en inglés a español
                case_type_map = {
                    "family": "familia",
                    "injury": "lesiones",
                    "labor": "laboral",
                    "real_estate": "inmobiliario",
                    "criminal": "criminal",
                    "commercial": "comercial",
                    "other": "otro"
                }
                intake.tipo_caso = case_type_map.get(tipo_caso, tipo_caso)
            if telefono and not intake.telefono_contacto:
                intake.telefono_contacto = telefono
            
            db.commit()
            
            # Si la conversación está completa Y tiene todos los datos
            if completa and solicita_consulta and intake.nombre and intake.tipo_caso and intake.telefono_contacto:
                # 1. Crear evento de calendario
                calendar_result = calendar_service.create_consultation_event(
                    client_name=intake.nombre,
                    client_phone=intake.telefono_contacto,
                    case_type=intake.tipo_caso.value
                )
                
                if calendar_result:
                    intake.fecha_cita = calendar_result["fecha_cita"]
                    intake.abogado_asignado = calendar_result["abogado_asignado"]
                    intake.google_calendar_event_id = calendar_result["event_id"]
                
                # 2. Enviar formulario WhatsApp
                form_sent = whatsapp_form_service.send_intake_form(
                    to_phone=intake.telefono_contacto,
                    nombre=intake.nombre,
                    tipo_caso=intake.tipo_caso.value,
                    intake_id=intake.id,
                    language=intake.idioma_detectado.value
                )
                
                if form_sent:
                    intake.whatsapp_form_sent = True
                
                # 3. Enviar email a abogado
                if calendar_result:
                    email_service.send_new_consultation_notification(
                        attorney_email=calendar_result["attorney_email"],
                        client_name=intake.nombre,
                        client_phone=intake.telefono_contacto,
                        case_type=intake.tipo_caso.value,
                        appointment_time=calendar_result["fecha_cita"],
                        calendar_link=calendar_result["calendar_link"],
                        intake_id=intake.id
                    )
                
                db.commit()
    
    # Generar respuesta TwiML
    twiml = _generate_twiml(response_text)
    return Response(content=twiml, media_type="application/xml")


def _generate_twiml(text: str) -> str:
    """Genera TwiML para Twilio."""
    from twilio.twiml.voice_response import VoiceResponse, Gather
    
    response = VoiceResponse()
    response.say(text, voice="Polly.Lupe", language="es-MX")
    
    # Esperar respuesta del cliente
    gather = Gather(
        input='speech',
        action='/api/v1/calls/incoming',
        method='POST',
        language='es-MX',
        speech_timeout='auto',
        timeout=10
    )
    response.append(gather)
    
    return str(response)


@router.post("/form-webhook")
async def form_submission_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Webhook para recibir respuestas del formulario (Jotform/Google Forms).
    
    Cuando el cliente completa el formulario, actualiza la info.
    """
    data = await request.json()
    
    # Extraer intake_id del formulario
    intake_id = data.get("intake_id")
    
    if not intake_id:
        raise HTTPException(400, "Missing intake_id")
    
    intake = crud_intake_simple.get(db, intake_id)
    
    if not intake:
        raise HTTPException(404, "Intake not found")
    
    # Actualizar con datos del formulario
    intake.nombre_completo = data.get("nombre_completo")
    intake.email = data.get("email")
    intake.descripcion_caso = data.get("descripcion_caso")
    intake.whatsapp_form_completed = True
    intake.estado = EstadoConsulta.FORMULARIO_COMPLETADO
    intake.form_submission_id = data.get("submission_id")
    
    db.commit()
    
    # Notificar al abogado que el formulario está completo
    if intake.abogado_asignado:
        email_service.send_form_completed_notification(
            attorney_email=_get_attorney_email(intake.abogado_asignado),
            client_name=intake.nombre_completo,
            intake_id=intake.id
        )
    
    return {"status": "success"}


@router.get("/", response_model=List[dict])
def list_intakes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """Lista todos los intakes."""
    return crud_intake_simple.get_multi_por_firma(db, firm_id, skip, limit)


@router.get("/{intake_id}")
def get_intake(
    intake_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """Obtiene detalles de un intake."""
    intake = crud_intake_simple.get_por_firma(db, intake_id, firm_id)
    
    if not intake:
        raise HTTPException(404, "Intake not found")
    
    return intake


@router.post("/{intake_id}/confirm")
def confirm_consultation(
    intake_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Abogado confirma la consulta y acepta el caso.
    """
    intake = crud_intake_simple.get_por_firma(db, intake_id, firm_id)
    
    if not intake:
        raise HTTPException(404, "Intake not found")
    
    intake.estado = EstadoConsulta.CONFIRMADA
    db.commit()
    
    # Enviar confirmación al cliente
    whatsapp_form_service.send_confirmation_message(
        to_phone=intake.telefono_contacto,
        client_name=intake.nombre_completo or intake.nombre,
        appointment_time=intake.fecha_cita,
        attorney_name=intake.abogado_asignado,
        language=intake.idioma_detectado.value
    )
    
    return {"status": "confirmed"}


@router.post("/{intake_id}/reject")
def reject_consultation(
    intake_id: int,
    reason: str = None,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Abogado rechaza el caso.
    """
    intake = crud_intake_simple.get_por_firma(db, intake_id, firm_id)
    
    if not intake:
        raise HTTPException(404, "Intake not found")
    
    intake.estado = EstadoConsulta.RECHAZADA
    db.commit()
    
    # Cancelar evento de calendario si existe
    if intake.google_calendar_event_id:
        calendar_service.delete_event(intake.google_calendar_event_id)
    
    # Notificar al cliente (opcional - puede ser delicado)
    # whatsapp_form_service.send_rejection_message(...)
    
    return {"status": "rejected"}


def _get_attorney_email(attorney_name: str) -> str:
    """Helper para obtener email del abogado por nombre."""
    # En producción, esto vendría de la DB
    attorney_emails = {
        "Lcda. María González": "maria@professionalhubs.com",
        "Lcdo. Carlos Pérez": "carlos@professionalhubs.com",
        "Lcdo. Juan Rodríguez": "juan@professionalhubs.com",
        "Lcda. Ana López": "ana@professionalhubs.com",
        "Lcdo. Roberto Martínez": "roberto@professionalhubs.com",
        "Lcdo. Luis Torres": "luis@professionalhubs.com",
    }
    return attorney_emails.get(attorney_name, "info@professionalhubs.com")