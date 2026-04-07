---
name: drift-detection
description: Configures and troubleshoots PSI-based data drift detection for ML models, including CronJob setup, threshold tuning, and alert integration with GitHub Actions retraining.
---

## What is Drift Detection?

Data drift occurs when the statistical distribution of input features changes over time, degrading model performance. This project uses **Population Stability Index (PSI)** to detect drift.

## PSI Thresholds

See `psi-thresholds.md` in this skill directory for detailed threshold guidance.

| PSI Value | Interpretation | Action |
|-----------|---------------|--------|
| < 0.1 | No significant drift | No action needed |
| 0.1 - 0.25 | Moderate drift | Monitor closely, investigate |
| > 0.25 | Significant drift | Trigger retraining pipeline |

## Setup Steps

### 1. CronJob Configuration
The drift detection CronJob is defined at `k8s/drift-detection-cronjob.yaml`:
- Schedule: Daily at 02:00 UTC
- Compares current production data distribution against training baseline
- Calculates PSI per feature
- Reports results to Prometheus metrics

### 2. Alert Integration
When PSI > 0.25 for any feature:
1. CronJob exits with non-zero status
2. GitHub Actions workflow `drift-detection.yml` captures the alert
3. If configured, triggers `retrain-bankchurn.yml` automatically

### 3. Monitoring
```bash
# Check last drift detection run
kubectl get jobs -l app=drift-detection --sort-by=.metadata.creationTimestamp

# View results
kubectl logs job/drift-detection-<timestamp>

# Check Prometheus metrics
curl -s http://prometheus:9090/api/v1/query?query=bankchurn_drift_psi
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| CronJob never runs | Schedule syntax error | Verify cron expression in YAML |
| PSI always 0 | Baseline data not loaded | Check ConfigMap with training distribution |
| False positives | Threshold too sensitive | Adjust per-feature thresholds |
| Job OOMKilled | Large dataset in memory | Increase resource limits or sample data |
