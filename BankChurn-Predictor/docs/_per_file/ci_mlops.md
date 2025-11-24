# ci-mlops.yml

**Location:** `.github/workflows/ci-mlops.yml`

## Purpose
Defines the Continuous Integration (CI) pipeline for the project, ensuring that every change to the `main` branch or Pull Request is verified.

### Steps
1.  **Checkout**: Retrieves code from GitHub.
2.  **Setup Python**: Installs Python 3.13.
3.  **Install Dependencies**: Installs `requirements.txt` and dev tools (`pytest`, `black`, `flake8`).
4.  **Linting**:
    -   `flake8`: Checks for syntax errors and style violations.
    -   `black`: Verifies code formatting.
    -   `mypy`: Static type checking.
5.  **Testing**: Runs `pytest` with coverage reporting.
6.  **Build Verification**: Attempts to build the Docker image to ensure the `Dockerfile` is valid.

## Validation
This workflow runs automatically on GitHub. To simulate it locally:
```bash
make lint
make test
make docker-build
```
