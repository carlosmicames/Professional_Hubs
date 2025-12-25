"""
Módulos CRUD para operaciones de base de datos.
"""

from app.crud.firma import crud_firma
from app.crud.cliente import crud_cliente
from app.crud.asunto import crud_asunto
from app.crud.parte_relacionada import crud_parte_relacionada

__all__ = ["crud_firma", "crud_cliente", "crud_asunto", "crud_parte_relacionada"]