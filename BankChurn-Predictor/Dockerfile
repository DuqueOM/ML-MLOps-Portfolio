# Multi-stage Dockerfile para BankChurn Predictor
# Stage 1: Builder - Compila dependencias
FROM python:3.11-slim-bookworm AS builder

# Metadatos
LABEL maintainer="Duque Ortega Mutis (DuqueOM) <DuqueOrtegaMutis@gmail.com>"
LABEL version="1.0.0"
LABEL description="BankChurn Predictor - Sistema de predicción de abandono de clientes bancarios"

# Variables de entorno de build
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Instalar build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements de producción (sin jupyter, dev tools, torch/CUDA)
COPY requirements-prod.txt ./

# Instalar dependencias en un virtualenv
# xgboost se instala con --no-deps para evitar nvidia-nccl-cu12 (~290MB)
# sus deps reales (numpy, scipy) ya están en requirements-prod.txt
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements-prod.txt && \
    pip install --no-cache-dir --no-deps "xgboost>=1.5.0,<3.0" && \
    pip install --no-cache-dir --no-deps "shap>=0.42.0"

# Stage 2: Runtime - Imagen final ligera
FROM python:3.11-slim-bookworm AS runtime

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV PATH="/opt/venv/bin:$PATH"
ENV MODEL_PATH=models/model.joblib

# Instalar solo runtime dependencies mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no-root para seguridad
RUN groupadd -r appuser --gid=1000 && \
    useradd -r -g appuser --uid=1000 --home-dir=/app appuser

WORKDIR /app

# Copiar virtualenv desde builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Instalar uvicorn en runtime (pequeño, no afecta cache)
RUN . /opt/venv/bin/activate && pip install --no-cache-dir "uvicorn>=0.18.0"

# Copiar configs primero (cambian menos, mejor cache)
COPY --chown=appuser:appuser configs/ ./configs/
COPY --chown=appuser:appuser pyproject.toml ./

# Copiar código fuente (cambia más frecuentemente)
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser monitoring/ ./monitoring/

# Crear directorios necesarios con permisos correctos
RUN mkdir -p logs data/raw data/processed models results && \
    chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check mejorado
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto (API)
CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
