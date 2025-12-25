"""
Endpoints para Verificación de Conflictos de Interés.
Multi-tenant: Todos los endpoints filtran por firma_id del header.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_firm_id
from app.schemas.conflicto import BusquedaConflicto, ResultadoConflicto
from app.services.conflict_checker import conflict_checker

router = APIRouter(
    prefix="/conflictos",
    tags=["Verificación de Conflictos"],
    responses={400: {"description": "Datos de búsqueda inválidos"}}
)


@router.post(
    "/verificar",
    response_model=ResultadoConflicto,
    summary="Verificar conflictos de interés",
    description="""
    Busca conflictos de interés potenciales para un cliente nuevo.
    
    Realiza búsqueda exacta (case-insensitive) en nombres de clientes existentes.
    Incluye asuntos activos y cerrados para una verificación completa.
    
    **Uso típico:**
    Antes de aceptar un nuevo cliente, verificar si ya existe en el sistema
    o si está relacionado con algún asunto previo.
    """
)
def verificar_conflictos(
    busqueda: BusquedaConflicto,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Verifica conflictos de interés para un cliente potencial.
    
    Proporcione al menos uno de:
    - **nombre** + **apellido**: Para persona natural
    - **nombre_empresa**: Para empresa/corporación
    
    Retorna lista de conflictos encontrados con detalles del asunto.
    """
    # Validar que hay al menos un criterio de búsqueda
    if not any([busqueda.nombre, busqueda.apellido, busqueda.nombre_empresa]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un criterio de búsqueda (nombre, apellido, o nombre_empresa)"
        )
    
    # Realizar búsqueda de conflictos
    resultado = conflict_checker.verificar_conflictos(
        db=db,
        firm_id=firm_id,
        busqueda=busqueda
    )
    
    return resultado


@router.get(
    "/estado",
    summary="Estado del servicio de conflictos",
    description="Verifica que el servicio de verificación de conflictos está funcionando."
)
def estado_servicio():
    """
    Retorna el estado del servicio de verificación.
    
    Útil para health checks y monitoreo.
    """
    return {
        "servicio": "Verificación de Conflictos de Interés",
        "estado": "activo",
        "version": "1.0.0",
        "descripcion": "Sistema de verificación de conflictos para bufetes de abogados de Puerto Rico"