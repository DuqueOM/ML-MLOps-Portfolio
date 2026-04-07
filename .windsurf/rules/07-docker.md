---
trigger: glob
globs: "**/Dockerfile*,**/docker-compose*.yml,**/docker-compose*.yaml"
---

# Docker Conventions

## Dockerfile Structure
- Multi-stage builds: builder stage (install deps) → production stage (copy artifacts)
- Base image: `python:3.11-slim` for ML services
- Non-root USER in production stage
- HEALTHCHECK with curl to /health endpoint
- COPY requirements first (layer caching), then app code
- No COPY of secrets, .env files, or model artifacts into image

## Build Patterns
- Pin base image tags (never use `latest`)
- Use `.dockerignore` to exclude: `.git/`, `__pycache__/`, `*.pyc`, `models/`, `.env`
- Set `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1`
- Install only production dependencies (no dev/test packages)

## Model Loading
- Models downloaded at runtime from GCS/S3 via init container or startup script
- Never bake model artifacts into Docker images (ADR-002)
- Use emptyDir volume mount for model storage in K8s pods

## Security
- Run as non-root user (UID 1000)
- No `--privileged` flag
- Scan images with `trivy` or `grype` in CI
- Use `COPY --chown=appuser:appuser` instead of chmod after copy

## docker-compose (Development Only)
- Used for local development and integration testing
- Expose ports only on 127.0.0.1 for local services
- Use named volumes for persistent data (models, databases)
- Include health checks matching K8s liveness probes

## Registry
- GCP: `us-central1-docker.pkg.dev/ml-portfolio-duque-om-202602/ml-portfolio-images/`
- AWS: `<account-id>.dkr.ecr.us-east-1.amazonaws.com/`
- Tag format: `<service-name>:v<semver>` (e.g., `bankchurn-predictor:v3.0.0`)
