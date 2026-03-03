# Multi-stage Dockerfile for CarVision Market Intelligence
# Stage 1: Builder
FROM python:3.11-slim-bookworm AS builder

# Metadata
LABEL maintainer="Duque Ortega Mutis (DuqueOM) <DuqueOrtegaMutis@gmail.com>"
LABEL project="CarVision-Market-Intelligence"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy production requirements (inference only — no streamlit/plotly/pyarrow)
COPY requirements-prod.txt ./

# Install deps in venv; lightgbm --no-deps avoids unnecessary CUDA deps
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --no-compile -r requirements-prod.txt && \
    pip install --no-cache-dir --no-deps "lightgbm>=4.0.0,<5.0" && \
    find /opt/venv -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null; \
    find /opt/venv -type d -name 'tests' -exec rm -rf {} + 2>/dev/null; \
    find /opt/venv -type f -name '*.pyc' -delete 2>/dev/null; \
    find /opt/venv -type f -name '*.pyo' -delete 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/pip 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/setuptools 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/wheel 2>/dev/null; \
    true

# Stage 2: Runtime
FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    # CarVision specific env vars
    MODEL_PATH=models/model.joblib \
    ARTIFACTS_DIR=artifacts

# Install runtime dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r appuser --gid=1000 && \
    useradd -r -g appuser --uid=1000 --home-dir=/app appuser

WORKDIR /app

# Copy venv from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy configs first (change less frequently, better cache)
COPY --chown=appuser:appuser configs/ ./configs/
COPY --chown=appuser:appuser pyproject.toml ./

# Copy source code (changes more frequently)
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser monitoring/ ./monitoring/
COPY --chown=appuser:appuser main.py ./

# Create directories (artifacts populated at runtime by download-metrics init container)
RUN mkdir -p logs data/raw data/processed models artifacts && \
    chown -R appuser:appuser /app

USER appuser

# Expose FastAPI and Streamlit ports
EXPOSE 8000
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (API)
CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
