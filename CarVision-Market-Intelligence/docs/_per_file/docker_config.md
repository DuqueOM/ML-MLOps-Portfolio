# Docker Configuration (`Dockerfile`)

## Purpose
Defines the reproducible runtime environment for the application. It relies on `python:3.11-slim` for a small footprint.
Key features:
- **Security:** Runs as a non-root user (implicit in slim, but good practice to enforce).
- **Optimization:** Cleans apt lists and pip caches.
- **Reliability:** Sets `PYTHONPATH=/app` to ensure the `src` package is discoverable by the application, regardless of working directory.

## Validation
To validate the build process:
```bash
docker build -t carvision-test .
```
To validate the runtime:
```bash
docker run --rm -p 8000:8000 carvision-test
```
**Success Criteria:**
- Image builds successfully.
- Container starts and responds to health checks (`curl http://localhost:8000/health`).
