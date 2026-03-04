# Multi-stage Dockerfile for ChicagoTaxi Demand Pipeline
# Serves pre-computed batch predictions via FastAPI
# PySpark ETL runs as a separate K8s Job (not in this image)
# Stage 1: Builder
FROM python:3.11-slim-bookworm AS builder

LABEL maintainer="DuqueOM <DuqueOrtegaMutis@gmail.com>" \
      version="1.0.0" \
      description="ChicagoTaxi Demand Pipeline — Batch demand prediction API"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

COPY requirements-prod.txt ./

RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements-prod.txt && \
    find /opt/venv -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null; \
    find /opt/venv -type d -name 'tests' -exec rm -rf {} + 2>/dev/null; \
    find /opt/venv -type d -name 'test' -exec rm -rf {} + 2>/dev/null; \
    find /opt/venv -type f -name '*.pyc' -delete 2>/dev/null; \
    find /opt/venv -name '*.so' -exec strip --strip-unneeded {} + 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/pip 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/setuptools 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/wheel 2>/dev/null; \
    true

# Stage 2: Runtime
FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    MODEL_PATH="/app/models/model.joblib" \
    PREDICTIONS_PATH="/app/data/processed/taxi_predictions"

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY app/ ./app/
COPY configs/ ./configs/
COPY src/ ./src/

# Create directories for mounted volumes
RUN mkdir -p /app/models /app/data/processed/taxi_predictions && \
    useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
