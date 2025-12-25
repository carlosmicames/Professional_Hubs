"""
Servicio de verificación de conflictos de interés con fuzzy matching.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from fuzzywuzzy import fuzz
from unidecode import unidecode

from app.models.cliente import Cliente
from app.models.asunto import Asunto
from app.models.parte_relacionada import ParteRelacionada
from app.schemas.conflicto import BusquedaConflicto, ResultadoConflicto, ConflictoEncontrado
from app.config import get_settings

settings = get_settings()


class ConflictChecker:
    """
    Servicio para verificar conflictos de interés con fuzzy matching.

    Características:
    - Búsqueda exacta (case-insensitive, accent-insensitive)
    - Búsqueda difusa con fuzzywuzzy (similitud > 70%)
    - Búsqueda en clientes Y partes relacionadas
    - Niveles de confianza (Alta: >=90%, Media: 70-89%)
    - Normalización de acentos (José=Jose, María=Maria, González=Gonzalez)
    """

    def __init__(self):
        self.fuzzy_threshold = settings.fuzzy_threshold
        self.high_confidence_threshold = settings.fuzzy_high_confidence

    def verificar_conflictos(
        self,
        db: Session,
        firm_id: int,
        busqueda: BusquedaConflicto
    ) -> ResultadoConflicto:
        """
        Busca conflictos de interés para un cliente potencial.

        Busca en:
        - Clientes existentes (nombre + apellido(s) o nombre_empresa)
        - Partes relacionadas en TODOS los asuntos (activos y cerrados)

        Retorna resultados ordenados por confianza (mayor a menor).

        Args:
            db: Sesión de base de datos
            firm_id: ID del bufete
            busqueda: Datos de búsqueda

        Returns:
            ResultadoConflicto con lista de conflictos encontrados
        """
        conflictos: List[ConflictoEncontrado] = []
        termino_busqueda = self._construir_termino_busqueda(busqueda)

        # Buscar por nombre de persona
        if busqueda.nombre or busqueda.apellido:
            # Buscar en clientes
            conflictos_clientes = self._buscar_en_clientes_persona(
                db, firm_id, busqueda
            )
            conflictos.extend(conflictos_clientes)

            # Buscar en partes relacionadas
            conflictos_partes = self._buscar_en_partes_relacionadas(
                db, firm_id, busqueda
            )
            conflictos.extend(conflictos_partes)

        # Buscar por nombre de empresa
        if busqueda.nombre_empresa:
            # Buscar en clientes empresa
            conflictos_empresa = self._buscar_en_clientes_empresa(
                db, firm_id, busqueda.nombre_empresa
            )
            conflictos.extend(conflictos_empresa)

            # Buscar en partes relacionadas empresa
            conflictos_partes_empresa = self._buscar_en_partes_empresa(
                db, firm_id, busqueda.nombre_empresa
            )
            conflictos.extend(conflictos_partes_empresa)

        # Eliminar duplicados (mismo asunto puede aparecer múltiples veces)
        conflictos = self._eliminar_duplicados(conflictos)

        # Ordenar por confianza (mayor a menor)
        conflictos.sort(key=lambda x: x.similitud_score, reverse=True)

        # Construir mensaje
        if conflictos:
            alta = sum(1 for c in conflictos if c.nivel_confianza == "alta")
            media = sum(1 for c in conflictos if c.nivel_confianza == "media")
            mensaje = f"Se encontraron {len(conflictos)} posible(s) conflicto(s): {alta} alta confianza, {media} media confianza"
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
        if busqueda.segundo_apellido:
            partes.append(busqueda.segundo_apellido)
        if busqueda.nombre_empresa:
            if partes:
                partes.append(f"/ {busqueda.nombre_empresa}")
            else:
                partes.append(busqueda.nombre_empresa)

        return " ".join(partes) if partes else "Sin término"

    def _normalizar_texto(self, texto: Optional[str]) -> str:
        """
        Normaliza texto para comparación:
        - Minúsculas
        - Sin acentos (José -> jose, María -> maria, González -> gonzalez)
        - Sin espacios extras

        Args:
            texto: Texto a normalizar

        Returns:
            Texto normalizado
        """
        if not texto:
            return ""
        # Convertir a minúsculas
        texto = texto.lower()
        # Remover acentos (José -> jose, María -> maria)
        texto = unidecode(texto)
        # Remover espacios extras
        texto = " ".join(texto.split())
        return texto

    def _calcular_similitud(self, texto1: str, texto2: str) -> float:
        """
        Calcula similitud entre dos textos usando fuzzywuzzy.

        Args:
            texto1: Primer texto
            texto2: Segundo texto

        Returns:
            Porcentaje de similitud (0-100)
        """
        if not texto1 or not texto2:
            return 0.0

        # Normalizar ambos textos
        t1_norm = self._normalizar_texto(texto1)
        t2_norm = self._normalizar_texto(texto2)

        # Calcular similitud usando token_sort_ratio (mejor para nombres con orden diferente)
        score = fuzz.token_sort_ratio(t1_norm, t2_norm)

        return float(score)

    def _determinar_nivel_confianza(self, score: float) -> str:
        """
        Determina nivel de confianza basado en score de similitud.

        Args:
            score: Porcentaje de similitud (0-100)

        Returns:
            "alta" para >= 90%, "media" para 70-89%
        """
        if score >= self.high_confidence_threshold:
            return "alta"
        else:
            return "media"

    def _buscar_en_clientes_persona(
        self,
        db: Session,
        firm_id: int,
        busqueda: BusquedaConflicto
    ) -> List[ConflictoEncontrado]:
        """
        Busca coincidencias en clientes usando fuzzy matching.

        Args:
            db: Sesión de base de datos
            firm_id: ID del bufete
            busqueda: Datos de búsqueda

        Returns:
            Lista de conflictos encontrados
        """
        conflictos = []

        # Construir nombre completo buscado
        partes_busqueda = [
            p for p in [busqueda.nombre, busqueda.apellido, busqueda.segundo_apellido] if p
        ]
        nombre_busqueda = " ".join(partes_busqueda)

        if not nombre_busqueda:
            return []

        # Obtener todos los clientes activos del bufete con sus asuntos
        query = (
            db.query(Cliente, Asunto)
            .join(Asunto, Cliente.id == Asunto.cliente_id)
            .filter(
                Cliente.firma_id == firm_id,
                Cliente.esta_activo == True,
                Asunto.esta_activo == True,
                # Filtrar solo clientes persona (no empresas)
                or_(Cliente.nombre.isnot(None), Cliente.apellido.isnot(None))
            )
        )

        resultados = query.all()

        # Calcular similitud para cada resultado
        for cliente, asunto in resultados:
            # Construir nombre completo del cliente
            partes_cliente = [
                p for p in [cliente.nombre, cliente.apellido, cliente.segundo_apellido] if p
            ]
            nombre_cliente = " ".join(partes_cliente)

            # Calcular similitud
            score = self._calcular_similitud(nombre_busqueda, nombre_cliente)

            # Solo incluir si supera el umbral
            if score >= self.fuzzy_threshold:
                conflictos.append(ConflictoEncontrado(
                    cliente_id=cliente.id,
                    cliente_nombre=cliente.nombre_completo,
                    asunto_id=asunto.id,
                    asunto_nombre=asunto.nombre_asunto,
                    estado_asunto=asunto.estado,
                    tipo_coincidencia="cliente_persona",
                    similitud_score=score,
                    nivel_confianza=self._determinar_nivel_confianza(score),
                    campo_coincidente="cliente_nombre"
                ))

        return conflictos

    def _buscar_en_clientes_empresa(
        self,
        db: Session,
        firm_id: int,
        nombre_empresa: str
    ) -> List[ConflictoEncontrado]:
        """
        Busca coincidencias en empresas usando fuzzy matching.

        Args:
            db: Sesión de base de datos
            firm_id: ID del bufete
            nombre_empresa: Nombre de empresa a buscar

        Returns:
            Lista de conflictos encontrados
        """
        conflictos = []

        # Obtener todos los clientes empresa del bufete con sus asuntos
        query = (
            db.query(Cliente, Asunto)
            .join(Asunto, Cliente.id == Asunto.cliente_id)
            .filter(
                Cliente.firma_id == firm_id,
                Cliente.esta_activo == True,
                Asunto.esta_activo == True,
                Cliente.nombre_empresa.isnot(None)
            )
        )

        resultados = query.all()

        # Calcular similitud para cada resultado
        for cliente, asunto in resultados:
            score = self._calcular_similitud(nombre_empresa, cliente.nombre_empresa)

            # Solo incluir si supera el umbral
            if score >= self.fuzzy_threshold:
                conflictos.append(ConflictoEncontrado(
                    cliente_id=cliente.id,
                    cliente_nombre=cliente.nombre_completo,
                    asunto_id=asunto.id,
                    asunto_nombre=asunto.nombre_asunto,
                    estado_asunto=asunto.estado,
                    tipo_coincidencia="cliente_empresa",
                    similitud_score=score,
                    nivel_confianza=self._determinar_nivel_confianza(score),
                    campo_coincidente="empresa_nombre"
                ))

        return conflictos

    def _buscar_en_partes_relacionadas(
        self,
        db: Session,
        firm_id: int,
        busqueda: BusquedaConflicto
    ) -> List[ConflictoEncontrado]:
        """
        Busca coincidencias en partes relacionadas de asuntos.

        Args:
            db: Sesión de base de datos
            firm_id: ID del bufete
            busqueda: Datos de búsqueda

        Returns:
            Lista de conflictos encontrados
        """
        conflictos = []

        # Construir nombre completo buscado
        partes_busqueda = [
            p for p in [busqueda.nombre, busqueda.apellido, busqueda.segundo_apellido] if p
        ]
        nombre_busqueda = " ".join(partes_busqueda)

        if not nombre_busqueda:
            return []

        # Obtener todas las partes relacionadas activas de asuntos del bufete
        query = (
            db.query(ParteRelacionada, Asunto, Cliente)
            .join(Asunto, ParteRelacionada.asunto_id == Asunto.id)
            .join(Cliente, Asunto.cliente_id == Cliente.id)
            .filter(
                Cliente.firma_id == firm_id,
                ParteRelacionada.esta_activo == True,
                Asunto.esta_activo == True,
                Cliente.esta_activo == True
            )
        )

        resultados = query.all()

        # Calcular similitud para cada resultado
        for parte, asunto, cliente in resultados:
            score = self._calcular_similitud(nombre_busqueda, parte.nombre)

            # Solo incluir si supera el umbral
            if score >= self.fuzzy_threshold:
                conflictos.append(ConflictoEncontrado(
                    cliente_id=cliente.id,
                    cliente_nombre=cliente.nombre_completo,
                    asunto_id=asunto.id,
                    asunto_nombre=asunto.nombre_asunto,
                    estado_asunto=asunto.estado,
                    tipo_coincidencia=f"parte_relacionada_{parte.tipo_relacion.value}",
                    similitud_score=score,
                    nivel_confianza=self._determinar_nivel_confianza(score),
                    campo_coincidente=f"parte_relacionada ({parte.tipo_relacion.value}: {parte.nombre})"
                ))

        return conflictos

    def _buscar_en_partes_empresa(
        self,
        db: Session,
        firm_id: int,
        nombre_empresa: str
    ) -> List[ConflictoEncontrado]:
        """
        Busca coincidencias de empresas en partes relacionadas.

        Args:
            db: Sesión de base de datos
            firm_id: ID del bufete
            nombre_empresa: Nombre de empresa a buscar

        Returns:
            Lista de conflictos encontrados
        """
        conflictos = []

        # Obtener todas las partes relacionadas activas de asuntos del bufete
        query = (
            db.query(ParteRelacionada, Asunto, Cliente)
            .join(Asunto, ParteRelacionada.asunto_id == Asunto.id)
            .join(Cliente, Asunto.cliente_id == Cliente.id)
            .filter(
                Cliente.firma_id == firm_id,
                ParteRelacionada.esta_activo == True,
                Asunto.esta_activo == True,
                Cliente.esta_activo == True
            )
        )

        resultados = query.all()

        # Calcular similitud para cada resultado
        for parte, asunto, cliente in resultados:
            score = self._calcular_similitud(nombre_empresa, parte.nombre)

            # Solo incluir si supera el umbral
            if score >= self.fuzzy_threshold:
                conflictos.append(ConflictoEncontrado(
                    cliente_id=cliente.id,
                    cliente_nombre=cliente.nombre_completo,
                    asunto_id=asunto.id,
                    asunto_nombre=asunto.nombre_asunto,
                    estado_asunto=asunto.estado,
                    tipo_coincidencia=f"parte_relacionada_{parte.tipo_relacion.value}",
                    similitud_score=score,
                    nivel_confianza=self._determinar_nivel_confianza(score),
                    campo_coincidente=f"parte_relacionada ({parte.tipo_relacion.value}: {parte.nombre})"
                ))

        return conflictos

    def _eliminar_duplicados(self, conflictos: List[ConflictoEncontrado]) -> List[ConflictoEncontrado]:
        """
        Elimina conflictos duplicados, manteniendo el de mayor score.

        Args:
            conflictos: Lista de conflictos

        Returns:
            Lista sin duplicados
        """
        if not conflictos:
            return []

        # Agrupar por asunto_id
        por_asunto = {}
        for conflicto in conflictos:
            key = conflicto.asunto_id
            if key not in por_asunto or conflicto.similitud_score > por_asunto[key].similitud_score:
                por_asunto[key] = conflicto

        return list(por_asunto.values())


# Instancia singleton del servicio
conflict_checker = ConflictChecker()
