"""
CRUD para Cliente.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.crud.base import CRUDBase
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate


class CRUDCliente(CRUDBase[Cliente, ClienteCreate, ClienteUpdate]):
    """
    CRUD para operaciones de Cliente.
    Incluye métodos de búsqueda para verificación de conflictos.
    """
    
    def buscar_por_nombre(
        self, 
        db: Session, 
        firm_id: int,
        nombre: Optional[str] = None,
        apellido: Optional[str] = None,
        nombre_empresa: Optional[str] = None,
        include_inactive: bool = False
    ) -> List[Cliente]:
        """
        Busca clientes por nombre exacto.
        Usado para verificación de conflictos.
        
        Args:
            db: Sesión de base de datos
            firm_id: ID del bufete
            nombre: Nombre a buscar
            apellido: Apellido a buscar
            nombre_empresa: Nombre de empresa a buscar
            include_inactive: Incluir clientes inactivos
        
        Returns:
            Lista de clientes que coinciden
        """
        query = db.query(Cliente).filter(Cliente.firma_id == firm_id)
        
        if not include_inactive:
            query = query.filter(Cliente.esta_activo == True)
        
        condiciones = []
        
        # Búsqueda por nombre y apellido (exacta, case-insensitive)
        if nombre and apellido:
            condiciones.append(
                and_(
                    func.lower(Cliente.nombre) == func.lower(nombre),
                    func.lower(Cliente.apellido) == func.lower(apellido)
                )
            )
        elif nombre:
            condiciones.append(func.lower(Cliente.nombre) == func.lower(nombre))
        elif apellido:
            condiciones.append(func.lower(Cliente.apellido) == func.lower(apellido))
        
        # Búsqueda por nombre de empresa (exacta, case-insensitive)
        if nombre_empresa:
            condiciones.append(
                func.lower(Cliente.nombre_empresa) == func.lower(nombre_empresa)
            )
        
        if condiciones:
            query = query.filter(or_(*condiciones))
        else:
            return []
        
        return query.all()
    
    def existe_cliente(
        self, 
        db: Session, 
        firm_id: int,
        nombre: Optional[str] = None,
        apellido: Optional[str] = None,
        nombre_empresa: Optional[str] = None
    ) -> bool:
        """
        Verifica si existe un cliente con el nombre dado.
        
        Args:
            db: Sesión de base de datos
            firm_id: ID del bufete
            nombre: Nombre a verificar
            apellido: Apellido a verificar
            nombre_empresa: Nombre de empresa a verificar
        
        Returns:
            True si existe, False si no
        """
        clientes = self.buscar_por_nombre(
            db, firm_id, nombre, apellido, nombre_empresa
        )
        return len(clientes) > 0


crud_cliente = CRUDCliente(Cliente)