# Dockerfile

## Purpose
Defines the reproducible runtime environment for the application. It builds a lightweight, secure image based on `python:3.11-slim`.

## Key Features
- **Security:** Creates and switches to a non-root user (`appuser`) to prevent privilege escalation attacks.
- **Optimization:** Installs dependencies with `--no-cache-dir` to keep image size down.
- **Performance:** Uses a `.dockerignore` file to exclude unnecessary build artifacts (like `.venv` or `__pycache__`) from the build context.

## Validation
Build the image and verify the user:
```bash
docker build -t telecomai .
docker run --rm telecomai whoami
# Expected output: appuser
```
