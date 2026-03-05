# Release Management

## Versioning

[Semantic Versioning](https://semver.org/) — `MAJOR.MINOR.PATCH`

**Current**: v3.5.0 (March 2026) — Python 3.11.14, sklearn 1.8.0, LightGBM 4.6+, FinBERT, PySpark 4.1

## Release Checklist

- [ ] All tests passing, coverage >= 85% (actual: 90–98%, 294+ tests)
- [ ] Security scans clean (Gitleaks, Bandit, Trivy)
- [ ] Model metrics meet thresholds (AUC > 0.80, R² > 0.75, Acc > 0.85)
- [ ] Docker images built and pushed to Artifact Registry
- [ ] Integration tests pass
- [ ] Documentation updated

## Release Process

1. **Version bump** → Update `__init__.py`, `pyproject.toml` across projects
2. **Test** → `pytest --cov`, Docker build, integration tests
3. **Tag & push** → `git tag -a vX.Y.Z && git push --tags`
4. **Build images** → Push to Artifact Registry (`us-central1-docker.pkg.dev`)
5. **Deploy** → `kubectl rollout restart deployment -n ml-portfolio`
6. **Verify** → Health checks + smoke tests on GKE

## Rollback

```bash
kubectl rollout undo deployment/<service> -n ml-portfolio
```

## Docker Registry

Images pushed to GCP Artifact Registry:
- `us-central1-docker.pkg.dev/ml-portfolio-duque-om-202602/ml-portfolio-images/bankchurn:latest`
- `us-central1-docker.pkg.dev/ml-portfolio-duque-om-202602/ml-portfolio-images/nlpinsight:latest`
- `us-central1-docker.pkg.dev/ml-portfolio-duque-om-202602/ml-portfolio-images/chicagotaxi:latest`

## Emergency Procedures

1. **Immediate rollback**: `kubectl rollout undo deployment/<service> -n ml-portfolio`
2. **Hotfix branch** from main, fix, test, merge
3. **Post-mortem** within 24 hours

## Audit Trail

- All releases tagged in Git
- Docker images immutable in Artifact Registry
- MLflow tracks all model versions and parameters
- CI/CD logs retained for 90 days

---

*Last Updated: March 2026 — v3.5.0*
