"""
Endpoints para Clientes.
Multi-tenant: Todos los endpoints filtran por firma_id del header.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_firm_id
from app.crud import crud_cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    responses={404: {"description": "Cliente no encontrado"}}
)


@router.post(
    "/",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo cliente",
    description="Crea un nuevo cliente para el bufete. Requiere header X-Firm-ID."
)
def crear_cliente(
    cliente_in: ClienteCreate,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Crea un nuevo cliente.
    
    Para persona natural:
    - **nombre**: Nombre del cliente
    - **apellido**: Apellido del cliente
    
    Para empresa:
    - **nombre_empresa**: Nombre de la empresa/corporación
    """
    return crud_cliente.create(db=db, obj_in=cliente_in, firm_id=firm_id)


@router.get(
    "/",
    response_model=List[ClienteResponse],
    summary="Listar clientes del bufete",
    description="Obtiene lista de clientes activos del bufete con paginación."
)
def listar_clientes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Lista todos los clientes activos del bufete.
    
    - **skip**: Número de registros a saltar
    - **limit**: Límite de registros a retornar
    """
    return crud_cliente.get_multi(db=db, firm_id=firm_id, skip=skip, limit=limit)


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Obtener un cliente",
    description="Obtiene los detalles de un cliente específico."
)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Obtiene un cliente por su ID.
    
    - **cliente_id**: ID del cliente
    """
    cliente = crud_cliente.get(db=db, id=cliente_id, firm_id=firm_id)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    return cliente


@router.put(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Actualizar un cliente",
    description="Actualiza los datos de un cliente existente."
)
def actualizar_cliente(
    cliente_id: int,
    cliente_in: ClienteUpdate,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Actualiza un cliente existente.
    
    - **cliente_id**: ID del cliente a actualizar
    """
    cliente = crud_cliente.get(db=db, id=cliente_id, firm_id=firm_id)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    return crud_cliente.update(db=db, db_obj=cliente, obj_in=cliente_in)


@router.delete(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Eliminar un cliente",
    description="Elimina un cliente (soft delete - marca como inactivo)."
)
def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Elimina un cliente (soft delete).
    
    - **cliente_id**: ID del cliente a eliminar
    """
    cliente = crud_cliente.delete(db=db, id=cliente_id, firm_id=firm_id)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    return cliente


@router.post(
    "/{cliente_id}/restaurar",
    response_model=ClienteResponse,
    summary="Restaurar un cliente",
    description="Restaura un cliente previamente eliminado."
)
def restaurar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Restaura un cliente eliminado.
    
    - **cliente_id**: ID del cliente a restaurar
    """
    cliente = crud_cliente.restore(db=db, id=cliente_id, firm_id=firm_id)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    return cliente


@router.get(
    "/buscar/",
    response_model=List[ClienteResponse],
    summary="Buscar clientes por nombre",
    description="Busca clientes por nombre, apellido o nombre de empresa."
)
def buscar_clientes(
    nombre: str = None,
    apellido: str = None,
    nombre_empresa: str = None,
    db: Session = Depends(get_db),
    firm_id: int = Depends(get_firm_id)
):
    """
    Busca clientes por nombre.
    
    - **nombre**: Nombre a buscar
    - **apellido**: Apellido a buscar
    - **nombre_empresa**: Nombre de empresa a buscar
    """
    if not any([nombre, apellido, nombre_empresa]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un criterio de búsqueda"
        )
    
    return crud_cliente.buscar_por_nombre(
        db=db,
        firm_id=firm_id,
        nombre=nombre,
        apellido=apellido,
        nombre_empresa=nombre_empresa
    )