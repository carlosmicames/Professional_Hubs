"""
Endpoints para Partes Relacionadas (Related Parties).
Multi-tenant: Todos los endpoints filtran por firma_id del header.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_firm_id
from app.crud import crud_parte_relacionada
from app.schemas.parte_relacionada import (
    ParteRelacionadaCreate,
    ParteRelacionadaUpdate,
    ParteRelacionadaResponse
)

# Valid tipo_relacion values
TIPOS_RELACION = [
    "DEMANDANTE", "DEMANDADO", "PARTE_CONTRARIA",
    "CO_DEMANDADO", "CONYUGE", "SUBSIDIARIA", "EMPRESA_MATRIZ"
]

router = APIRouter(
    prefix="/partes-relacionadas",
    tags=["Partes Relacionadas"],
    responses={404: {"description": "Parte relacionada no encontrada"}}
)


@router.post(
    "/",
    response_model=ParteRelacionadaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una parte relacionada"
)
def crear_parte_relacionada(
    parte_in: ParteRelacionadaCreate,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    if not crud_parte_relacionada.verificar_pertenencia_firma(db, parte_in.asunto_id, firm_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asunto no encontrado"
        )
    return crud_parte_relacionada.create(db=db, obj_in=parte_in)


@router.get(
    "/",
    response_model=List[ParteRelacionadaResponse],
    summary="Listar partes relacionadas del bufete"
)
def listar_partes_relacionadas(
    skip: int = 0,
    limit: int = 100,
    tipo_relacion: Optional[str] = Query(None, description="Filtrar por tipo de relacion"),
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    return crud_parte_relacionada.get_multi_por_firma(
        db=db, firm_id=firm_id, skip=skip, limit=limit, tipo_relacion=tipo_relacion
    )


@router.get(
    "/{parte_id}",
    response_model=ParteRelacionadaResponse,
    summary="Obtener una parte relacionada"
)
def obtener_parte_relacionada(
    parte_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    parte = crud_parte_relacionada.get_por_firma(db=db, id=parte_id, firm_id=firm_id)
    if parte is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parte relacionada no encontrada"
        )
    return parte


@router.put(
    "/{parte_id}",
    response_model=ParteRelacionadaResponse,
    summary="Actualizar una parte relacionada"
)
def actualizar_parte_relacionada(
    parte_id: int,
    parte_in: ParteRelacionadaUpdate,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    parte = crud_parte_relacionada.get_por_firma(db=db, id=parte_id, firm_id=firm_id)
    if parte is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parte relacionada no encontrada"
        )
    return crud_parte_relacionada.update(db=db, db_obj=parte, obj_in=parte_in)


@router.delete(
    "/{parte_id}",
    response_model=ParteRelacionadaResponse,
    summary="Eliminar una parte relacionada (soft delete)"
)
def eliminar_parte_relacionada(
    parte_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    parte = crud_parte_relacionada.get_por_firma(db=db, id=parte_id, firm_id=firm_id)
    if parte is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parte relacionada no encontrada"
        )
    parte.esta_activo = False
    db.commit()
    db.refresh(parte)
    return parte


@router.post(
    "/{parte_id}/restaurar",
    response_model=ParteRelacionadaResponse,
    summary="Restaurar una parte relacionada"
)
def restaurar_parte_relacionada(
    parte_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    parte = crud_parte_relacionada.get_por_firma(
        db=db, id=parte_id, firm_id=firm_id, include_inactive=True
    )
    if parte is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parte relacionada no encontrada"
        )
    parte.esta_activo = True
    db.commit()
    db.refresh(parte)
    return parte


@router.get(
    "/asunto/{asunto_id}",
    response_model=List[ParteRelacionadaResponse],
    summary="Listar partes de un asunto"
)
def listar_partes_por_asunto(
    asunto_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    if not crud_parte_relacionada.verificar_pertenencia_firma(db, asunto_id, firm_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asunto no encontrado"
        )
    return crud_parte_relacionada.get_por_asunto(db=db, asunto_id=asunto_id)


@router.get(
    "/tipos/",
    response_model=List[str],
    summary="Listar tipos de relacion disponibles"
)
def listar_tipos_relacion():
    return TIPOS_RELACION