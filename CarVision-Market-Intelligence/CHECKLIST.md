# Acceptance Checklist

Before merging any changes to `main`, ensure the following checks pass:

## Code Quality
- [ ] **Linting**: `flake8` and `ruff` pass without errors.
- [ ] **Formatting**: Code is formatted with `black` or `isort`.
- [ ] **Type Checking**: `mypy` scan reports no critical errors.

## Testing
- [ ] **Unit Tests**: `pytest tests/` passes (100% success).
- [ ] **Coverage**: Project coverage is > 75%.
- [ ] **Integration**: `make start-demo` runs locally without crashing.

## Security
- [ ] **Secrets**: No API keys or credentials hardcoded (check with `gitleaks`).
- [ ] **Dependencies**: No known vulnerabilities in `requirements.txt` (check with `safety check`).
- [ ] **Docker**: Image runs as non-root user.

## Documentation
- [ ] **README**: Updated with new features or env vars.
- [ ] **Architecture**: `ARCHITECTURE.md` reflects system design changes.
- [ ] **Docstrings**: Public functions/classes have docstrings.

## Artifacts
- [ ] **Reproducibility**: `dvc repro` runs successfully from scratch.
- [ ] **Model Registry**: Training run logged to MLflow.
