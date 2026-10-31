# Multi-stage Dockerfile for BankChurn Predictor
# Optimized for minimal image size (~600MB target)
#
# Build context is the REPOSITORY ROOT (ADR-019):
#     docker build -f BankChurn-Predictor/Dockerfile .
# The image installs from the workspace lock (uv.lock) — the same resolution CI
# and development use — so the versions that train a model are the versions
# that serve it. Dockerfile.dockerignore (next to this file) whitelists what
# the root context may send.

# Stage 1: Builder
FROM python:3.13.15-slim-bookworm AS builder

LABEL maintainer="DuqueOM <DuqueOrtegaMutis@gmail.com>" \
      version="3.0.0" \
      description="BankChurn Predictor — Bank customer churn prediction API"

# Build environment variables. uv installs into /opt/venv with the image's own
# interpreter and never downloads one.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON=/usr/local/bin/python3 \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1

# uv, pinned to the version that wrote uv.lock
COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /usr/local/bin/uv

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Workspace metadata only: the root project, the lock, and every member's
# pyproject.toml (uv validates the whole workspace). No source is needed to
# install dependencies.
COPY pyproject.toml uv.lock ./
COPY BankChurn-Predictor/pyproject.toml BankChurn-Predictor/
COPY ChicagoTaxi-Demand-Pipeline/pyproject.toml ChicagoTaxi-Demand-Pipeline/
COPY NLPInsight-Analyzer/pyproject.toml NLPInsight-Analyzer/
COPY common_utils/pyproject.toml common_utils/

# Exactly this service's locked runtime dependencies: no dev tools, no
# training groups, no other service. --frozen fails instead of re-resolving.
# xgboost-cpu (pyproject) keeps nvidia-nccl-cu12 (~290MB) out, which the old
# `pip install --no-deps` did by hand.
RUN uv sync --frozen --no-dev --package bankchurn-predictor --no-install-workspace && \
    find /opt/venv -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null; \
    find /opt/venv -type d -name 'tests' -not -path '*/numpy/*' -exec rm -rf {} + 2>/dev/null; \
    find /opt/venv -type f -name '*.pyc' -delete 2>/dev/null; \
    find /opt/venv -type f -name '*.pyo' -delete 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/scipy/datasets 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/pandas/tests 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/pip 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/setuptools 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/wheel 2>/dev/null; \
    /opt/venv/bin/python -c "import fastapi, uvicorn, xgboost, lightgbm"

# Stage 2: Runtime — Lightweight final image
FROM python:3.13.15-slim-bookworm AS runtime

# Runtime environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV PATH="/opt/venv/bin:$PATH"
ENV MODEL_PATH=models/model.joblib

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser --gid=1000 && \
    useradd -r -g appuser --uid=1000 --home-dir=/app appuser

WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy configs first (change less frequently, better cache)
COPY --chown=appuser:appuser BankChurn-Predictor/configs/ ./configs/
COPY --chown=appuser:appuser BankChurn-Predictor/pyproject.toml ./

# Copy source code (changes more frequently)
COPY --chown=appuser:appuser BankChurn-Predictor/src/ ./src/
COPY --chown=appuser:appuser BankChurn-Predictor/app/ ./app/
COPY --chown=appuser:appuser BankChurn-Predictor/monitoring/ ./monitoring/

# Create required directories
RUN mkdir -p logs data/raw data/processed models results && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (API)
CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
