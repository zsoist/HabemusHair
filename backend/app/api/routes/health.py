"""
Endpoint de salud — Para verificar que el servidor esta funcionando.

PARA PRINCIPIANTES:
Un "health check" es un endpoint simple que devuelve "OK".
Lo usan herramientas de monitoreo para saber si el servidor esta vivo.
Docker tambien lo usa para saber si el contenedor esta sano.

EJEMPLO:
    curl http://localhost:8000/health
    # Respuesta: {"status": "healthy", "version": "0.1.0"}
"""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Verifica que el servidor esta funcionando."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "app": settings.APP_NAME,
    }
