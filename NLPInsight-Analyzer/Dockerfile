# Multi-stage Dockerfile for NLPInsight Analyzer
# Optimized for transformer model inference (CPU)
# Stage 1: Builder
FROM python:3.11-slim-bookworm AS builder

LABEL maintainer="Duque Ortega Mutis (DuqueOM) <DuqueOrtegaMutis@gmail.com>"
LABEL project="NLPInsight-Analyzer"

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

# Install dependencies in venv (CPU-only torch to keep image small)
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    if [ -f requirements.in ]; then \
        sed -e '/--hash=/d' -e 's/ \\$//' -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' -e '/^torch/d' requirements.in > requirements_clean.txt; \
    else \
        sed -e '/--hash=/d' -e 's/ \\$//' -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' -e '/^torch/d' requirements.txt > requirements_clean.txt; \
    fi && \
    pip install --no-cache-dir -r requirements_clean.txt

# Stage 2: Runtime
FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    MODEL_PATH=models \
    TRANSFORMERS_CACHE=/app/.cache/huggingface

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

# Copy configs first (change less frequently, better cache)
COPY --chown=appuser:appuser configs/ ./configs/
COPY --chown=appuser:appuser pyproject.toml ./

# Copy source code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser app/ ./app/

# Create directories
RUN mkdir -p logs models artifacts data/raw .cache/huggingface && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (API)
CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
