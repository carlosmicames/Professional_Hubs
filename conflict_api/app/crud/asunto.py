"""
CRUD para Asunto (Matter).
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.asunto import Asunto, EstadoAsunto
from app.models.cliente import Cliente
from app.schemas.asunto import AsuntoCreate, AsuntoUpdate


class CRUDAsunto(CRUDBase[Asunto, AsuntoCreate, AsuntoUpdate]):
    """
    CRUD para operaciones de Asunto.
    Filtra por firma a través del cliente.
    """
    
    def get_por_firma(
        self, 
        db: Session, 
        id: int, 
        firm_id: int,
        include_inactive: bool = False
    ) -> Optional[Asunto]:
        """
        Obtiene un asunto verificando pertenencia al bufete.
        
        Args:
            db: Sesión de base de datos
            id: ID del asunto
            firm_id: ID del bufete
            include_inactive: Incluir asuntos inactivos
        """
        query = (
            db.query(Asunto)
            .join(Cliente)
            .filter(
                Asunto.id == id,
                Cliente.firma_id == firm_id
            )
        )
        
        if not include_inactive:
            query = query.filter(Asunto.esta_activo == True)
        
        return query.first()
    
    def get_multi_por_firma(
        self, 
        db: Session, 
        firm_id: int,
        skip: int = 0, 
        limit: int = 100,
        estado: Optional[EstadoAsunto] = None,
        include_inactive: bool = False
    ) -> List[Asunto]:
        """
        Obtiene asuntos del bufete con paginación.
        
        Args:
            db: Sesión de base de datos
            firm_id: ID del bufete
            skip: Registros a saltar
            limit: Límite de registros
            estado: Filtrar por estado
            include_inactive: Incluir asuntos inactivos
        """
        query = (
            db.query(Asunto)
            .join(Cliente)
            .filter(Cliente.firma_id == firm_id)
            .options(joinedload(Asunto.cliente))
        )
        
        if not include_inactive:
            query = query.filter(Asunto.esta_activo == True)
        
        if estado:
            query = query.filter(Asunto.estado == estado)
        
        return query.offset(skip).limit(limit).all()
    
    def get_por_cliente(
        self, 
        db: Session, 
        cliente_id: int,
        include_inactive: bool = False
    ) -> List[Asunto]:
        """
        Obtiene todos los asuntos de un cliente.
        
        Args:
            db: Sesión de base de datos
            cliente_id: ID del cliente
            include_inactive: Incluir asuntos inactivos
        """
        query = db.query(Asunto).filter(Asunto.cliente_id == cliente_id)
        
        if not include_inactive:
            query = query.filter(Asunto.esta_activo == True)
        
        return query.all()
    
    def verificar_pertenencia_firma(
        self, 
        db: Session, 
        cliente_id: int, 
        firm_id: int
    ) -> bool:
        """
        Verifica que el cliente pertenece al bufete.
        
        Args:
            db: Sesión de base de datos
            cliente_id: ID del cliente
            firm_id: ID del bufete
        """
        cliente = (
            db.query(Cliente)
            .filter(
                Cliente.id == cliente_id,
                Cliente.firma_id == firm_id,
                Cliente.esta_activo == True
            )
            .first()
        )
        return cliente is not None


crud_asunto = CRUDAsunto(Asunto)