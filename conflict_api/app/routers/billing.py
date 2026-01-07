"""
Endpoints para gestión de facturación y recordatorios.
"""

from app.models.billing_communication import CommunicationType, CommunicationStatus
from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_firm_id
from app.crud.billing_communication import crud_billing_communication
from app.services.ai_resignation_service import ai_resignation_service
from app.services.billing_scheduler import billing_scheduler


router = APIRouter(
    prefix="/billing",
    tags=["Billing & Collections"],
    responses={404: {"description": "Not found"}}
)


# ============================================================================
# SCHEMAS
# ============================================================================

class InvoiceSummary(BaseModel):
    """Resumen de factura con días de atraso."""
    id: int
    invoice_number: str
    client_name: str
    client_email: Optional[str]
    client_phone: Optional[str]
    amount: float
    due_date: date
    days_overdue: int
    status: str
    last_communication_date: Optional[str]
    communication_count: int


class DashboardStats(BaseModel):
    """Estadísticas para dashboard."""
    total_outstanding: float
    overdue_30_plus: int
    overdue_30_plus_amount: float
    danger_zone_count: int
    danger_zone_amount: float
    total_invoices: int


class ResignationLetterRequest(BaseModel):
    """Request para generar carta de renuncia."""
    case_details: Optional[str] = None
    attorney_name: str = "Professional Hubs"


class ResignationLetterResponse(BaseModel):
    """Response con carta generada."""
    success: bool
    letter: Optional[str]
    generated_at: Optional[str]
    client_name: str
    invoice_number: str
    error: Optional[str] = None


# ============================================================================
# ENDPOINTS - DASHBOARD & STATS
# ============================================================================

@router.get(
    "/dashboard/stats",
    response_model=DashboardStats,
    summary="Obtener estadísticas del dashboard"
)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Obtiene estadísticas de facturación para el dashboard.
    
    - **total_outstanding**: Total de dinero pendiente
    - **overdue_30_plus**: Cantidad de facturas vencidas 30+ días
    - **danger_zone_count**: Facturas en zona de peligro (60+ días)
    """
    # Query SQL para estadísticas
    query = """
        SELECT 
            COUNT(*) as total_invoices,
            COALESCE(SUM(amount), 0) as total_outstanding,
            COALESCE(SUM(CASE WHEN CURRENT_DATE - due_date >= 30 THEN 1 ELSE 0 END), 0) as overdue_30_plus,
            COALESCE(SUM(CASE WHEN CURRENT_DATE - due_date >= 30 THEN amount ELSE 0 END), 0) as overdue_30_plus_amount,
            COALESCE(SUM(CASE WHEN CURRENT_DATE - due_date >= 60 THEN 1 ELSE 0 END), 0) as danger_zone_count,
            COALESCE(SUM(CASE WHEN CURRENT_DATE - due_date >= 60 THEN amount ELSE 0 END), 0) as danger_zone_amount
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        WHERE i.status = 'pending'
        AND c.firma_id = :firm_id
        AND i.esta_activo = true
    """
    
    result = db.execute(query, {"firm_id": firm_id}).fetchone()
    
    return DashboardStats(
        total_outstanding=float(result[1]),
        overdue_30_plus=int(result[2]),
        overdue_30_plus_amount=float(result[3]),
        danger_zone_count=int(result[4]),
        danger_zone_amount=float(result[5]),
        total_invoices=int(result[0])
    )


@router.get(
    "/invoices/overdue",
    response_model=List[InvoiceSummary],
    summary="Listar facturas vencidas"
)
def list_overdue_invoices(
    min_days: int = Query(0, description="Mínimo de días de atraso"),
    max_days: int = Query(None, description="Máximo de días de atraso"),
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Lista facturas vencidas con información de comunicaciones.
    
    - **min_days**: Filtrar por mínimo de días de atraso (ej: 30 para ver solo 30+ días)
    - **max_days**: Filtrar por máximo de días (ej: 59 para excluir danger zone)
    """
    # Construir query con filtros
    query = """
        SELECT 
            i.id,
            i.invoice_number,
            c.nombre || ' ' || COALESCE(c.apellido, '') as client_name,
            c.email,
            c.telefono,
            i.amount,
            i.due_date,
            CURRENT_DATE - i.due_date as days_overdue,
            i.status
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        WHERE i.status = 'pending'
        AND c.firma_id = :firm_id
        AND i.esta_activo = true
        AND CURRENT_DATE - i.due_date >= :min_days
    """
    
    params = {"firm_id": firm_id, "min_days": min_days}
    
    if max_days:
        query += " AND CURRENT_DATE - i.due_date <= :max_days"
        params["max_days"] = max_days
    
    query += " ORDER BY days_overdue DESC"
    
    results = db.execute(query, params).fetchall()
    
    invoices = []
    for row in results:
        # Obtener última comunicación
        last_comm = crud_billing_communication.get_last_communication(db, row[0])
        comm_count = crud_billing_communication.get_communication_count(db, row[0])
        
        invoices.append(InvoiceSummary(
            id=row[0],
            invoice_number=row[1],
            client_name=row[2],
            client_email=row[3],
            client_phone=row[4],
            amount=float(row[5]),
            due_date=row[6],
            days_overdue=int(row[7]),
            status=row[8],
            last_communication_date=last_comm.sent_at.isoformat() if last_comm else None,
            communication_count=comm_count
        ))
    
    return invoices


