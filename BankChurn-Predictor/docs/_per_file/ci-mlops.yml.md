# CI/CD Pipeline (`ci-mlops.yml`)

The `.github/workflows/ci-mlops.yml` file defines the Continuous Integration and Continuous Deployment pipeline for the portfolio. It is a unified workflow that handles multiple projects.

## Jobs
1.  **Tests**: Runs `pytest` with coverage for each project matrix (BankChurn, CarVision, TelecomAI).
2.  **Security**: Scans code with `bandit` and secrets with `gitleaks`.
3.  **Docker**: Builds the Docker image and scans it for vulnerabilities using `Trivy`.
4.  **E2E**: Runs end-to-end tests (specific to BankChurn) to verify the full flow from API startup to prediction.

## Validation
The pipeline triggers automatically on push to `main` or pull requests. You can simulate parts of it locally using `make test` or `make security-scan`.
