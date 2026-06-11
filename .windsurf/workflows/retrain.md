---
description: Model retraining workflow — triggered by drift alert or manual request
---

# /retrain Workflow

## 1. Identify the Service

Determine which service needs retraining and why:
- Drift alert: check PSI scores in Prometheus
- Metric degradation: check rolling metrics in Grafana
- Manual request: document reason

## 2. Download Fresh Data

```bash
gsutil cp gs://${DATA_BUCKET}/${SERVICE}/production_data_latest.csv data/raw/
```
// turbo

## 3. Validate Data

```bash
python -c "
from src.${SERVICE_SLUG}.schemas import ServiceInputSchema
import pandas as pd
df = pd.read_csv('data/raw/production_data_latest.csv')
ServiceInputSchema.validate(df)
print(f'OK: {len(df)} rows')
"
```

## 4. Execute Training

```bash
python src/${SERVICE_SLUG}/training/train.py \
  --data data/raw/production_data_latest.csv \
  --experiment "${SERVICE}-retrain-$(date +%Y%m%d)" \
  --optuna-trials 50
```

## 5. Evaluate Quality Gates

Run quality gate checks. **ALL must pass — no exceptions**:

| Gate | Condition | Typical Threshold |
|------|-----------|------------------|
| Primary metric | `new_auc >= MIN_THRESHOLD` | ROC-AUC >= 0.80 |
| No regression | `new_auc >= prod_auc * 0.95` | < 5% drop |
| Fairness | `DIR >= 0.80` per protected attribute | Four-fifths rule |
| Latency | `new_p95 <= prod_p95 * 1.20` | No more than 20% slower |
| Leakage check | `auc < 0.99` | Suspiciously high = investigate |

```bash
# Verify quality gates programmatically
python -c "
import joblib, pandas as pd
from sklearn.metrics import roc_auc_score

pipe = joblib.load('models/model.joblib')
X_test = pd.read_csv('data/test_features.csv')
y_test = pd.read_csv('data/test_labels.csv').squeeze()
y_prob = pipe.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_prob)
print(f'ROC-AUC: {auc:.4f}')
assert auc >= 0.80, f'FAIL: {auc:.4f} < 0.80'
assert auc < 0.99, f'LEAKAGE?: {auc:.4f} suspiciously high'
print('All gates passed')
"
```

## 6a. If ALL PASS — Promote

```bash
# Promote in MLflow
python scripts/promote_model.py --service ${SERVICE} --version ${NEW_VERSION}

# Upload model
gsutil cp models/model.joblib gs://${MODEL_BUCKET}/${SERVICE}/model.joblib
aws s3 cp models/model.joblib s3://${MODEL_BUCKET}/${SERVICE}/model.joblib

# Rolling restart
kubectl rollout restart deployment/${SERVICE}-predictor -n ${NAMESPACE}
```

## 6b. If ANY FAIL — Do Not Promote

```bash
gh issue create \
  --title "Retraining quality gate failure: ${SERVICE}" \
  --body "Failed gates: ${FAILED_GATES}" \
  --label "ml-retraining,quality-gate-failure"
```

## 7. Update Reference Data

```bash
python src/${SERVICE_SLUG}/monitoring/drift_detection.py --update-reference
```

## 8. Verify Deployment

- Check pods restarted and healthy
- Verify new model_version in `/metrics`
- Run `/drift-check` post-deploy to establish new baseline
