# Multi-stage Dockerfile for NLPInsight Analyzer
# Optimized for transformer model inference (CPU)
#
# Build context is the REPOSITORY ROOT (ADR-019):
#     docker build -f NLPInsight-Analyzer/Dockerfile .
# Installs from the workspace lock (uv.lock), the resolution CI and development
# use; torch is the CPU wheel from download.pytorch.org (root pyproject
# [tool.uv.sources]). Dockerfile.dockerignore whitelists the root context.

# Stage 1: Builder
FROM python:3.13.15-slim-bookworm AS builder

LABEL maintainer="Duque Ortega Mutis (DuqueOM) <DuqueOrtegaMutis@gmail.com>"
LABEL project="NLPInsight-Analyzer"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON=/usr/local/bin/python3 \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    UV_HTTP_RETRIES=5

# uv, pinned to the version that wrote uv.lock
COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /usr/local/bin/uv

WORKDIR /build

# Install build dependencies (curl: the torch fallback below)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Workspace metadata only (uv validates the whole workspace)
COPY pyproject.toml uv.lock ./
COPY BankChurn-Predictor/pyproject.toml BankChurn-Predictor/
COPY ChicagoTaxi-Demand-Pipeline/pyproject.toml ChicagoTaxi-Demand-Pipeline/
COPY NLPInsight-Analyzer/pyproject.toml NLPInsight-Analyzer/
COPY common_utils/pyproject.toml common_utils/
COPY NLPInsight-Analyzer/docker/fetch_locked_wheel.py /tmp/fetch_locked_wheel.py

# Exactly this service's locked runtime dependencies (--frozen never
# re-resolves). torch via pip/urllib3 has been observed to fail the TLS
# handshake against download.pytorch.org's CDN edge from GitHub-hosted runners
# while curl, against the same URL, succeeds — the two clients build a
# different ClientHello. uv uses yet another TLS stack and is tried first. If
# it fails, everything else is installed with uv and torch is fetched with curl
# from the URL uv.lock records, verified against the lock's sha256 — the same
# file, or the build fails. (The old fallback scraped the index for the newest
# wheel: a version nobody had locked.)
RUN ( uv sync --frozen --no-dev --package nlpinsight-analyzer --no-install-workspace \
      || ( echo "uv could not fetch from download.pytorch.org - installing the locked torch wheel with curl" && \
           uv sync --frozen --no-dev --package nlpinsight-analyzer --no-install-workspace --no-install-package torch && \
           WHL=$(python3 /tmp/fetch_locked_wheel.py uv.lock torch /tmp/wheels) && \
           uv pip install --python /opt/venv/bin/python --no-deps "$WHL" && \
           rm -rf /tmp/wheels \
         ) \
    ) && \
    find /opt/venv -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null; \
    find /opt/venv -type d -name 'tests' -not -path '*/numpy/*' -exec rm -rf {} + 2>/dev/null; \
    find /opt/venv -type d -name 'test' -exec rm -rf {} + 2>/dev/null; \
    find /opt/venv -type f -name '*.pyc' -delete 2>/dev/null; \
    find /opt/venv -type f -name '*.pyo' -delete 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/torch/test 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/torch/include 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/torch/share 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/torch/_inductor 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/torch/_dynamo 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/caffe2 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/pip 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/setuptools 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/wheel 2>/dev/null; \
    /opt/venv/bin/python -c "import fastapi, uvicorn, torch"

# Stage 2: Runtime
FROM python:3.13.15-slim-bookworm AS runtime

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
COPY --chown=appuser:appuser NLPInsight-Analyzer/configs/ ./configs/
COPY --chown=appuser:appuser NLPInsight-Analyzer/pyproject.toml ./

# Copy source code
COPY --chown=appuser:appuser NLPInsight-Analyzer/src/ ./src/
COPY --chown=appuser:appuser NLPInsight-Analyzer/app/ ./app/

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
