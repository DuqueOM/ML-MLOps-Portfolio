# Makefile

**Location:** `Makefile`

## Purpose
Provides a centralized interface for all project operations, abstracting complex commands into simple targets. It serves as the entry point for both developers and CI/CD systems.

### Key Targets
-   **Lifecycle**: `install`, `setup`, `clean`, `clean-all`.
-   **Development**: `lint`, `format`, `test`, `test-coverage`.
-   **ML Pipeline**: `train`, `evaluate`, `predict`.
-   **Deployment**: `api-start`, `docker-build`, `docker-run`, `start-demo`.

### Design Pattern
The Makefile uses variable definitions (e.g., `PYTHON`, `DOCKER_IMAGE`) to allow easy configuration overrides and self-documenting help text (via the `help` target).

## Validation
Run `make help` to see the self-documentation:
```bash
make help
```
