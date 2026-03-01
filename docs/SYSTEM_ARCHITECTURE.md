# SYSTEM_ARCHITECTURE — Arquitectura del sistema

## Vista general

```
                    +------------------+
                    |    FRONTEND      |
                    |    (Next.js)     |
                    |   Puerto 3000    |
                    +--------+---------+
                             |
                             | HTTP/REST
                             |
                    +--------v---------+
                    |    BACKEND       |
                    |    (FastAPI)     |
                    |   Puerto 8000    |
                    +--+----+----+----++
                       |    |    |    |
              +--------+  +-+  ++   ++--------+
              |           |    |              |
     +--------v---+ +----v--+ +v--------+ +--v---------+
     | PostgreSQL  | | Redis | | MinIO   | | CV Service |
     | (datos)     | |(colas)| | (fotos) | | (modelos)  |
     | Puerto 5432 | | 6379  | | 9000    | | interno    |
     +-------------+ +-------+ +---------+ +------------+
```

## Componentes

### Frontend (Next.js + TypeScript + Tailwind)
- **Que hace:** La interfaz que ve el medico en el navegador
- **Responsabilidades:**
  - Wizard de captura de fotos
  - Visualizacion de segmentaciones
  - Planning canvas (V2)
  - Visor de reportes
- **Donde esta:** `/frontend/`

### Backend (FastAPI + Python)
- **Que hace:** El "cerebro" que procesa todo
- **Responsabilidades:**
  - API REST para el frontend
  - Validacion de datos
  - Orquestacion de servicios
  - Autenticacion
  - Generacion de reportes
- **Donde esta:** `/backend/`

### Servicios de ML (Python + PyTorch)
- **cv-inference:** Segmentacion anatomica, medicion de densidad
- **planning-engine:** Motor de estimacion de grafts (reglas clinicas)
- **simulation-engine:** Simulacion visual (V3)
- **report-engine:** Generacion de PDFs
- **Donde estan:** `/services/`

### Base de datos (PostgreSQL)
- **Que hace:** Almacena todos los datos estructurados
- **Tablas principales:** patients, images, segmentations, planning_sessions, graft_estimations
- **Schema completo:** `/backend/app/models/database.py`

### Cola de tareas (Redis + Celery)
- **Que hace:** Maneja tareas lentas de forma asincrona
- **Por que:** La inferencia de modelos de ML puede tardar segundos o minutos. No podemos dejar al medico esperando con la pantalla congelada
- **Flujo:**
  1. Frontend pide "segmentar esta imagen"
  2. Backend pone la tarea en la cola de Redis
  3. Un worker Celery toma la tarea y ejecuta el modelo
  4. Cuando termina, guarda el resultado en la DB
  5. Frontend recibe notificacion y muestra el resultado

### Almacenamiento (MinIO)
- **Que hace:** Guarda archivos binarios (fotos, mascaras, PDFs)
- **Por que no en la DB:** Las imagenes son grandes. Ponerlas en PostgreSQL haria la DB lenta. MinIO es como un "mini AWS S3" que corre local
- **Consola web:** http://localhost:9001 (minioadmin/minioadmin)

## Decisiones de arquitectura

| Decision | Opcion elegida | Por que |
|----------|---------------|---------|
| Framework backend | FastAPI | Async nativo, documentacion automatica, tipado fuerte, ecosistema Python ML |
| Framework frontend | Next.js | SSR, buen ecosistema React, deploy facil |
| Base de datos | PostgreSQL | Robusta, JSON nativo, geolocalización futura, gratis |
| ORM | SQLAlchemy 2.0 | Estandar de Python, migraciones con Alembic |
| Almacenamiento | MinIO | Compatible S3, corre local, facil migrar a AWS despues |
| Cola de tareas | Celery + Redis | Estandar de Python para tareas asincronas |
| ML framework | PyTorch | Mejor ecosistema para investigacion, mas modelos pretrained |
| Contenedores | Docker Compose | Un comando levanta todo, reproducible, facil para principiantes |

## Flujo de datos principal

```
MEDICO toma foto
    |
    v
[Frontend] --> POST /api/capture/upload --> [Backend]
    |                                           |
    |                                    Valida calidad
    |                                    Guarda en MinIO
    |                                    Registra en DB
    |                                           |
    |                                    Encola tarea de segmentacion
    |                                           |
    |                                    [Celery Worker]
    |                                    Carga modelo ML
    |                                    Ejecuta inferencia
    |                                    Guarda mascara en MinIO
    |                                    Guarda resultado en DB
    |                                           |
    v                                           |
[Frontend] <-- GET /api/segmentation/{id} <-----+
    |
    v
MEDICO ve zonas segmentadas, ajusta plan
    |
    v
[Frontend] --> POST /api/planning/ --> [Backend]
    |                                       |
    |                                Motor de estimacion
    |                                Calcula rango de grafts
    |                                Genera reporte PDF
    |                                       |
    v                                       |
[Frontend] <-- Reporte listo <--------------+
    |
    v
MEDICO descarga PDF, lo muestra al paciente
```
