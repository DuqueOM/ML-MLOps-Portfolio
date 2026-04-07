---
trigger: glob
globs: "**/*.py"
---

# Python & ML Conventions

## Code Style
- Type hints on ALL public functions and methods
- Pydantic BaseModel for config classes, request/response schemas
- Google-style docstrings on public functions and classes
- Use `from __future__ import annotations` for forward references
- Import order: stdlib → third-party → local (enforced by ruff)

## ML Patterns
- sklearn Pipeline for all preprocessing — no manual transform chains
- ColumnTransformer for heterogeneous feature types
- Custom transformers inherit from BaseEstimator + TransformerMixin
- Model serialization via joblib (sklearn) or model.tar.gz (FinBERT)
- SHAP: use KernelExplainer for StackingClassifier — TreeExplainer is incompatible (ADR-010)

## FastAPI Services
- Single-worker uvicorn under K8s — horizontal scaling via HPA (ADR-014)
- Async inference: `asyncio.run_in_executor` + `ThreadPoolExecutor(4)` (ADR-015)
- /health endpoint for liveness/readiness probes
- Prometheus metrics: use service-specific prefixes (bankchurn_*, nlpinsight_*, chicagotaxi_*)
- Pydantic models for request validation and response serialization

## Dependencies
- Compatible release pinning (~=) for ALL packages (ADR-005)
- numpy <2.0 — version 2.x silently corrupts joblib-serialized models
- requirements.txt or requirements.in for pip-compile

## Testing
- pytest with fixtures in conftest.py
- Minimum 80% coverage per service
- Unit tests in tests/unit/, integration in tests/integration/
- Test model predictions with known inputs/outputs
- Never use production models in CI — generate lightweight test models
