# .github/workflows/ci-mlops.yml

## Purpose
Defines the Continuous Integration (CI) pipeline for the MLOps portfolio. It ensures that changes to any project (`BankChurn`, `TelecomAI`, `CarVision`) meet quality standards before merging.

## Key Features
- **Path Filtering:** Uses `paths` triggers to run specific jobs only when relevant files change (e.g., changes in `TelecomAI` trigger TelecomAI tests).
- **Quality Gates:** Runs:
  - **Linting:** `ruff` (and `flake8` legacy) to enforce style.
  - **Type Checking:** `mypy` for static type safety.
  - **Testing:** `pytest` with coverage thresholds.
- **Automation:** Can automatically post reports (like CML) back to the PR (if configured).

## Validation
The workflow runs automatically on Push or Pull Request to `main`. You can see the status in the "Actions" tab of the GitHub repository.
