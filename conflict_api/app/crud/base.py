"""
Clase base CRUD con aislamiento multi-tenant.
"""

from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel
from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Clase base CRUD genérica con operaciones estándar.
    Incluye soft delete y aislamiento por firma cuando aplica.
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Inicializa el CRUD con el modelo especificado.
        
        Args:
            model: Clase del modelo SQLAlchemy
        """
        self.model = model
    
    def get(
        self, 
        db: Session, 
        id: int, 
        firm_id: Optional[int] = None,
        include_inactive: bool = False
    ) -> Optional[ModelType]:
        """
        Obtiene un registro por ID.
        
        Args:
            db: Sesión de base de datos
            id: ID del registro
            firm_id: ID de firma para filtrar (si aplica)
            include_inactive: Incluir registros inactivos
        """
        query = db.query(self.model).filter(self.model.id == id)
        
        # Filtrar por firma si el modelo tiene firma_id
        if firm_id is not None and hasattr(self.model, 'firma_id'):
            query = query.filter(self.model.firma_id == firm_id)
        
        # Filtrar inactivos por defecto
        if not include_inactive and hasattr(self.model, 'esta_activo'):
            query = query.filter(self.model.esta_activo == True)
        
        return query.first()
    
    def get_multi(
        self, 
        db: Session, 
        firm_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100,
        include_inactive: bool = False
    ) -> List[ModelType]:
        """
        Obtiene múltiples registros con paginación.
        
        Args:
            db: Sesión de base de datos
            firm_id: ID de firma para filtrar (si aplica)
            skip: Registros a saltar
            limit: Límite de registros
            include_inactive: Incluir registros inactivos
        """
        query = db.query(self.model)
        
        # Filtrar por firma si el modelo tiene firma_id
        if firm_id is not None and hasattr(self.model, 'firma_id'):
            query = query.filter(self.model.firma_id == firm_id)
        
        # Filtrar inactivos por defecto
        if not include_inactive and hasattr(self.model, 'esta_activo'):
            query = query.filter(self.model.esta_activo == True)
        
        return query.offset(skip).limit(limit).all()
    
    def create(
        self, 
        db: Session, 
        obj_in: CreateSchemaType,
        firm_id: Optional[int] = None
    ) -> ModelType:
        """
        Crea un nuevo registro.
        
        Args:
            db: Sesión de base de datos
            obj_in: Schema con datos de creación
            firm_id: ID de firma para asignar (si aplica)
        """
        obj_data = obj_in.model_dump()
        
        # Agregar firma_id si el modelo lo requiere
        if firm_id is not None and hasattr(self.model, 'firma_id'):
            obj_data['firma_id'] = firm_id
        
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, 
        db: Session, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """
        Actualiza un registro existente.
        
        Args:
            db: Sesión de base de datos
            db_obj: Objeto a actualizar
            obj_in: Schema con datos de actualización
        """
        obj_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(
        self, 
        db: Session, 
        id: int,
        firm_id: Optional[int] = None,
        hard_delete: bool = False
    ) -> Optional[ModelType]:
        """
        Elimina un registro (soft delete por defecto).
        
        Args:
            db: Sesión de base de datos
            id: ID del registro
            firm_id: ID de firma para verificar pertenencia
            hard_delete: Si True, elimina permanentemente
        """
        obj = self.get(db, id=id, firm_id=firm_id, include_inactive=True)
        
        if obj is None:
            return None
        
        if hard_delete:
            db.delete(obj)
        else:
            if hasattr(obj, 'esta_activo'):
                obj.esta_activo = False
                db.add(obj)
        
        db.commit()
        return obj
    
    def restore(
        self, 
        db: Session, 
        id: int,
        firm_id: Optional[int] = None
    ) -> Optional[ModelType]:
        """
        Restaura un registro eliminado (soft delete).
        
        Args:
            db: Sesión de base de datos
            id: ID del registro
            firm_id: ID de firma para verificar pertenencia
        """
        obj = self.get(db, id=id, firm_id=firm_id, include_inactive=True)
        
        if obj is None:
            return None
        
        if hasattr(obj, 'esta_activo'):
            obj.esta_activo = True
            db.add(obj)
            db.commit()
            db.refresh(obj)
        
        return obj