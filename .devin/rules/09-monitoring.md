---
trigger: glob
globs: ["monitoring/**/*", "**/alertmanager*", "**/prometheus*", "**/grafana*"]
description: Observability patterns — Prometheus metrics, Grafana dashboards, AlertManager rules
---

# Monitoring Rules

## Metrics Every Service MUST Export

```python
# Business metrics (not just infrastructure)
predictions_total = Counter(
    '{service}_predictions_total',
    'Total predictions',
    ['risk_level', 'model_version']
)

prediction_latency = Histogram(
    '{service}_prediction_latency_seconds',
    'Prediction latency',
    ['endpoint'],
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
)

prediction_score_distribution = Histogram(
    '{service}_prediction_score',
    'Model output score distribution',
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
)

# Drift metrics (pushed via Pushgateway from CronJob)
psi_score_per_feature = Gauge(
    '{service}_psi_score',
    'PSI drift score per feature',
    ['feature']
)

drift_detection_last_run_timestamp = Gauge(
    'drift_detection_last_run_timestamp',
    'Unix timestamp of last successful drift detection run'
)
```

## Alert Severity Levels (MANDATORY)

| Level | SLA | Action | Example |
|-------|-----|--------|---------|
| **P1** | 15 min | Immediate rollback | High error rate (>5%) |
| **P2** | 4 hours | Trigger retraining | Primary metric degraded |
| **P3** | 24 hours | Investigate + plan | Significant drift on critical feature |
| **P4** | 1 week | Document trend | Incipient drift |

## Critical Alerts

```yaml
groups:
- name: ml_sla
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 2m
    labels: {severity: P1}

  - alert: DriftDetectionHeartbeatMissing
    expr: (time() - drift_detection_last_run_timestamp) > 172800
    for: 5m
    labels: {severity: P2}
    # Detects silently broken CronJobs

  - alert: CriticalFeatureDriftHigh
    expr: '{service}_psi_score{feature="critical_feature"} > 0.20'
    for: 1h
    labels: {severity: P3}
```

## Grafana Dashboard Requirements

Every service dashboard MUST include:
- Request rate and error rate
- Latency percentiles (p50, p95, p99)
- Prediction score distribution
- PSI per feature (line chart over time)
- Model version in use
- Resource utilization (CPU, memory)

## PSI (Population Stability Index)

ALWAYS use quantile-based bins (not uniform):
```python
breakpoints = np.percentile(reference, np.linspace(0, 100, bins + 1))
```

Thresholds:
- PSI < 0.10: No significant change
- 0.10 <= PSI < 0.20: Moderate change → monitor
- PSI >= 0.20: Significant change → action required

For temporal data: use Year-over-Year comparison instead of standard PSI.

## Heartbeat Alert (MANDATORY)

Every CronJob-based process MUST have a heartbeat alert:
- Drift detection CronJob → alert if no report in 48h
- Prevents silently broken automation from going unnoticed
