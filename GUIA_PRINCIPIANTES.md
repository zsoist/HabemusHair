# Guia para Principiantes — HabemusHair

Si estas aprendiendo a programar o es tu primer proyecto serio, esta guia es para ti. Explica TODO paso a paso.

---

## Que necesitas instalado en tu computador

### 1. Git (control de versiones)
Git es como un "historial de cambios" para tu codigo. Cada cambio que hagas se guarda y puedes volver atras si algo sale mal.

```bash
# Verificar si lo tienes:
git --version

# Si no lo tienes, instalalo:
# Mac:   brew install git
# Ubuntu: sudo apt install git
# Windows: descargar de https://git-scm.com
```

### 2. Docker (contenedores)
Docker es como una "maquina virtual ligera". Permite correr PostgreSQL, Redis y MinIO sin instalar cada uno manualmente. Piensa en ello como "descargar una app que ya viene configurada".

```bash
# Verificar si lo tienes:
docker --version
docker compose version

# Instalarlo:
# https://docs.docker.com/get-docker/
# En la pagina, elige tu sistema operativo y sigue los pasos.
```

### 3. Python 3.12+ (backend)
Python es el lenguaje principal del backend y de los modelos de ML.

```bash
# Verificar si lo tienes:
python3 --version

# Si no lo tienes o es version vieja:
# Mac:   brew install python@3.12
# Ubuntu: sudo apt install python3.12 python3.12-venv
```

### 4. Node.js 20+ (frontend)
Node.js es el "motor" que ejecuta el frontend (Next.js).

```bash
# Verificar si lo tienes:
node --version

# Instalarlo (recomiendo usar nvm para manejar versiones):
# curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
# nvm install 20
# nvm use 20
```

---

## Como empezar (paso a paso)

### Paso 1: Clonar el repositorio

"Clonar" significa descargar una copia del proyecto a tu computador.

```bash
git clone https://github.com/zsoist/HabemusHair.git
cd HabemusHair
```

### Paso 2: Levantar la infraestructura con Docker

Este comando descarga y arranca 3 servicios: PostgreSQL (base de datos), Redis (cola de tareas) y MinIO (almacenamiento de fotos).

```bash
# Levantar todo (la primera vez tarda unos minutos descargando)
docker compose up -d

# Verificar que todo esta corriendo:
docker compose ps

# Deberias ver algo como:
# habemus-db      running   5432
# habemus-redis   running   6379
# habemus-minio   running   9000, 9001
```

**Que puedes hacer ahora:**
- Ver MinIO (almacenamiento de fotos): http://localhost:9001 (usuario: minioadmin, password: minioadmin)

### Paso 3: Configurar el backend

```bash
# Entrar a la carpeta del backend
cd backend

# Crear un "entorno virtual" de Python
# (es como una carpeta aislada para las dependencias de ESTE proyecto)
python3 -m venv .venv

# Activar el entorno virtual
# Mac/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# Tu terminal deberia mostrar (.venv) al inicio de la linea.
# Eso significa que el entorno virtual esta activo.

# Instalar dependencias
pip install -r requirements.txt

# Copiar el archivo de configuracion
cp .env.example .env

# Arrancar el servidor
uvicorn app.main:app --reload
```

**Que puedes hacer ahora:**
- Ver la API documentada: http://localhost:8000/docs
- Probar crear un paciente directamente desde la interfaz de Swagger

### Paso 4: Probar que funciona

Abre http://localhost:8000/docs en tu navegador. Veras una interfaz interactiva donde puedes probar cada endpoint.

**Prueba crear un paciente:**
1. Click en "POST /api/patients/"
2. Click "Try it out"
3. Pega este JSON:
```json
{
  "external_id": "PAC-001",
  "sex": "male",
  "age": 35,
  "fitzpatrick": 3,
  "norwood_ludwig": "NW3"
}
```
4. Click "Execute"
5. Deberia devolver un 201 con los datos del paciente creado

### Paso 5: Probar el motor de estimacion de grafts

```bash
# Desde la raiz del proyecto:
cd services/planning-engine
python3 graft_estimator.py
```

Veras un resultado como:
```
============================================================
RESULTADO DE ESTIMACION DE GRAFTS
============================================================

  Rango conservador:  1234 grafts
  Rango recomendado:  1542 - 1773 grafts
  Rango agresivo:     1928 grafts

  Donante disponible: 2880 grafts
  Advertencia:        No
```

---

## Conceptos clave que debes entender

### API REST
Es como un "menu de restaurante" para software. El frontend (mesero) le pide cosas al backend (cocina) usando URLs:
- `GET /api/patients/` = "dame la lista de pacientes"
- `POST /api/patients/` = "crea un paciente nuevo"
- `GET /api/patients/123` = "dame los datos del paciente 123"

### Base de datos relacional (PostgreSQL)
Piensa en Excel pero mas poderoso. Cada "tabla" es una hoja, cada "fila" es un registro, cada "columna" es un campo. Las tablas se conectan entre si (un paciente tiene muchas fotos).

### Docker
Piensa en Docker como "cajas" que contienen todo lo necesario para correr un programa. En vez de instalar PostgreSQL en tu computador (que puede ser complicado), Docker lo corre dentro de una caja aislada.

Comandos basicos:
```bash
docker compose up -d      # Levantar todo
docker compose down        # Apagar todo
docker compose logs -f     # Ver logs en tiempo real
docker compose ps          # Ver que esta corriendo
docker compose down -v     # Apagar y BORRAR todos los datos
```

