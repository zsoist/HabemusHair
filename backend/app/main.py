"""
PUNTO DE ENTRADA DE LA API — FastAPI

QUE HACE ESTE ARCHIVO:
Este es el archivo principal del backend. Cuando "arrancas el servidor",
FastAPI lee este archivo y crea la aplicacion web.

PARA PRINCIPIANTES:
- FastAPI es un framework para crear APIs (interfaces que comunican frontend y backend).
- Cada "endpoint" es una URL que hace algo (ej: /api/patients crea un paciente).
- Este archivo configura la app y conecta todas las rutas.

COMO CORRERLO:
    cd backend
    uvicorn app.main:app --reload

    Luego abre http://localhost:8000/docs para ver TODA la API documentada automaticamente.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import patients, capture, health

# --- Crear la app ---
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    Hair Planning Copilot API.

    Sistema de apoyo clinico para consulta de trasplante capilar.
    Este backend maneja: pacientes, sesiones de captura, imagenes,
    segmentaciones, mediciones, planificacion y reportes.
    """,
    docs_url="/docs",       # Documentacion interactiva: http://localhost:8000/docs
    redoc_url="/redoc",     # Documentacion alternativa: http://localhost:8000/redoc
)

# --- CORS ---
# CORS permite que el frontend (Next.js en puerto 3000) hable con el backend (puerto 8000).
# Sin esto, el navegador bloquea las peticiones por seguridad.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Frontend en desarrollo
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Registrar rutas ---
app.include_router(health.router, tags=["Health"])
app.include_router(patients.router, prefix="/api/patients", tags=["Patients"])
app.include_router(capture.router, prefix="/api/capture", tags=["Capture"])
