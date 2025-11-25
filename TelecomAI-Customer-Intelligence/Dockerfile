# Multi-stage Dockerfile for TelecomAI Customer Intelligence
# Stage 1: Builder
FROM python:3.14-slim AS builder

# Metadata
LABEL maintainer="Daniel Duque <daniel.duque@example.com>"
LABEL project="TelecomAI-Customer-Intelligence"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements.in* ./

# Install dependencies in venv
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    # If requirements.in exists, we try to use it (cleaning it first), else use requirements.txt
    if [ -f requirements.in ]; then \
        sed -e '/--hash=/d' -e 's/ \\$//' -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' requirements.in > requirements_clean.txt; \
    else \
        sed -e '/--hash=/d' -e 's/ \\$//' -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' requirements.txt > requirements_clean.txt; \
    fi && \
    pip install --no-cache-dir -r requirements_clean.txt

# Stage 2: Runtime
FROM python:3.14-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    # TelecomAI specific env vars
    MODEL_PATH=artifacts/model.joblib

# Install runtime dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r appuser --gid=1000 && \
    useradd -r -g appuser --uid=1000 --home-dir=/app appuser

WORKDIR /app

# Copy venv from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy source code
COPY --chown=appuser:appuser . .

# Create directories
RUN mkdir -p logs data/raw data/processed models artifacts && \
    chown -R appuser:appuser /app

USER appuser

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (API)
CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
