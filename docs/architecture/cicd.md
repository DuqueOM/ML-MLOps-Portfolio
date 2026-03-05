# CI/CD Pipeline

GitHub Actions workflows for testing, building, and deploying the ML-MLOps Portfolio.

## Workflows

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| **Main CI** | `ci-mlops.yml` | Push/PR to main | Tests, security, Docker, integration |
| **Docs** | `docs.yml` | Push to docs/ | Build and deploy GitHub Pages |
| **CML Training** | `cml-training-comparison.yml` | Manual | Model comparison reports |

## Main Pipeline (`ci-mlops.yml`)

**10 jobs**: tests → security → docker → integration-test → integration-report → validate-docs

### Matrix Strategy

```yaml
matrix:
  project: [BankChurn-Predictor, NLPInsight-Analyzer]
  python-version: ['3.11', '3.12']
```

6 parallel test jobs (3 projects × 2 Python versions). ChicagoTaxi included in matrix.

### Jobs

| Job | Tools | Purpose |
|-----|-------|---------|
| **tests** | pytest, flake8, black, isort, mypy | Unit tests + linting + coverage |
| **security** | Gitleaks, Bandit | Secret detection + Python security |
| **docker** | Docker, Trivy | Multi-stage build + vulnerability scan |
| **integration-test** | docker-compose, pytest | Full-stack E2E validation |

### Caching

- **pip**: `actions/setup-python` with `cache: 'pip'`
- **Docker layers**: `docker/build-push-action` with GHA cache

## Pipeline Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Build Time | <10 min | ~8 min |
| Test Coverage | >85% | 90–98% (294+ tests) |
| Security | 0 critical | Pass |

## Local CI

```bash
pre-commit run --all-files    # Lint + format + security
pytest tests/ -v --cov        # Tests + coverage
```

---

*Last Updated: March 2026 — v3.5.0*