@router.get(
    "/invoices/danger-zone",
    response_model=List[InvoiceSummary],
    summary="Listar facturas en zona de peligro"
)
def list_danger_zone_invoices(
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Lista facturas en zona de peligro (60+ días vencidas).
    Estas requieren acción manual (posible carta de renuncia).
    """
    return list_overdue_invoices(min_days=60, db=db, firm_id=firm_id)


# ============================================================================
# ENDPOINTS - COMMUNICATION LOGS
# ============================================================================

@router.get(
    "/invoices/{invoice_id}/communications",
    summary="Ver historial de comunicaciones"
)
def get_invoice_communications(
    invoice_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Obtiene historial completo de comunicaciones para una factura.
    """
    # TODO: Verificar que la factura pertenece al bufete
    
    logs = crud_billing_communication.get_by_invoice(db, invoice_id)
    
    return {
        "invoice_id": invoice_id,
        "total_communications": len(logs),
        "communications": [
            {
                "id": log.id,
                "type": log.type.value,
                "status": log.status.value,
                "sent_at": log.sent_at.isoformat(),
                "days_overdue_when_sent": log.days_overdue_when_sent,
                "reminder_sequence": log.reminder_sequence,
                "delivered_at": log.delivered_at.isoformat() if log.delivered_at else None,
                "external_id": log.external_id
            }
            for log in logs
        ]
    }


# ============================================================================
# ENDPOINTS - AI RESIGNATION LETTER
# ============================================================================

@router.post(
    "/generate-resignation/{invoice_id}",
    response_model=ResignationLetterResponse,
    summary="Generar carta de renuncia con IA"
)
def generate_resignation_letter(
    invoice_id: int,
    request: ResignationLetterRequest,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Genera carta formal de renuncia de representación usando IA.
    
    Sintetiza todos los logs de comunicación y genera documento legal
    listo para imprimir y enviar por correo certificado.
    
    **Requisitos:**
    - Factura debe tener 60+ días de atraso
    - Debe existir historial de comunicaciones
    """
    # Obtener información de la factura
    query = """
        SELECT 
            i.invoice_number,
            i.amount,
            i.due_date,
            c.nombre || ' ' || COALESCE(c.apellido, '') as client_name,
            CURRENT_DATE - i.due_date as days_overdue
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        WHERE i.id = :invoice_id
        AND c.firma_id = :firm_id
        AND i.esta_activo = true
    """
    
    result = db.execute(query, {"invoice_id": invoice_id, "firm_id": firm_id}).fetchone()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada"
        )
    
    invoice_number, amount, due_date, client_name, days_overdue = result
    
    # Verificar que esté en danger zone
    if days_overdue < 60:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Factura solo tiene {days_overdue} días de atraso. Se requiere 60+ días para generar carta de renuncia."
        )
    
    # Obtener historial de comunicaciones
    logs = crud_billing_communication.get_by_invoice(db, invoice_id)
    
    if len(logs) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere al menos 3 intentos de comunicación antes de generar carta de renuncia."
        )
    
    # Convertir logs a formato para IA
    log_dicts = [
        {
            "type": log.type.value,
            "status": log.status.value,
            "sent_at": log.sent_at.isoformat(),
            "days_overdue_when_sent": log.days_overdue_when_sent
        }
        for log in logs
    ]
    
    # Generar carta con IA
    result = ai_resignation_service.generate_resignation_letter(
        client_name=client_name,
        invoice_number=invoice_number,
        amount_due=float(amount),
        days_overdue=int(days_overdue),
        communication_logs=log_dicts,
        case_details=request.case_details,
        attorney_name=request.attorney_name
    )
    
    if not result.get('success'):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get('error', 'Failed to generate letter')
        )
    
    # Registrar que se generó la carta
    crud_billing_communication.create_log(
        db=db,
        invoice_id=invoice_id,
        type=CommunicationType.LETTER,
        message_body="AI-generated resignation letter created",
        days_overdue=int(days_overdue),
        reminder_sequence=99,  # Código especial para cartas de renuncia
        status=CommunicationStatus.SENT
    )
    
    return ResignationLetterResponse(
        success=True,
        letter=result['letter'],
        generated_at=result['generated_at'],
        client_name=client_name,
        invoice_number=invoice_number
    )


@router.get(
    "/generate-resignation/{invoice_id}/pdf",
    summary="Descargar carta de renuncia como PDF"
)
def download_resignation_letter_pdf(
    invoice_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Genera y descarga carta de renuncia como PDF.
    
    TODO: Implementar generación de PDF usando reportlab o similar.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="PDF generation not yet implemented. Use the POST endpoint to get letter text."
    )


# ============================================================================
# ENDPOINTS - MANUAL ACTIONS
# ============================================================================

@router.post(
    "/scheduler/trigger",
    summary="Trigger manual del scheduler"
)
def manual_trigger_scheduler(
    firm_id: int = Depends(get_firm_id)
):
    """
    Ejecuta manualmente el proceso de recordatorios.
    Útil para testing o ejecución fuera de horario programado.
    """
    try:
        billing_scheduler.manual_trigger()
        return {
            "success": True,
            "message": "Scheduler triggered successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger scheduler: {str(e)}"
        )


@router.get(
    "/scheduler/status",
    summary="Estado del scheduler"
)
def get_scheduler_status():
    """Obtiene estado actual del scheduler."""
    return {
        "is_running": billing_scheduler.is_running,
        "reminder_days": billing_scheduler.reminder_days,
        "danger_zone_threshold": billing_scheduler.danger_zone_days
    }