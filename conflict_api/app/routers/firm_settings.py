"""
Endpoints for Firm Settings (Profile, Studies, Practice Areas, Location, Plans).
All endpoints use upsert behavior for single-firm MVP (firm_id=1).
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.perfil import Perfil
from app.models.estudios import Estudios
from app.models.areas_practica import AreasPractica
from app.models.ubicacion import Ubicacion
from app.models.planes import Planes
from app.schemas.perfil import PerfilUpdate, PerfilResponse
from app.schemas.estudios import EstudiosUpdate, EstudiosResponse
from app.schemas.areas_practica import AreasPracticaUpdate, AreasPracticaResponse
from app.schemas.ubicacion import UbicacionUpdate, UbicacionResponse
from app.schemas.planes import PlanesUpdate, PlanesResponse, PlanSelectionResponse

# Default firm ID for MVP
DEFAULT_FIRM_ID = 1

router = APIRouter(tags=["Firm Settings"])


# ===========================================================================
# PERFIL (Profile)
# ===========================================================================

@router.get(
    "/perfil/{firma_id}",
    response_model=Optional[PerfilResponse],
    summary="Obtener perfil del bufete",
    description="Obtiene el perfil profesional del bufete. Returns null if not created yet."
)
def obtener_perfil(
    firma_id: int = DEFAULT_FIRM_ID,
    db: Session = Depends(get_db)
):
    """Get profile for firm. Returns None if not exists for upsert pattern."""
    perfil = db.query(Perfil).filter(Perfil.firma_id == firma_id).first()
    return perfil


@router.put(
    "/perfil/{firma_id}",
    response_model=PerfilResponse,
    summary="Actualizar/Crear perfil (upsert)",
    description="Actualiza el perfil existente o lo crea si no existe."
)
def actualizar_perfil(
    perfil_in: PerfilUpdate,
    firma_id: int = DEFAULT_FIRM_ID,
    db: Session = Depends(get_db)
):
    """Upsert profile: Update if exists, create if not."""
    perfil = db.query(Perfil).filter(Perfil.firma_id == firma_id).first()

    if perfil is None:
        # Create new profile
        perfil_data = perfil_in.model_dump(exclude_unset=True)
        perfil = Perfil(firma_id=firma_id, **perfil_data)
        db.add(perfil)
    else:
        # Update existing
        update_data = perfil_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(perfil, field, value)

    db.commit()
    db.refresh(perfil)
    return perfil


# ===========================================================================
# ESTUDIOS (Studies/Education)
# ===========================================================================

@router.get(
    "/estudios/{firma_id}",
    response_model=Optional[EstudiosResponse],
    summary="Obtener estudios del bufete",
    description="Obtiene la informacion educativa. Returns null if not created yet."
)
def obtener_estudios(
    firma_id: int = DEFAULT_FIRM_ID,
    db: Session = Depends(get_db)
):
    """Get studies for firm. Returns None if not exists."""
    estudios = db.query(Estudios).filter(Estudios.firma_id == firma_id).first()
    return estudios


@router.put(
    "/estudios/{firma_id}",
    response_model=EstudiosResponse,
    summary="Actualizar/Crear estudios (upsert)",
    description="Actualiza los estudios existentes o los crea si no existen."
)
def actualizar_estudios(
    estudios_in: EstudiosUpdate,
    firma_id: int = DEFAULT_FIRM_ID,
    db: Session = Depends(get_db)
):
    """Upsert studies: Update if exists, create if not."""
    estudios = db.query(Estudios).filter(Estudios.firma_id == firma_id).first()

    if estudios is None:
        estudios_data = estudios_in.model_dump(exclude_unset=True)
        estudios = Estudios(firma_id=firma_id, **estudios_data)
        db.add(estudios)
    else:
        update_data = estudios_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(estudios, field, value)

    db.commit()
    db.refresh(estudios)
    return estudios


# ===========================================================================
# AREAS DE PRACTICA (Practice Areas)
# ===========================================================================

@router.get(
    "/areas-practica/{firma_id}",
    response_model=Optional[AreasPracticaResponse],
    summary="Obtener areas de practica",
    description="Obtiene las areas de practica del bufete. Returns null if not created yet."
)
def obtener_areas_practica(
    firma_id: int = DEFAULT_FIRM_ID,
    db: Session = Depends(get_db)
):
    """Get practice areas for firm. Returns None if not exists."""
    areas = db.query(AreasPractica).filter(AreasPractica.firma_id == firma_id).first()
    return areas


@router.put(
    "/areas-practica/{firma_id}",
    response_model=AreasPracticaResponse,
    summary="Actualizar/Crear areas de practica (upsert)",
    description="Actualiza las areas de practica existentes o las crea si no existen."
)
def actualizar_areas_practica(
    areas_in: AreasPracticaUpdate,
    firma_id: int = DEFAULT_FIRM_ID,
    db: Session = Depends(get_db)
):
    """Upsert practice areas: Update if exists, create if not."""
    areas = db.query(AreasPractica).filter(AreasPractica.firma_id == firma_id).first()

    if areas is None:
        areas_data = areas_in.model_dump(exclude_unset=True)
        areas = AreasPractica(firma_id=firma_id, **areas_data)
        db.add(areas)
    else:
        update_data = areas_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(areas, field, value)

    db.commit()
    db.refresh(areas)
    return areas


# ===========================================================================
# UBICACION (Geographic Location)
# ===========================================================================

@router.get(
    "/ubicacion/{firma_id}",
    response_model=Optional[UbicacionResponse],
    summary="Obtener ubicacion geografica",
    description="Obtiene la ubicacion geografica del bufete. Returns null if not created yet."
)
def obtener_ubicacion(
    firma_id: int = DEFAULT_FIRM_ID,
    db: Session = Depends(get_db)
):
    """Get location for firm. Returns None if not exists."""
    ubicacion = db.query(Ubicacion).filter(Ubicacion.firma_id == firma_id).first()
    return ubicacion


@router.put(
    "/ubicacion/{firma_id}",
    response_model=UbicacionResponse,
    summary="Actualizar/Crear ubicacion (upsert)",
    description="Actualiza la ubicacion existente o la crea si no existe."
)
def actualizar_ubicacion(
    ubicacion_in: UbicacionUpdate,
    firma_id: int = DEFAULT_FIRM_ID,
    db: Session = Depends(get_db)
):
    """Upsert location: Update if exists, create if not."""
    ubicacion = db.query(Ubicacion).filter(Ubicacion.firma_id == firma_id).first()

    if ubicacion is None:
        ubicacion_data = ubicacion_in.model_dump(exclude_unset=True)
        ubicacion = Ubicacion(firma_id=firma_id, **ubicacion_data)
        db.add(ubicacion)
    else:
        update_data = ubicacion_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ubicacion, field, value)

    db.commit()
    db.refresh(ubicacion)
    return ubicacion


# ===========================================================================
# PLANES (Subscription Plans)
# ===========================================================================

@router.get(
    "/planes/{firma_id}",
    response_model=Optional[PlanesResponse],
    summary="Obtener plan del bufete",
    description="Obtiene el plan de suscripcion del bufete. Returns null if not created yet."
)
def obtener_planes(
    firma_id: int = DEFAULT_FIRM_ID,
    db: Session = Depends(get_db)
):
    """Get subscription plan for firm. Returns None if not exists."""
    planes = db.query(Planes).filter(Planes.firma_id == firma_id).first()
    return planes


@router.put(
    "/planes/{firma_id}",
    response_model=PlanSelectionResponse,
    summary="Seleccionar/Actualizar plan (upsert)",
    description="Selecciona o actualiza el plan de suscripcion. Basico = 14 dias trial."
)
def actualizar_planes(
    planes_in: PlanesUpdate,
    firma_id: int = DEFAULT_FIRM_ID,
    db: Session = Depends(get_db)
):
    """Upsert plan selection: Update if exists, create if not."""
    planes = db.query(Planes).filter(Planes.firma_id == firma_id).first()

    # If Basico plan selected, set trial_days to 14
    if planes_in.selected_plan == "Basico":
        planes_in.trial_days = 14

    if planes is None:
        planes_data = planes_in.model_dump(exclude_unset=True)
        planes = Planes(firma_id=firma_id, **planes_data)
        db.add(planes)
    else:
        update_data = planes_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(planes, field, value)

    db.commit()
    db.refresh(planes)

    return PlanSelectionResponse(
        success=True,
        message="Plan seleccionado. Integracion de pagos proximamente.",
        plan=planes
    )
