# Acceptance Checklist

Before merging any changes to `main`, ensure the following checks pass:

## Code Quality
- [ ] **Linting**: `flake8` and `ruff` pass without errors.
- [ ] **Formatting**: Code is formatted with `black` and `isort`.
- [ ] **Type Checking**: `mypy` scan reports no critical errors.

## Testing
- [ ] **Unit Tests**: `pytest tests/` passes (100% success).
- [ ] **Coverage**: Project coverage is > 70%.
- [ ] **Integration**: `make start-demo` runs locally without crashing.

## Security
- [ ] **Secrets**: No API keys or credentials hardcoded (check with `gitleaks`).
- [ ] **Dependencies**: No known vulnerabilities in `requirements.txt` (check with `safety check`).
- [ ] **Docker**: Image runs as non-root user.

## Documentation
- [ ] **README**: Updated with new features or env vars.
- [ ] **Architecture**: `ARCHITECTURE.md` reflects system design changes.
- [ ] **Model Card**: `model_card.md` updated if model changed.
- [ ] **Docstrings**: Public functions/classes have docstrings.

## Artifacts
- [ ] **Reproducibility**: `dvc repro` runs successfully from scratch (or `make train`).
- [ ] **Model Registry**: Training run logged to MLflow (`make mlflow-demo`).

## API
- [ ] **Health Check**: `/health` endpoint responds correctly.
- [ ] **Predict**: `/predict` endpoint returns valid predictions.
- [ ] **Validation**: Input validation catches invalid data gracefully.
