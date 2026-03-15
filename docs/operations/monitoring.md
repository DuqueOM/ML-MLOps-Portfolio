# Monitoring Guide

Prometheus + Grafana + MLflow + Evidently monitoring stack deployed on GKE + EKS (both clouds).

![Grafana Dashboard](../media/screenshots/monitoring/34-grafana-dashboard.png)

## Stack

| Component | Purpose | Access |
|-----------|---------|--------|
| **Prometheus** | Metrics collection (15s scrape) | `:9090` |
| **Grafana** | Auto-provisioned 26-panel dashboard (6 rows) | `:3000` |
| **MLflow** | Experiment tracking (9 runs, 3 projects) | `:5000` |
| **Evidently** | Data drift detection (PSI/KS) | All 3 projects |

## Prometheus Metrics

All APIs expose `/metrics`. Key metrics per service:

| Metric | BankChurn | NLPInsight | ChicagoTaxi |
|--------|-----------|------------|-------------|
| `{svc}_requests_total` | `bankchurn_requests_total` | `nlpinsight_requests_total` | `chicagotaxi_requests_total` |
| `{svc}_predictions_total` | `{risk_level}` label | `{sentiment}` label | `{demand_category}` label |
| `{svc}_request_*_seconds` | `_duration_seconds` (histogram) | `_duration_seconds` (histogram) | `_latency_seconds` (histogram) |

### Real Production Counters (measured 2026-03-11, post load-test)

| Service | Total Requests | Predictions (breakdown) |
|---------|---------------|-------------------------|
| BankChurn | 416 | HIGH=211 · MEDIUM=100 · LOW=105 |
| NLPInsight | 919 | neutral=1110 · negative=449 · positive=212 |
| ChicagoTaxi | 225 | 1709 demand predictions across all categories |

![Prometheus Targets](../media/screenshots/monitoring/37-prometheus-targets-up.png)

## MLflow Experiments (v3.5.3)

| Experiment | Best Run | Key Metric |
|------------|----------|------------|
| **BankChurn** | StackingClassifier (RF+GB+XGB+LGB→LR) | AUC 0.87 |
| **NLPInsight** | TF-IDF + LogReg (prod) / FinBERT (GPU) | Acc 80.6% |

![MLflow Experiments](../media/screenshots/monitoring/39-mlflow-experiments.png)

### MLflow Run Comparison — BankChurn Model Selection

Parallel coordinates plot comparing 5 model runs (StackingClassifier, RandomForest, LogisticRegression, GradientBoosting) across hyperparameters and metrics. This visualization drove the selection of StackingClassifier as the production model (highest `roc_auc` at 0.86).

![MLflow Model Comparison](../media/screenshots/monitoring/55-mlflow-xgboost-comparison.png)

| ML Dashboard Panels | Load Test Results | P95 Latency |
|:---:|:---:|:---:|
| ![ML Panels](../media/screenshots/monitoring/34b-grafana-dashboard-ml-panels.png) | ![Load Test](../media/screenshots/monitoring/38c-load-test-results.png) | ![P95](../media/screenshots/monitoring/75-prometheus-latency-p95.png) |

## SLOs

| Service | Availability | P95 Latency (in-pod) | P95 Latency (via ingress) | Error Rate |
|---------|--------------|---------------------|--------------------------|------------|
| BankChurn | 99.9% | 111ms | 481ms | <1% |
| NLPInsight | 99.9% | 15ms | 9.6ms | <1% |
| ChicagoTaxi | 99.9% | 460ms | 35.5ms | <1% |

> **Load test baseline** (2026-03-11): 2673 requests · 30 users · 120s · **0.07% error rate** · 22.35 req/s aggregate throughput.
> Locust per-endpoint P50/P95: BankChurn predict 770ms/1700ms · NLPInsight predict 80ms/160ms · ChicagoTaxi demand 90ms/170ms.

## HPA Autoscaling

CPU-only scaling (memory is fixed for ML models loaded at startup):

| Service | CPU Target | Min/Max Pods | Memory (real) |
|---------|-----------|--------------|---------------|
| BankChurn | 70% | 1–3 | ~344Mi |
| NLPInsight | 70% | 1–3 | ~283Mi |
| ChicagoTaxi | 70% | 1–3 | ~431Mi |

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

*Last Updated: March 2026 — v3.5.3*
