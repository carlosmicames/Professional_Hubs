"""
Modelos de base de datos SQLAlchemy.
"""

from app.models.firma import Firma
from app.models.cliente import Cliente
from app.models.asunto import Asunto
from app.models.parte_relacionada import ParteRelacionada

__all__ = ["Firma", "Cliente", "Asunto", "ParteRelacionada"]