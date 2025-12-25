"""
Endpoints para Firmas (Bufetes).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud import crud_firma
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
    """
    Crea una nueva firma (bufete).
    
    - **nombre**: Nombre del bufete (requerido)
    """
    return crud_firma.create(db=db, obj_in=firma_in)


@router.get(
    "/",
    response_model=List[FirmaResponse],
    summary="Listar todas las firmas",
    description="Obtiene lista de todas las firmas activas con paginación."
)
def listar_firmas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lista todas las firmas activas.
    
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Límite de registros a retornar
    """
    return crud_firma.get_multi(db=db, skip=skip, limit=limit)


@router.get(
    "/{firma_id}",
    response_model=FirmaResponse,
    summary="Obtener una firma",
    description="Obtiene los detalles de una firma específica."
)
def obtener_firma(
    firma_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una firma por su ID.
    
    - **firma_id**: ID de la firma
    """
    firma = crud_firma.get(db=db, id=firma_id)
    if firma is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Firma no encontrada"
        )
    return firma


@router.put(
    "/{firma_id}",
    response_model=FirmaResponse,
    summary="Actualizar una firma",
    description="Actualiza los datos de una firma existente."
)
def actualizar_firma(
    firma_id: int,
    firma_in: FirmaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza una firma existente.
    
    - **firma_id**: ID de la firma a actualizar
    - **nombre**: Nuevo nombre (opcional)
    """
    firma = crud_firma.get(db=db, id=firma_id)
    if firma is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Firma no encontrada"
        )
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
    """
    Elimina una firma (soft delete).
    
    - **firma_id**: ID de la firma a eliminar
    """
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
    """
    Restaura una firma eliminada.
    
    - **firma_id**: ID de la firma a restaurar
    """
    firma = crud_firma.restore(db=db, id=firma_id)
    if firma is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Firma no encontrada"
        )
    return firma