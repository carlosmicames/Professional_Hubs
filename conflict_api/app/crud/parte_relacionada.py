"""
CRUD para Parte Relacionada (Related Party).
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.parte_relacionada import ParteRelacionada
from app.models.asunto import Asunto
from app.models.cliente import Cliente
from app.schemas.parte_relacionada import ParteRelacionadaCreate, ParteRelacionadaUpdate


class CRUDParteRelacionada(CRUDBase[ParteRelacionada, ParteRelacionadaCreate, ParteRelacionadaUpdate]):
    """
    CRUD para operaciones de Parte Relacionada.
    Filtra por firma a través del asunto y cliente.
    """
    
    def get_por_firma(
        self, 
        db: Session, 
        id: int, 
        firm_id: int,
        include_inactive: bool = False
    ) -> Optional[ParteRelacionada]:
        """
        Obtiene una parte relacionada verificando pertenencia al bufete.
        
        Args:
            db: Sesión de base de datos
            id: ID de la parte relacionada
            firm_id: ID del bufete
            include_inactive: Incluir partes inactivas
        """
        query = (
            db.query(ParteRelacionada)
            .join(Asunto)
            .join(Cliente)
            .filter(
                ParteRelacionada.id == id,
                Cliente.firma_id == firm_id
            )
        )
        
        if not include_inactive:
            query = query.filter(ParteRelacionada.esta_activo == True)
        
        return query.first()
    
    def get_multi_por_firma(
        self,
        db: Session,
        firm_id: int,
        skip: int = 0,
        limit: int = 100,
        tipo_relacion: Optional[str] = None,
        include_inactive: bool = False
    ) -> List[ParteRelacionada]:
        """
        Obtiene partes relacionadas del bufete con paginación.
        
        Args:
            db: Sesión de base de datos
            firm_id: ID del bufete
            skip: Registros a saltar
            limit: Límite de registros
            tipo_relacion: Filtrar por tipo de relación
            include_inactive: Incluir partes inactivas
        """
        query = (
            db.query(ParteRelacionada)
            .join(Asunto)
            .join(Cliente)
            .filter(Cliente.firma_id == firm_id)
            .options(
                joinedload(ParteRelacionada.asunto).joinedload(Asunto.cliente)
            )
        )
        
        if not include_inactive:
            query = query.filter(ParteRelacionada.esta_activo == True)
        
        if tipo_relacion:
            query = query.filter(ParteRelacionada.tipo_relacion == tipo_relacion)
        
        return query.offset(skip).limit(limit).all()
    
    def get_por_asunto(
        self, 
        db: Session, 
        asunto_id: int,
        include_inactive: bool = False
    ) -> List[ParteRelacionada]:
        """
        Obtiene todas las partes relacionadas de un asunto.
        
        Args:
            db: Sesión de base de datos
            asunto_id: ID del asunto
            include_inactive: Incluir partes inactivas
        """
        query = db.query(ParteRelacionada).filter(ParteRelacionada.asunto_id == asunto_id)
        
        if not include_inactive:
            query = query.filter(ParteRelacionada.esta_activo == True)
        
        return query.all()
    
    def verificar_pertenencia_firma(
        self, 
        db: Session, 
        asunto_id: int, 
        firm_id: int
    ) -> bool:
        """
        Verifica que el asunto pertenece al bufete.
        
        Args:
            db: Sesión de base de datos
            asunto_id: ID del asunto
            firm_id: ID del bufete
        """
        asunto = (
            db.query(Asunto)
            .join(Cliente)
            .filter(
                Asunto.id == asunto_id,
                Cliente.firma_id == firm_id,
                Asunto.esta_activo == True
            )
            .first()
        )
        return asunto is not None


crud_parte_relacionada = CRUDParteRelacionada(ParteRelacionada)