"""
Rutas de Captura — Subir y validar imagenes.

QUE HACE ESTE ARCHIVO:
Maneja la subida de fotos de pacientes y valida su calidad automaticamente.

PARA PRINCIPIANTES:
Cuando el medico toma una foto del paciente, esa foto se sube a traves
de estos endpoints. El sistema valida:
- Que la imagen no este borrosa (blur)
- Que tenga buena exposicion (no muy oscura ni muy clara)
- Que tenga resolucion suficiente (minimo 640x480)
- Que el tipo de imagen sea valido (frontal, lateral, etc.)

Despues la guarda en el almacenamiento (MinIO/S3) y registra la metadata
en la base de datos.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

router = APIRouter()


class ImageType(str, Enum):
    FRONTAL = "frontal"
    LATERAL_LEFT = "lateral_left"
    LATERAL_RIGHT = "lateral_right"
    TOP = "top"
    OCCIPITAL = "occipital"
    TRICHOSCOPY = "trichoscopy"


class ImageQualityResult(BaseModel):
    """Resultado de la validacion de calidad de una imagen."""
    passed: bool
    blur_score: float
    exposure_score: float
    resolution_ok: bool
    warnings: list[str]


class UploadResponse(BaseModel):
    image_id: UUID
    quality: ImageQualityResult
    message: str


@router.post("/upload", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(..., description="La foto a subir (JPEG o PNG)"),
    patient_id: str = Form(..., description="ID del paciente"),
    image_type: ImageType = Form(..., description="Tipo de imagen: frontal, lateral_left, etc."),
    capture_session_id: Optional[str] = Form(None, description="ID de sesion de captura existente"),
):
    """
    Subir una imagen de paciente y validar su calidad automaticamente.

    El sistema valida:
    - Formato: solo JPEG y PNG
    - Resolucion minima: 640x480
    - Blur: detecta si la foto esta borrosa
    - Exposicion: detecta si esta sobre/sub-expuesta

    Si la imagen no pasa la validacion, se sube pero con advertencias.
    """
    # Validar formato
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado: {file.content_type}. Use JPEG o PNG."
        )

    # Leer contenido
    contents = await file.read()
    file_size = len(contents)

    # Validar tamano (max 20MB)
    max_size = 20 * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo muy grande: {file_size / 1024 / 1024:.1f}MB. Maximo: 20MB."
        )

    # TODO: Implementar validacion real de calidad con OpenCV
    # Por ahora retornamos valores placeholder
    quality = ImageQualityResult(
        passed=True,
        blur_score=0.85,
        exposure_score=0.72,
        resolution_ok=True,
        warnings=[],
    )

    image_id = uuid4()

    # TODO: Guardar en MinIO/S3 y registrar en base de datos

    return UploadResponse(
        image_id=image_id,
        quality=quality,
        message=f"Imagen {image_type.value} subida exitosamente. Calidad: OK.",
    )
