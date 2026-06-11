---
description: Run PSI drift analysis for one or all services
---

# /drift-check Workflow

## 1. Select Target

Choose which service(s) to check:
- Single service: `${SERVICE}`
- All services: iterate over project services

## 2. Download Current Production Data

```bash
gsutil cp gs://${DATA_BUCKET}/${SERVICE}/production_data_latest.csv data/production/
```
// turbo

## 3. Run Drift Detection

```bash
python src/${SERVICE_SLUG}/monitoring/drift_detection.py \
  --reference data/reference/${SERVICE_SLUG}_reference.csv \
  --current data/production/production_data_latest.csv \
  --output drift_report_$(date +%Y%m%d).json
```

## 4. Review PSI Scores

For each feature, check against thresholds:
```
PSI < 0.10:  ✅ No drift
0.10 ≤ PSI < 0.20: ⚠️ Warning — monitor
PSI ≥ 0.20:  🚨 Alert — action required
```

## 5. Push Metrics to Prometheus

```bash
python src/${SERVICE_SLUG}/monitoring/drift_detection.py --push-metrics
```
// turbo

## 6. Decision Tree

```
IF any critical feature PSI ≥ alert threshold:
  → Trigger /retrain workflow
  → Create GitHub Issue

IF any feature PSI ≥ warning threshold:
  → Log in drift tracking
  → Schedule review in 1 week

IF all features PSI < warning:
  → No action needed
  → Log successful check
```

## 7. Verify Heartbeat

Confirm the drift detection timestamp was updated:
```bash
curl 'http://prometheus:9090/api/v1/query?query=drift_detection_last_run_timestamp'
```

Should be within the last few minutes. If stale, the CronJob may be broken.

## 8. Document Results

Update the drift tracking log with:
- Date of check
- Per-feature PSI scores
- Decision taken (no action / monitor / retrain)
- Any notable patterns or trends
