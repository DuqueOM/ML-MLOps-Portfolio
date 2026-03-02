# Troubleshooting Guide

## Quick Diagnostics

```bash
docker compose ps                    # Container status
kubectl get pods -n ml-portfolio     # K8s pod status
curl localhost:8001/health           # API health
```

## Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Container won't start | Missing model | `scripts/setup_demo_models.sh` |
| Port in use | Conflict | `lsof -i :8001` then `kill <PID>` |
| OOMKilled | Memory limit | Increase in K8s/compose resources |
| Model load fails | Wrong sklearn version | Retrain with `scripts/train_production_models.py` |
| 422 on predict | Invalid input | Check Pydantic schema, required fields |
| 500 on predict | Feature mismatch | Verify training/inference alignment |
| Slow predictions | SHAP overhead | Use `?explain=true` only when needed |
| CI tests fail locally pass | Python version | Ensure Python 3.11, check `pip freeze` |
| Coverage below threshold | Uncovered code | `pytest --cov --cov-report=html` |
| Gitleaks false positive | Non-secret string | Add to `.gitleaksignore` |
| MLflow connection refused | Not running | `kubectl port-forward svc/mlflow-service 5000:5000` |
| Docker build stuck | Cache/network | `docker builder prune -f && docker compose build --no-cache` |

## Kubernetes Debugging

```bash
kubectl describe pod <pod> -n ml-portfolio    # Pod events
kubectl logs <pod> -n ml-portfolio            # App logs
kubectl logs <pod> -c init-download-model     # Init container logs
kubectl top pods -n ml-portfolio              # Resource usage
kubectl rollout undo deployment/<svc>         # Rollback
```

## Dependency Issues

- **sklearn mismatch**: Model trained with different version → retrain
- **NumPy/Pandas**: Pin versions in `requirements.txt`
- **pip conflicts**: `pip check` and `pipdeptree` to diagnose

---

*Last Updated: March 2026*
