---
trigger: glob
globs: ["**/Dockerfile*", "docker-compose*.yml", "docker-compose*.yaml"]
description: Docker patterns for ML services — multi-stage builds, no embedded models
---

# Docker Rules

## Dockerfile Template

```dockerfile
FROM python:3.11-slim AS base

WORKDIR /app

# System dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY src/ src/

# Non-root user
RUN useradd -m -u 1000 appuser
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Single worker — K8s HPA manages scale
CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]
```

## Rules

### NEVER include in Docker image:
- Model artifacts (`models/`) — downloaded via init container
- Raw data (`data/raw/`) — stored in GCS/S3
- Test files (`tests/`) — not needed in production
- `.git/` directory
- Secrets or credentials

### ALWAYS include:
- `.dockerignore` excluding: `models/`, `data/raw/`, `*.pyc`, `__pycache__`, `tests/`, `.git/`
- `HEALTHCHECK` instruction
- Non-root `USER`
- `--no-cache-dir` on pip install
- Single `CMD` with uvicorn (no `--workers`)

### Image Tagging:
- Tags are IMMUTABLE — never overwrite an existing tag
- Use semantic versioning: `v1.2.3`
- Always tag with git commit SHA as well: `sha-abc1234`

### Multi-stage builds (when needed):
```dockerfile
FROM python:3.11-slim AS builder
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/deps -r requirements.txt

FROM python:3.11-slim AS runtime
COPY --from=builder /deps /usr/local/lib/python3.11/site-packages
COPY app/ app/
COPY src/ src/
```

### Security:
- Scan with `trivy` in CI before pushing
- Pin base image to specific digest when possible
- No `apt-get install` without `--no-install-recommends`
- Remove build tools in same RUN layer if used
