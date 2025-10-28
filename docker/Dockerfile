FROM python:3.11-slim

WORKDIR /app

# Copiar solo lo necesario
COPY ../code ./code
COPY ../tests ./tests
COPY ../logs ./logs
COPY ../README.md .

# Copiar requirements.txt si existe
COPY ../requirements.txt ./requirements.txt

# Instalar dependencias
# - Se instalan dependencias del archivo si existe
# - Se aseguran FastAPI, Uvicorn, Redis y Pytest siempre presentes
RUN pip install --no-cache-dir --upgrade pip && \
    (pip install --no-cache-dir -r requirements.txt || true) && \
    pip install --no-cache-dir fastapi uvicorn redis pytest

# Exponer el puerto del API
EXPOSE 8000

# Comando por defecto
CMD ["bash"]

