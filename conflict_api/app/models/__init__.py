"""
Modelos de base de datos SQLAlchemy.
"""

from app.models.firma import Firma
from app.models.cliente import Cliente
from app.models.asunto import Asunto
from app.models.parte_relacionada import ParteRelacionada
from app.models.perfil import Perfil
from app.models.estudios import Estudios
from app.models.areas_practica import AreasPractica
from app.models.ubicacion import Ubicacion
from app.models.planes import Planes

__all__ = [
    "Firma",
    "Cliente",
    "Asunto",
    "ParteRelacionada",
    "Perfil",
    "Estudios",
    "AreasPractica",
    "Ubicacion",
    "Planes",
]
