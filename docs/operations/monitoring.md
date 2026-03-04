# Monitoring Guide

Prometheus + Grafana + MLflow + Evidently monitoring stack deployed on GKE.

![Grafana Dashboard](../media/screenshots/monitoring/34-grafana-dashboard.png)

## Stack

| Component | Purpose | Access |
|-----------|---------|--------|
| **Prometheus** | Metrics collection (15s scrape) | `:9090` |
| **Grafana** | Auto-provisioned 10-panel dashboard | `:3000` |
| **MLflow** | Experiment tracking (9 runs, 3 projects) | `:5000` |
| **Evidently** | Data drift detection (PSI/KS) | All 3 projects |

## Prometheus Metrics

All APIs expose `/metrics`. Key metrics per service:

- `{service}_requests_total` — Counter: total HTTP requests
- `{service}_predictions_total` — Counter: predictions made
- `{service}_request_duration_seconds` — Histogram: latency

![Prometheus Targets](../media/screenshots/monitoring/37-prometheus-targets-up.png)

## MLflow Experiments (v3.0.0)

| Experiment | Best Run | Key Metric |
|------------|----------|------------|
| **BankChurn** | StackingClassifier (RF+GB+XGB+LGB→LR) | AUC 0.87 |
| **CarVision** | LightGBM + FeatureEngineer (24 features) | R² 0.80 |
| **NLPInsight** | FinBERT (ProsusAI) | Acc 97% |

![MLflow Experiments](../media/screenshots/monitoring/39-mlflow-experiments.png)

## SLOs

| Service | Availability | P95 Latency | Error Rate |
|---------|--------------|-------------|------------|
| BankChurn | 99.9% | <250ms | <1% |
| CarVision | 99.5% | <500ms | <2% |
| NLPInsight | 99.9% | <250ms | <1% |

## HPA Autoscaling

CPU-only scaling (memory is fixed for ML models loaded at startup):

| Service | CPU Target | Min/Max Pods | Memory |
|---------|-----------|--------------|--------|
| BankChurn | 70% | 1–3 | ~300Mi |
| CarVision | 70% | 1–3 | ~550Mi |
| NLPInsight | 75% | 1–3 | ~650Mi |

## Testing

```bash
pytest tests/integration/test_smoke_k8s.py -v    # Smoke tests
locust -f tests/load/locustfile.py --headless     # Load tests
```

## Runbook

- **High errors**: Check `/health`, review logs (`kubectl logs`), verify model loaded
- **High latency**: Scale up (`kubectl scale`), check concurrent requests
- **Service down**: Check pod status, resource limits (OOM), restart count

---

*Last Updated: March 2026 — v3.3.1*
