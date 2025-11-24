# Dockerfile

The `Dockerfile` defines the container image for the BankChurn Predictor service. It uses a multi-stage build process to optimize image size and security.

## Stages
1.  **Builder Stage**: Uses `python:3.12-slim` to install build dependencies and compile Python packages.
2.  **Runtime Stage**: Copies only the installed packages and necessary source code to a clean slim image.
3.  **Security**: Creates a non-root user (`appuser`) to run the application, following container security best practices.

## Validation
To verify the Docker build process:

```bash
docker build -t bankchurn:test .
```

To run the container and check if it starts correctly:

```bash
docker run --rm -p 8000:8000 bankchurn:test
```

Then access `http://localhost:8000/health` to confirm the service is up.
