# conflict_api/app/models/intake.py
"""
Modelo simplificado de Intake Call.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class IdiomaLlamada(str, enum.Enum):
    """Idiomas detectados."""
    ESPANOL = "es"
    INGLES = "en"


class TipoCasoSimple(str, enum.Enum):
    """Tipos de casos para routing de abogados."""
    FAMILIA = "familia"  # Divorcio, custodia
    LESIONES = "lesiones"  # Accidentes, lesiones personales
    LABORAL = "laboral"  # Despidos, discriminación
    INMOBILIARIO = "inmobiliario"  # Hipotecas, desahucios
    CRIMINAL = "criminal"  # Casos criminales
    COMERCIAL = "comercial"  # Contratos, negocios
    OTRO = "otro"


class EstadoConsulta(str, enum.Enum):
    """Estado de la consulta."""
    PENDIENTE = "pendiente"  # Esperando respuesta del cliente (formulario)
    FORMULARIO_COMPLETADO = "formulario_completado"  # Cliente completó formulario
    CONFIRMADA = "confirmada"  # Abogado confirmó cita
    RECHAZADA = "rechazada"  # Abogado rechazó caso
    CANCELADA = "cancelada"  # Cliente canceló


class IntakeCallSimple(Base):
    """
    Llamada de intake simplificada.
    Solo recopila info básica durante la llamada.
    """
    
    __tablename__ = "intake_calls_simple"
    
    id = Column(Integer, primary_key=True, index=True)
    firma_id = Column(Integer, ForeignKey("firmas.id"), nullable=False, index=True)
    
    # Info de llamada
    twilio_call_sid = Column(String(100), unique=True, index=True)
    numero_llamante = Column(String(20), nullable=False)
    idioma_detectado = Column(Enum(IdiomaLlamada), default=IdiomaLlamada.ESPANOL)
    
    # Info básica recopilada en llamada (mínimo)
    nombre = Column(String(255), comment="Solo nombre (no apellidos)")
    tipo_caso = Column(Enum(TipoCasoSimple), comment="Tipo de caso para routing")
    telefono_contacto = Column(String(20), comment="Número confirmado")
    
    # Info del formulario WhatsApp (completado después)
    nombre_completo = Column(String(255), comment="Del formulario WhatsApp")
    email = Column(String(255), comment="Del formulario WhatsApp")
    descripcion_caso = Column(Text, comment="Del formulario WhatsApp")
    
    # Cita agendada
    fecha_cita = Column(DateTime, comment="Fecha/hora de consulta")
    abogado_asignado = Column(String(255), comment="Nombre del abogado asignado")
    google_calendar_event_id = Column(String(255), comment="ID del evento en Google Calendar")
    
    # Estado
    estado = Column(Enum(EstadoConsulta), default=EstadoConsulta.PENDIENTE)
    
    # Formulario WhatsApp
    whatsapp_form_sent = Column(Boolean, default=False, comment="Si se envió formulario")
    whatsapp_form_completed = Column(Boolean, default=False, comment="Si cliente completó formulario")
    form_submission_id = Column(String(255), comment="ID de respuesta del formulario")
    
    # Auditoría
    esta_activo = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    firma = relationship("Firma")
    
    def __repr__(self):
        return f"<IntakeCallSimple(id={self.id}, nombre='{self.nombre}', tipo={self.tipo_caso})>"