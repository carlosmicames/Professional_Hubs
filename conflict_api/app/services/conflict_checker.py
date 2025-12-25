"""
Servicio de verificación de conflictos de interés.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.cliente import Cliente
from app.models.asunto import Asunto
from app.schemas.conflicto import BusquedaConflicto, ResultadoConflicto, ConflictoEncontrado


class ConflictChecker:
    """
    Servicio para verificar conflictos de interés.
    Busca coincidencias exactas en nombres de clientes existentes.
    """
    
    def verificar_conflictos(
        self, 
        db: Session, 
        firm_id: int,
        busqueda: BusquedaConflicto
    ) -> ResultadoConflicto:
        """
        Busca conflictos de interés para un cliente potencial.
        
        Busca coincidencias exactas (case-insensitive) en:
        - Nombre + Apellido de clientes existentes
        - Nombre de empresa de clientes existentes
        
        Incluye asuntos activos y cerrados.
        
        Args:
            db: Sesión de base de datos
            firm_id: ID del bufete
            busqueda: Datos de búsqueda
        
        Returns:
            ResultadoConflicto con lista de conflictos encontrados
        """
        conflictos: List[ConflictoEncontrado] = []
        termino_busqueda = self._construir_termino_busqueda(busqueda)
        
        # Buscar por nombre y apellido
        if busqueda.nombre or busqueda.apellido:
            conflictos_nombre = self._buscar_por_nombre_persona(
                db, firm_id, busqueda.nombre, busqueda.apellido
            )
            conflictos.extend(conflictos_nombre)
        
        # Buscar por nombre de empresa
        if busqueda.nombre_empresa:
            conflictos_empresa = self._buscar_por_empresa(
                db, firm_id, busqueda.nombre_empresa
            )
            conflictos.extend(conflictos_empresa)
        
        # Construir mensaje
        if conflictos:
            mensaje = f"Se encontraron {len(conflictos)} posible(s) conflicto(s) de interés"
        else:
            mensaje = "No se encontraron conflictos de interés"
        
        return ResultadoConflicto(
            termino_busqueda=termino_busqueda,
            total_conflictos=len(conflictos),
            conflictos=conflictos,
            mensaje=mensaje
        )
    
    def _construir_termino_busqueda(self, busqueda: BusquedaConflicto) -> str:
        """Construye string descriptivo del término buscado."""
        partes = []
        
        if busqueda.nombre:
            partes.append(busqueda.nombre)
        if busqueda.apellido:
            partes.append(busqueda.apellido)
        if busqueda.nombre_empresa:
            if partes:
                partes.append(f"/ {busqueda.nombre_empresa}")
            else:
                partes.append(busqueda.nombre_empresa)
        
        return " ".join(partes) if partes else "Sin término"
    
    def _buscar_por_nombre_persona(
        self, 
        db: Session, 
        firm_id: int,
        nombre: Optional[str],
        apellido: Optional[str]
    ) -> List[ConflictoEncontrado]:
        """
        Busca conflictos por nombre y apellido de persona.
        
        Args:
            db: Sesión de base de datos
            firm_id: ID del bufete
            nombre: Nombre a buscar
            apellido: Apellido a buscar
        
        Returns:
            Lista de conflictos encontrados
        """
        conflictos = []
        
        # Query base: clientes activos del bufete con sus asuntos
        query = (
            db.query(Cliente, Asunto)
            .join(Asunto, Cliente.id == Asunto.cliente_id)
            .filter(
                Cliente.firma_id == firm_id,
                Cliente.esta_activo == True,
                Asunto.esta_activo == True
            )
        )
        
        # Filtrar por nombre y/o apellido (exacto, case-insensitive)
        if nombre and apellido:
            query = query.filter(
                func.lower(Cliente.nombre) == func.lower(nombre),
                func.lower(Cliente.apellido) == func.lower(apellido)
            )
        elif nombre:
            query = query.filter(func.lower(Cliente.nombre) == func.lower(nombre))
        elif apellido:
            query = query.filter(func.lower(Cliente.apellido) == func.lower(apellido))
        else:
            return []
        
        resultados = query.all()
        
        for cliente, asunto in resultados:
            conflictos.append(ConflictoEncontrado(
                cliente_id=cliente.id,
                cliente_nombre=cliente.nombre_completo,
                asunto_id=asunto.id,
                asunto_nombre=asunto.nombre_asunto,
                estado_asunto=asunto.estado,
                tipo_coincidencia="cliente_existente"
            ))
        
        return conflictos
    
    def _buscar_por_empresa(
        self, 
        db: Session, 
        firm_id: int,
        nombre_empresa: str
    ) -> List[ConflictoEncontrado]:
        """
        Busca conflictos por nombre de empresa.
        
        Args:
            db: Sesión de base de datos
            firm_id: ID del bufete
            nombre_empresa: Nombre de empresa a buscar
        
        Returns:
            Lista de conflictos encontrados
        """
        conflictos = []
        
        # Query: clientes empresa activos del bufete con sus asuntos
        query = (
            db.query(Cliente, Asunto)
            .join(Asunto, Cliente.id == Asunto.cliente_id)
            .filter(
                Cliente.firma_id == firm_id,
                Cliente.esta_activo == True,
                Asunto.esta_activo == True,
                func.lower(Cliente.nombre_empresa) == func.lower(nombre_empresa)
            )
        )
        
        resultados = query.all()
        
        for cliente, asunto in resultados:
            conflictos.append(ConflictoEncontrado(
                cliente_id=cliente.id,
                cliente_nombre=cliente.nombre_completo,
                asunto_id=asunto.id,
                asunto_nombre=asunto.nombre_asunto,
                estado_asunto=asunto.estado,
                tipo_coincidencia="empresa_existente"
            ))
        
        return conflictos


# Instancia singleton del servicio
conflict_checker = ConflictChecker()