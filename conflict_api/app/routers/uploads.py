"""
Endpoints for file uploads (logo, signature images).
MVP implementation - stores files in local directory.
"""

import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.perfil import Perfil

# Upload directory configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "logos"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "firmas"), exist_ok=True)

# Default firm ID for MVP
DEFAULT_FIRM_ID = 1

router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    # Check extension
    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no permitido. Formatos aceptados: {', '.join(ALLOWED_EXTENSIONS)}"
        )


def save_file(file: UploadFile, subdirectory: str) -> str:
    """Save uploaded file and return the relative path."""
    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, subdirectory, filename)

    with open(filepath, "wb") as buffer:
        content = file.file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Archivo demasiado grande. Maximo 5MB."
            )
        buffer.write(content)

    # Return relative URL path
    return f"/uploads/{subdirectory}/{filename}"


@router.post(
    "/logo",
    summary="Subir logo de empresa",
    description="Sube el logo de la empresa para facturas. Tamano recomendado: 300x100 pixeles."
)
async def upload_logo(
    file: UploadFile = File(..., description="Imagen del logo (JPG, PNG)"),
    firma_id: int = DEFAULT_FIRM_ID,
    db: Session = Depends(get_db)
):
    """Upload company logo and update profile."""
    validate_file(file)

    try:
        file_url = save_file(file, "logos")

        # Update profile with logo URL
        perfil = db.query(Perfil).filter(Perfil.firma_id == firma_id).first()
        if perfil is None:
            perfil = Perfil(firma_id=firma_id, logo_empresa_url=file_url)
            db.add(perfil)
        else:
            perfil.logo_empresa_url = file_url

        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Logo subido exitosamente",
                "url": file_url
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar archivo: {str(e)}"
        )


@router.post(
    "/firma",
    summary="Subir firma del abogado",
    description="Sube la firma del abogado para facturas. Tamano recomendado: 300x100 pixeles."
)
async def upload_firma(
    file: UploadFile = File(..., description="Imagen de la firma (JPG, PNG)"),
    firma_id: int = DEFAULT_FIRM_ID,
    db: Session = Depends(get_db)
):
    """Upload attorney signature and update profile."""
    validate_file(file)

    try:
        file_url = save_file(file, "firmas")

        # Update profile with signature URL
        perfil = db.query(Perfil).filter(Perfil.firma_id == firma_id).first()
        if perfil is None:
            perfil = Perfil(firma_id=firma_id, firma_abogado_url=file_url)
            db.add(perfil)
        else:
            perfil.firma_abogado_url = file_url

        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Firma subida exitosamente",
                "url": file_url
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar archivo: {str(e)}"
        )
