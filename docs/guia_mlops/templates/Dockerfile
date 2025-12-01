# ════════════════════════════════════════════════════════════════════════════════
# DOCKERFILE - ML Model Serving
# Multi-stage build optimizado para modelos ML
# ════════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder
# ─────────────────────────────────────────────────────────────────────────────────
FROM python:3.10-slim as builder

WORKDIR /app

# Instalar dependencias de sistema para compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear virtualenv para aislar dependencias
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────────
# Stage 2: Runtime
# ─────────────────────────────────────────────────────────────────────────────────
FROM python:3.10-slim as runtime

WORKDIR /app

# Copiar virtualenv del builder (reduce tamaño significativamente)
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar código fuente
COPY src/ ./src/
COPY models/ ./models/
COPY configs/ ./configs/

# Crear usuario no-root por seguridad
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Variables de entorno
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MODEL_PATH=/app/models/model.pkl \
    CONFIG_PATH=/app/configs/default.yaml

# Puerto de la API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicio
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ─────────────────────────────────────────────────────────────────────────────────
# Notas de uso:
# ─────────────────────────────────────────────────────────────────────────────────
# Build:
#   docker build -t ml-model:latest .
#
# Run:
#   docker run -p 8000:8000 ml-model:latest
#
# Run con volumen para modelos:
#   docker run -p 8000:8000 -v $(pwd)/models:/app/models ml-model:latest
#
# Run con variables de entorno:
#   docker run -p 8000:8000 -e MODEL_PATH=/app/models/v2.pkl ml-model:latest
#
# Verificar tamaño:
#   docker images ml-model:latest
#   # Target: < 500MB
# ─────────────────────────────────────────────────────────────────────────────────
