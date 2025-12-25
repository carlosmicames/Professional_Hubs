"""
Endpoints para Verificación de Conflictos de Interés.
Incluye búsqueda exacta y difusa con niveles de confianza.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_firm_id
from app.schemas.conflicto import BusquedaConflicto, ResultadoConflicto
from app.services.conflict_checker import conflict_checker
from app.config import get_settings

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
    
    ## Tipos de búsqueda
    
    - **Coincidencia exacta**: Insensible a mayúsculas y acentos comunes
      - José = jose = JOSÉ
      - María = maria = Maria
      - González = gonzalez
      - NOTA: ñ NO se normaliza (Muñoz ≠ Munoz)
    
    - **Coincidencia difusa**: Usando algoritmo de similitud (>70%)
      - Detecta errores tipográficos
      - Nombres similares
    
    ## Ámbito de búsqueda
    
    - Clientes existentes (personas y empresas)
    - Partes relacionadas en TODOS los asuntos (activos y cerrados)
    
    ## Niveles de confianza
    
    - **Alta**: 90-100% de similitud
    - **Media**: 70-89% de similitud
    
    ## Segundo apellido
    
    Si se proporciona segundo_apellido, se requiere que coincida para obtener match exacto.
    """
)
def verificar_conflictos(
    busqueda: BusquedaConflicto,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Verifica conflictos de interés para un cliente potencial.
    
    **Para persona natural:**
    - nombre (requerido o apellido)
    - apellido (requerido o nombre)
    - segundo_apellido (opcional)
    
    **Para empresa:**
    - nombre_empresa
    
    Retorna lista de conflictos ordenados por confianza (mayor a menor).
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
    """
    settings = get_settings()
    return {
        "servicio": "Verificación de Conflictos de Interés",
        "estado": "activo",
        "version": settings.api_version,
        "configuracion": {
            "umbral_similitud": settings.fuzzy_threshold,
            "umbral_confianza_alta": settings.fuzzy_high_confidence
        },
        "descripcion": "Sistema de verificación de conflictos para bufetes de abogados de Puerto Rico"
    }