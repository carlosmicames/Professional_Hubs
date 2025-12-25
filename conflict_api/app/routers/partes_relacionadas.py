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
from app.models.parte_relacionada import TipoRelacion
from app.schemas.parte_relacionada import (
    ParteRelacionadaCreate, 
    ParteRelacionadaUpdate, 
    ParteRelacionadaResponse
)

router = APIRouter(
    prefix="/partes-relacionadas",
    tags=["Partes Relacionadas"],
    responses={404: {"description": "Parte relacionada no encontrada"}}
)


@router.post(
    "/",
    response_model=ParteRelacionadaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una parte relacionada",
    description="Crea una nueva parte relacionada a un asunto. Requiere header X-Firm-ID."
)
def crear_parte_relacionada(
    parte_in: ParteRelacionadaCreate,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Crea una nueva parte relacionada.
    
    - **asunto_id**: ID del asunto (debe pertenecer al bufete)
    - **nombre**: Nombre de la parte
    - **tipo_relacion**: Tipo de relación (demandante, demandado, parte_contraria, etc.)
    """
    # Verificar que el asunto pertenece al bufete
    if not crud_parte_relacionada.verificar_pertenencia_firma(db, parte_in.asunto_id, firm_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asunto no encontrado"
        )
    
    return crud_parte_relacionada.create(db=db, obj_in=parte_in)


@router.get(
    "/",
    response_model=List[ParteRelacionadaResponse],
    summary="Listar partes relacionadas del bufete",
    description="Obtiene lista de partes relacionadas con paginación y filtros."
)
def listar_partes_relacionadas(
    skip: int = 0,
    limit: int = 100,
    tipo_relacion: Optional[TipoRelacion] = Query(None, description="Filtrar por tipo de relación"),
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Lista todas las partes relacionadas del bufete.
    
    - **skip**: Número de registros a saltar
    - **limit**: Límite de registros a retornar
    - **tipo_relacion**: Filtrar por tipo de relación
    """
    return crud_parte_relacionada.get_multi_por_firma(
        db=db, 
        firm_id=firm_id, 
        skip=skip, 
        limit=limit,
        tipo_relacion=tipo_relacion
    )


@router.get(
    "/{parte_id}",
    response_model=ParteRelacionadaResponse,
    summary="Obtener una parte relacionada",
    description="Obtiene los detalles de una parte relacionada específica."
)
def obtener_parte_relacionada(
    parte_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Obtiene una parte relacionada por su ID.
    
    - **parte_id**: ID de la parte relacionada
    """
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
    summary="Actualizar una parte relacionada",
    description="Actualiza los datos de una parte relacionada existente."
)
def actualizar_parte_relacionada(
    parte_id: int,
    parte_in: ParteRelacionadaUpdate,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Actualiza una parte relacionada existente.
    
    - **parte_id**: ID de la parte a actualizar
    - **nombre**: Nuevo nombre (opcional)
    - **tipo_relacion**: Nuevo tipo de relación (opcional)
    """
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
    summary="Eliminar una parte relacionada",
    description="Elimina una parte relacionada (soft delete)."
)
def eliminar_parte_relacionada(
    parte_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Elimina una parte relacionada (soft delete).
    
    - **parte_id**: ID de la parte a eliminar
    """
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
    summary="Restaurar una parte relacionada",
    description="Restaura una parte relacionada eliminada."
)
def restaurar_parte_relacionada(
    parte_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Restaura una parte relacionada eliminada.
    
    - **parte_id**: ID de la parte a restaurar
    """
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
    summary="Listar partes de un asunto",
    description="Obtiene todas las partes relacionadas de un asunto específico."
)
def listar_partes_por_asunto(
    asunto_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Lista todas las partes relacionadas de un asunto.
    
    - **asunto_id**: ID del asunto
    """
    # Verificar que el asunto pertenece al bufete
    if not crud_parte_relacionada.verificar_pertenencia_firma(db, asunto_id, firm_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asunto no encontrado"
        )
    
    return crud_parte_relacionada.get_por_asunto(db=db, asunto_id=asunto_id)


@router.get(
    "/tipos/",
    response_model=List[str],
    summary="Listar tipos de relación",
    description="Obtiene lista de todos los tipos de relación disponibles."
)
def listar_tipos_relacion():
    """
    Lista todos los tipos de relación disponibles.
    
    Tipos disponibles:
    - demandante
    - demandado
    - parte_contraria
    - co_demandado
    - conyuge
    - subsidiaria
    - empresa_matriz
    """
    return [tipo.value for tipo in TipoRelacion]