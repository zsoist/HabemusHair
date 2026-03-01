# ============================================================
# DOCKERFILE DEL BACKEND
# ============================================================
#
# QUE ES UN DOCKERFILE:
# Es una "receta" para crear un contenedor Docker.
# Piensa en ello como instrucciones paso a paso para
# preparar un computador nuevo que corra tu backend.
#
# COMO FUNCIONA:
# 1. Empieza con una imagen base (Python 3.12)
# 2. Instala las dependencias
# 3. Copia el codigo
# 4. Arranca el servidor
# ============================================================

FROM python:3.12-slim

# Instalar dependencias del sistema operativo que necesita WeasyPrint (para PDFs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el codigo del backend
COPY . .

# Puerto que expone el servidor
EXPOSE 8000

# Comando para arrancar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
