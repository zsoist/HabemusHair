"""
Rutas de Pacientes — CRUD basico.

QUE HACE ESTE ARCHIVO:
Define los endpoints (URLs) para crear, leer, actualizar y listar pacientes.

PARA PRINCIPIANTES:
- GET = leer datos (como abrir un archivo)
- POST = crear datos nuevos (como guardar un archivo nuevo)
- PUT = actualizar datos existentes (como editar un archivo)
- DELETE = borrar datos (como eliminar un archivo)

Los endpoints aqui son:
    POST   /api/patients/        -> Crear paciente nuevo
    GET    /api/patients/        -> Listar todos los pacientes
    GET    /api/patients/{id}    -> Ver un paciente especifico
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

router = APIRouter()


# --- Schemas (formatos de datos) ---
# Pydantic valida automaticamente que los datos tengan el formato correcto.

class PatientCreate(BaseModel):
    """Datos necesarios para crear un paciente nuevo."""
    external_id: str = Field(..., description="Codigo del paciente en la clinica", examples=["PAC-001"])
    sex: str = Field(..., description="male o female", examples=["male"])
    age: int = Field(..., ge=18, le=100, description="Edad del paciente", examples=[35])
    fitzpatrick: Optional[int] = Field(None, ge=1, le=6, description="Escala Fitzpatrick 1-6")
    norwood_ludwig: Optional[str] = Field(None, description="Grado alopecia", examples=["NW3"])
    diagnosis_notes: Optional[str] = None
    medications: Optional[str] = None
    consent_data_usage: bool = Field(False, description="Consentimiento para uso en ML")


class PatientResponse(BaseModel):
    """Formato de respuesta cuando devolvemos datos de un paciente."""
    id: UUID
    external_id: str
    sex: str
    age: int
    fitzpatrick: Optional[int] = None
    norwood_ludwig: Optional[str] = None
    diagnosis_notes: Optional[str] = None
    medications: Optional[str] = None
    consent_data_usage: bool
    created_at: datetime


# --- Almacenamiento temporal en memoria ---
# TODO: Reemplazar con base de datos real (PostgreSQL + SQLAlchemy)
# Por ahora usamos un diccionario en memoria para que puedas probar la API
# sin necesidad de tener PostgreSQL instalado.
_patients_db: dict[UUID, dict] = {}


# --- Endpoints ---

@router.post("/", response_model=PatientResponse, status_code=201)
async def create_patient(patient: PatientCreate):
    """
    Crear un paciente nuevo.

    Ejemplo con curl:
        curl -X POST http://localhost:8000/api/patients/ \\
            -H "Content-Type: application/json" \\
            -d '{"external_id": "PAC-001", "sex": "male", "age": 35}'
    """
    # Verificar que no exista otro paciente con el mismo external_id
    for p in _patients_db.values():
        if p["external_id"] == patient.external_id:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un paciente con external_id '{patient.external_id}'"
            )

    patient_id = uuid4()
    now = datetime.utcnow()

    patient_data = {
        "id": patient_id,
        **patient.model_dump(),
        "created_at": now,
    }
    _patients_db[patient_id] = patient_data

    return patient_data


@router.get("/", response_model=list[PatientResponse])
async def list_patients():
    """Listar todos los pacientes registrados."""
    return list(_patients_db.values())


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: UUID):
    """Ver los datos de un paciente especifico por su ID."""
    if patient_id not in _patients_db:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return _patients_db[patient_id]