### Entorno virtual de Python
Es una carpeta que contiene SOLO las dependencias de este proyecto. Sin entorno virtual, las dependencias se mezclan con las de otros proyectos y causa problemas.

```bash
# Crear:     python3 -m venv .venv
# Activar:   source .venv/bin/activate
# Desactivar: deactivate
# Saber si esta activo: mira si tu terminal dice (.venv) al inicio
```

### Git basico
```bash
git status                 # Ver que archivos cambiaron
git add nombre_archivo     # Preparar un archivo para guardar
git commit -m "mensaje"    # Guardar cambios con un mensaje
git push                   # Subir cambios a GitHub
git pull                   # Descargar cambios de GitHub
git log --oneline -10      # Ver los ultimos 10 commits
```

---

## Estructura del proyecto explicada

```
HabemusHair/
|
|-- backend/                    <-- EL SERVIDOR (Python)
|   |-- app/
|   |   |-- api/routes/         <-- Los "endpoints" (URLs que hacen cosas)
|   |   |   |-- health.py       <-- GET /health (verificar que el server vive)
|   |   |   |-- patients.py     <-- CRUD de pacientes
|   |   |   +-- capture.py      <-- Subir y validar fotos
|   |   |-- models/
|   |   |   +-- database.py     <-- TODAS las tablas de la base de datos
|   |   |-- core/
|   |   |   +-- config.py       <-- Configuracion (puertos, URLs, etc.)
|   |   +-- main.py             <-- Punto de entrada del backend
|   |-- requirements.txt        <-- Lista de dependencias de Python
|   +-- Dockerfile              <-- Receta para crear el contenedor Docker
|
|-- services/                   <-- LOGICA DE NEGOCIO SEPARADA
|   |-- planning-engine/
|   |   +-- graft_estimator.py  <-- Motor de estimacion de grafts
|   |-- cv-inference/           <-- Modelos de IA (por crear)
|   +-- report-engine/          <-- Generacion de PDFs (por crear)
|
|-- docs/                       <-- DOCUMENTACION
|   |-- guia-reunion-medico.html    <-- Abrir en navegador: guia para hablar con el medico
|   |-- presentacion-proyecto.html  <-- Abrir en navegador: presentacion del proyecto
|   |-- PRODUCT_SCOPE.md       <-- Que hace y que no hace el producto
|   |-- CLINICAL_CLAIMS.md     <-- Que podemos y no podemos decir clinicamente
|   |-- CAPTURE_PROTOCOL.md    <-- Como tomar las fotos correctamente
|   |-- RISK_REGISTER.md       <-- Riesgos identificados y mitigaciones
|   |-- SYSTEM_ARCHITECTURE.md <-- Como se conectan los componentes
|   +-- DATA_DICTIONARY.md     <-- Que significa cada dato
|
|-- data/                       <-- DATOS (no se sube a Git)
|   |-- raw/                    <-- Fotos originales
|   |-- processed/              <-- Fotos procesadas
|   +-- annotations/            <-- Anotaciones para entrenamiento
|
|-- models/                     <-- MODELOS DE ML (no se sube a Git)
|   +-- weights/                <-- Pesos de modelos entrenados
|
|-- docker-compose.yml          <-- Un comando levanta todo
|-- .gitignore                  <-- Archivos que Git ignora
+-- README.md                   <-- Descripcion general
```

---

## Flujo de desarrollo diario

```bash
# 1. Abrir terminal, ir al proyecto
cd HabemusHair

# 2. Asegurar que Docker este corriendo
docker compose up -d

# 3. Activar entorno virtual de Python
cd backend
source .venv/bin/activate

# 4. Arrancar el servidor de desarrollo
uvicorn app.main:app --reload
# (--reload hace que se reinicie automaticamente cuando guardas un archivo)

# 5. Hacer cambios en el codigo...

# 6. Verificar en http://localhost:8000/docs

# 7. Guardar cambios en Git
git add archivos_que_cambiaste
git commit -m "descripcion de lo que hiciste"
git push
```

---

## Cuando algo no funciona

### "El servidor no arranca"
```bash
# Verificar que Docker este corriendo:
docker compose ps

# Si no esta corriendo:
docker compose up -d

# Ver logs del backend:
docker compose logs backend
```

### "No puedo conectar a la base de datos"
```bash
# Verificar que PostgreSQL este corriendo:
docker compose ps db

# Si no esta:
docker compose up -d db
# Esperar 5 segundos y reintentar
```

### "pip install falla"
```bash
# Asegurar que el entorno virtual esta activo:
# Deberias ver (.venv) en tu terminal

# Si no:
source .venv/bin/activate

# Luego reintentar:
pip install -r requirements.txt
```

### "Que es un error 422?"
Significa que mandaste datos en formato incorrecto. Ve a http://localhost:8000/docs y revisa que campos espera el endpoint.

---

## Proximos pasos de desarrollo

1. **Ahora:** Probar la API, familiarizarte con el codigo
2. **Despues de hablar con el medico:** Incorporar datos reales
3. **Semanas 3-4:** Conectar PostgreSQL real (reemplazar el dict en memoria)
4. **Semanas 5-8:** Implementar segmentacion con modelos de ML
5. **Semanas 9-12:** Conectar motor de grafts con la API + generar reportes PDF
