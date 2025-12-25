"""
CRUD para Firma (Bufete).
"""

from app.crud.base import CRUDBase
from app.models.firma import Firma
from app.schemas.firma import FirmaCreate, FirmaUpdate


class CRUDFirma(CRUDBase[Firma, FirmaCreate, FirmaUpdate]):
    """
    CRUD para operaciones de Firma.
    No requiere filtrado por firma (es la entidad principal de tenant).
    """
    pass


crud_firma = CRUDFirma(Firma)