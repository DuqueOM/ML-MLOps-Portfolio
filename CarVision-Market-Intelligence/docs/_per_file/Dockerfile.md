# Dockerfile

**Location:** `Dockerfile`

## Purpose
Defines the container image for the CarVision application. It uses a multi-stage build process to optimize image size and security.

## Stages
1.  **Builder**:
    -   Base: `python:3.11-slim`
    -   Installs system dependencies (gcc) and Python packages.
    -   Creates virtual environment.
2.  **Runtime**:
    -   Base: `python:3.11-slim`
    -   Copies virtual environment from Builder.
    -   Copies source code.
    -   Runs as non-root `appuser`.

## Security Features
-   **Non-root execution**: Reduces attack surface.
-   **Slim base image**: Minimizes vulnerabilities.
-   **No build tools**: Compilers are only present in the builder stage.

## Validation
Build and run the image to verify startup:
```bash
docker build -t carvision:test .
docker run --rm carvision:test python -c "import src.carvision"
```
