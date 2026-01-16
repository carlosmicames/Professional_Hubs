"""
Endpoints para Firmas (Bufetes).
Updated with upsert behavior for single-firm MVP.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud import crud_firma
from app.models.firma import Firma
from app.schemas.firma import FirmaCreate, FirmaUpdate, FirmaResponse

router = APIRouter(
    prefix="/firmas",
    tags=["Firmas"],
    responses={404: {"description": "Firma no encontrada"}}
)


@router.post(
    "/",
    response_model=FirmaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva firma",
    description="Crea un nuevo bufete de abogados en el sistema."
)
def crear_firma(
    firma_in: FirmaCreate,
    db: Session = Depends(get_db)
):
    """Crea una nueva firma (bufete)."""
    return crud_firma.create(db=db, obj_in=firma_in)


@router.get(
    "/",
    response_model=List[FirmaResponse],
    summary="Listar todas las firmas",
    description="Obtiene lista de todas las firmas activas con paginacion."
)
def listar_firmas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todas las firmas activas."""
    return crud_firma.get_multi(db=db, skip=skip, limit=limit)


@router.get(
    "/{firma_id}",
    response_model=Optional[FirmaResponse],
    summary="Obtener una firma",
    description="Obtiene los detalles de una firma especifica. Returns null if not found for upsert pattern."
)
def obtener_firma(
    firma_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una firma por su ID.
    For single-firm MVP: Returns None if firm_id=1 doesn't exist yet.
    """
    firma = crud_firma.get(db=db, id=firma_id)
    if firma is None:
        # For MVP upsert pattern - return None for firm_id=1
        if firma_id == 1:
            return None
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Firma no encontrada"
        )
    return firma


@router.put(
    "/{firma_id}",
    response_model=FirmaResponse,
    summary="Actualizar/Crear una firma (upsert)",
    description="Actualiza una firma existente o la crea si no existe (upsert behavior para MVP)."
)
def actualizar_firma(
    firma_id: int,
    firma_in: FirmaUpdate,
    db: Session = Depends(get_db)
):
    """Upsert firma: Update if exists, create if not (for single-firm MVP)."""
    firma = crud_firma.get(db=db, id=firma_id, include_inactive=True)

    if firma is None:
        # Create new firm with specified ID (for MVP single-firm pattern)
        firma_data = firma_in.model_dump(exclude_unset=True)
        new_firma = Firma(id=firma_id, **firma_data)
        db.add(new_firma)
        db.commit()
        db.refresh(new_firma)
        return new_firma

    # Update existing
    return crud_firma.update(db=db, db_obj=firma, obj_in=firma_in)


@router.delete(
    "/{firma_id}",
    response_model=FirmaResponse,
    summary="Eliminar una firma",
    description="Elimina una firma (soft delete - marca como inactiva)."
)
def eliminar_firma(
    firma_id: int,
    db: Session = Depends(get_db)
):
    """Elimina una firma (soft delete)."""
    firma = crud_firma.delete(db=db, id=firma_id)
    if firma is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Firma no encontrada"
        )
    return firma


@router.post(
    "/{firma_id}/restaurar",
    response_model=FirmaResponse,
    summary="Restaurar una firma",
    description="Restaura una firma previamente eliminada."
)
def restaurar_firma(
    firma_id: int,
    db: Session = Depends(get_db)
):
    """Restaura una firma eliminada."""
    firma = crud_firma.restore(db=db, id=firma_id)
    if firma is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Firma no encontrada"
        )
    return firma
