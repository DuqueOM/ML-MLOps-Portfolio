# Dockerfile

**Location:** `Dockerfile`

## Purpose
Defines the container image for the application, utilizing a **multi-stage build** pattern to minimize image size and improve security.

### Stages
1.  **Builder**:
    -   Base: `python:3.13-slim`
    -   Installs compilers (gcc, g++) needed for some python packages.
    -   Creates a virtual environment at `/opt/venv`.
    -   Installs dependencies from `requirements.txt`.
2.  **Runtime**:
    -   Base: `python:3.13-slim` (clean image).
    -   Installs `curl` for healthchecks.
    -   Copies `/opt/venv` from Builder stage.
    -   Creates a non-root user `appuser` (UID 1000) for security.
    -   Copies application code.
    -   Exposes port 8000.
    -   Sets `uvicorn` as the default command (`CMD`).

## Security Features
-   **Non-root user**: Application runs as `appuser`, restricting file system access.
-   **Slim image**: Reduces attack surface by excluding unnecessary tools.
-   **Healthcheck**: Built-in `HEALTHCHECK` instruction using `curl`.

## Validation
Build and run the image:
```bash
make docker-build
make docker-run
```
