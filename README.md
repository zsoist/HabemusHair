# HabemusHair — Hair Planning Copilot

Sistema de apoyo clinico para consulta de trasplante capilar. Medicion objetiva, planificacion inteligente, resultados defendibles.

## Que es esto

Una herramienta web que ayuda al cirujano capilar durante la consulta inicial:

1. **Captura estandarizada** de fotos del paciente
2. **Medicion automatica** de densidad capilar con IA
3. **Estimacion inteligente** de rango de grafts necesarios
4. **Reporte PDF** profesional para el paciente

## Estado actual

- **Fase:** Pre-MVP (scaffold + documentacion)
- **Codigo:** Backend FastAPI funcional, DB schema completo, motor de estimacion de grafts
- **Mercado:** Colombia (sin competencia local accesible)

## Estructura del proyecto

```
HabemusHair/
|-- backend/                  # API (FastAPI + Python)
|   |-- app/
|   |   |-- api/routes/       # Endpoints de la API
|   |   |-- models/           # Tablas de base de datos
|   |   |-- services/         # Logica de negocio
|   |   |-- core/             # Configuracion
|   |   +-- main.py           # Punto de entrada
|   |-- tests/
|   |-- requirements.txt
|   +-- Dockerfile
|-- frontend/                 # Interfaz web (Next.js) — por crear
|-- services/
|   |-- cv-inference/         # Modelos de vision por computador
|   |-- planning-engine/      # Motor de estimacion de grafts
|   |-- simulation-engine/    # Simulacion visual (V3)
|   +-- report-engine/        # Generacion de PDFs
|-- docs/                     # Documentacion del proyecto
|   |-- PRODUCT_SCOPE.md      # Alcance del producto
|   |-- CLINICAL_CLAIMS.md    # Reglas de comunicacion clinica
|   |-- CAPTURE_PROTOCOL.md   # Protocolo de captura de fotos
|   |-- RISK_REGISTER.md      # Registro de riesgos
|   |-- SYSTEM_ARCHITECTURE.md # Arquitectura del sistema
|   |-- DATA_DICTIONARY.md    # Diccionario de datos
|   |-- guia-reunion-medico.html    # Guia para reunion con medico
|   +-- presentacion-proyecto.html  # Presentacion para el medico
|-- data/                     # Datos (NO se sube a Git)
|-- models/                   # Modelos de ML (NO se sube a Git)
|-- docker-compose.yml        # Levanta todo con un comando
+-- GUIA_PRINCIPIANTES.md     # Guia completa para empezar
```

## Inicio rapido

```bash
# 1. Clonar el repo
git clone https://github.com/zsoist/HabemusHair.git
cd HabemusHair

# 2. Levantar infraestructura con Docker
docker compose up -d

# 3. Ver la API funcionando
open http://localhost:8000/docs
```

## Documentacion

- [Guia para principiantes](GUIA_PRINCIPIANTES.md)
- [Arquitectura del sistema](docs/SYSTEM_ARCHITECTURE.md)
- [Diccionario de datos](docs/DATA_DICTIONARY.md)
- [Protocolo de captura](docs/CAPTURE_PROTOCOL.md)
- [Alcance del producto](docs/PRODUCT_SCOPE.md)

## Stack

| Componente | Tecnologia | Para que |
|-----------|-----------|---------|
| Backend | FastAPI + Python | API REST |
| Frontend | Next.js + TypeScript | Interfaz web |
| Base de datos | PostgreSQL | Datos estructurados |
| Almacenamiento | MinIO (S3-compatible) | Fotos de pacientes |
| Cola de tareas | Celery + Redis | Inferencia asincrona |
| ML | PyTorch + OpenCV | Segmentacion, medicion |
| Contenedores | Docker Compose | Todo en un comando |
