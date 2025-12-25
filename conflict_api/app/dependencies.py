"""
Dependencias compartidas para FastAPI.
"""

from fastapi import Header, HTTPException, status
from typing import Annotated


def get_firm_id(
    x_firm_id: Annotated[int | None, Header()] = None
) -> int:
    """
    Extrae y valida el ID del bufete desde el header X-Firm-ID.

    Args:
        x_firm_id: ID del bufete desde header HTTP

    Returns:
        ID del bufete validado

    Raises:
        HTTPException: Si no se proporciona el header o es inválido

    Uso:
        @router.get("/items")
        def get_items(firm_id: int = Depends(get_firm_id)):
            ...
    """
    if x_firm_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Header 'X-Firm-ID' es requerido para esta operación"
        )

    if x_firm_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'X-Firm-ID' debe ser un número positivo"
        )

    return x_firm_id
