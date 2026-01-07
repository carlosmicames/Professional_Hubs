# conflict_api/app/crud/intake.py
"""
CRUD para IntakeCallSimple.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.intake import IntakeCallSimple, EstadoConsulta  # FIXED: Added EstadoConsulta import
from app.schemas.intake import IntakeCallCreate, IntakeCallUpdate  # Add schemas if needed


class CRUDIntakeSimple(CRUDBase):
    """CRUD para intake calls simplificados."""
    
    def get_por_firma(
        self,
        db: Session,
        id: int,
        firm_id: int,
        include_inactive: bool = False
    ) -> Optional[IntakeCallSimple]:
        """Obtiene intake por ID y firma."""
        query = db.query(IntakeCallSimple).filter(
            IntakeCallSimple.id == id,
            IntakeCallSimple.firma_id == firm_id
        )
        
        if not include_inactive:
            query = query.filter(IntakeCallSimple.esta_activo == True)
        
        return query.first()
    
    def get_multi_por_firma(
        self,
        db: Session,
        firm_id: int,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False
    ) -> List[IntakeCallSimple]:
        """Lista intakes del bufete."""
        query = db.query(IntakeCallSimple).filter(
            IntakeCallSimple.firma_id == firm_id
        )
        
        if not include_inactive:
            query = query.filter(IntakeCallSimple.esta_activo == True)
        
        return query.order_by(
            IntakeCallSimple.creado_en.desc()
        ).offset(skip).limit(limit).all()
    
    def get_by_call_sid(
        self,
        db: Session,
        call_sid: str
    ) -> Optional[IntakeCallSimple]:
        """Obtiene intake por Twilio Call SID."""
        return db.query(IntakeCallSimple).filter(
            IntakeCallSimple.twilio_call_sid == call_sid
        ).first()
    
    def get_pending_forms(
        self,
        db: Session,
        firm_id: int
    ) -> List[IntakeCallSimple]:
        """Obtiene consultas pendientes de formulario."""
        return db.query(IntakeCallSimple).filter(
            IntakeCallSimple.firma_id == firm_id,
            IntakeCallSimple.estado == EstadoConsulta.PENDIENTE,
            IntakeCallSimple.whatsapp_form_sent == True,
            IntakeCallSimple.whatsapp_form_completed == False
        ).all()
    
    def create(
        self,
        db: Session,
        obj_in: dict,
        firm_id: int
    ) -> IntakeCallSimple:
        """Create a new intake call record."""
        obj_in['firma_id'] = firm_id
        db_obj = IntakeCallSimple(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


crud_intake_simple = CRUDIntakeSimple(IntakeCallSimple)