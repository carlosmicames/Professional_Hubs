"""
Endpoints para Asuntos (Matters/Cases).
Multi-tenant: Todos los endpoints filtran por firma_id del header.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_firm_id
from app.crud import crud_asunto
from app.models.asunto import EstadoAsunto
from app.schemas.asunto import AsuntoCreate, AsuntoUpdate, AsuntoResponse

router = APIRouter(
    prefix="/asuntos",
    tags=["Asuntos"],
    responses={404: {"description": "Asunto no encontrado"}}
)


@router.post(
    "/",
    response_model=AsuntoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo asunto"
)
def crear_asunto(
    asunto_in: AsuntoCreate,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    if not crud_asunto.verificar_pertenencia_firma(db, asunto_in.cliente_id, firm_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    return crud_asunto.create(db=db, obj_in=asunto_in)


@router.get(
    "/",
    response_model=List[AsuntoResponse],
    summary="Listar asuntos del bufete"
)
def listar_asuntos(
    skip: int = 0,
    limit: int = 100,
    estado: Optional[EstadoAsunto] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    return crud_asunto.get_multi_por_firma(
        db=db, firm_id=firm_id, skip=skip, limit=limit, estado=estado
    )


@router.get(
    "/{asunto_id}",
    response_model=AsuntoResponse,
    summary="Obtener un asunto"
)
def obtener_asunto(
    asunto_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    asunto = crud_asunto.get_por_firma(db=db, id=asunto_id, firm_id=firm_id)
    if asunto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asunto no encontrado"
        )
    return asunto


@router.put(
    "/{asunto_id}",
    response_model=AsuntoResponse,
    summary="Actualizar un asunto"
)
def actualizar_asunto(
    asunto_id: int,
    asunto_in: AsuntoUpdate,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    asunto = crud_asunto.get_por_firma(db=db, id=asunto_id, firm_id=firm_id)
    if asunto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asunto no encontrado"
        )
    return crud_asunto.update(db=db, db_obj=asunto, obj_in=asunto_in)


@router.delete(
    "/{asunto_id}",
    response_model=AsuntoResponse,
    summary="Eliminar un asunto (soft delete)"
)
def eliminar_asunto(
    asunto_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    asunto = crud_asunto.get_por_firma(db=db, id=asunto_id, firm_id=firm_id)
    if asunto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asunto no encontrado"
        )
    asunto.esta_activo = False
    db.commit()
    db.refresh(asunto)
    return asunto


@router.post(
    "/{asunto_id}/restaurar",
    response_model=AsuntoResponse,
    summary="Restaurar un asunto eliminado"
)
def restaurar_asunto(
    asunto_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    asunto = crud_asunto.get_por_firma(db=db, id=asunto_id, firm_id=firm_id, include_inactive=True)
    if asunto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asunto no encontrado"
        )
    asunto.esta_activo = True
    db.commit()
    db.refresh(asunto)
    return asunto


@router.get(
    "/cliente/{cliente_id}",
    response_model=List[AsuntoResponse],
    summary="Listar asuntos de un cliente"
)
def listar_asuntos_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    if not crud_asunto.verificar_pertenencia_firma(db, cliente_id, firm_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    return crud_asunto.get_por_cliente(db=db, cliente_id=cliente_id)