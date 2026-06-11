---
name: model-retrain
description: Execute model retraining with quality gates and safe promotion
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Bash(python:*)
  - Bash(gsutil:*)
  - Bash(aws:*)
  - Bash(kubectl:*)
  - Bash(gh:*)
when_to_use: >
  Use when a model needs retraining due to drift, scheduled maintenance, or metric degradation.
  Examples: 'retrain bankchurn model', 'drift detected needs retraining', 'scheduled retrain'
argument-hint: "<service-name> [trigger-reason]"
arguments:
  - service-name
authorization_mode:
  train: AUTO        # reversible — new MLflow run, existing model untouched
  to_staging: CONSULT # human approves Staging transition (affects staging deploys)
  to_production: STOP # requires governance approval (ADR-002)
---

# Model Retraining

## Authorization Protocol

This skill spans three authorization layers, aligned with the Agent Behavior Protocol (AGENTS.md):

| Phase | Mode | What happens |
|-------|------|--------------|
| Training (MLflow run) | AUTO | Agent may run training, log to MLflow, produce artifacts |
| Transition to `Staging` | CONSULT | Agent presents metrics + quality gates + drift diff; human approves via MLflow UI or `/promote-model` PR |
| Transition to `Production` | **STOP** | Never transitions directly. Opens PR, waits for Tech Lead approval via GitHub Environment `production` |

### Automatic STOP escalation

Even in AUTO phase, escalate to STOP if the new model exhibits any of:
- Primary metric > 0.99 without explanation (D-06 — investigate leakage)
- Fairness DIR in `[0.80, 0.85]` (marginal — human judgment required)
- Metric regression > 5% vs current production
- Any quality gate fails

Emit structured signal:
```
[AGENT MODE: STOP]
Operation: Model retraining for {service}
Reason: Fairness DIR = 0.82 (marginal, requires human review)
Waiting for: Engineer inspection + either ADR documenting decision OR retraining with fairness-aware loss
```

## Step 1: Validate Retraining Trigger

Before retraining, confirm the trigger:
- **Drift alert**: PSI ≥ threshold on critical feature (check Prometheus/Grafana)
- **Metric degradation**: Rolling metric below quality gate (check monitoring)
- **Scheduled**: Periodic retraining per policy
- **Manual**: Engineer-initiated (document reason)

## Step 2: Download Fresh Data

```bash
# Download latest production data
gsutil cp gs://{data-bucket}/{service}/production_data_latest.csv data/raw/
# Or from AWS:
aws s3 cp s3://{data-bucket}/{service}/production_data_latest.csv data/raw/
```

## Step 3: Validate Data Before Training

```bash
python -c "
from src.{service}.schemas import ServiceInputSchema
import pandas as pd
import pandera as pa

df = pd.read_csv('data/raw/production_data_latest.csv')
ServiceInputSchema.validate(df)
print(f'Validation passed: {len(df)} rows, {len(df.columns)} columns')
"
```

If validation fails → investigate upstream data changes before proceeding.

## Step 4: Execute Training

```bash
python src/{service}/training/train.py \
  --data data/raw/production_data_latest.csv \
  --experiment "{service}-retraining-$(date +%Y%m%d)" \
  --optuna-trials 50
```

This executes the full pipeline:
1. Load + validate data
2. Feature engineering
3. Train/val/test split (temporal if dates exist)
4. Cross-validation
5. Optuna hyperparameter tuning
6. Evaluate on test set
7. Log to MLflow

## Step 5: Quality Gates (ALL MUST PASS)

```python
gates = {
    "primary_metric >= threshold": new_metrics["primary"] >= MINIMUM_THRESHOLD,
    "no regression > 5%": new_metrics["primary"] >= prod_metrics["primary"] * 0.95,
    "secondary_metric": new_metrics["secondary"] >= SECONDARY_THRESHOLD,
    "fairness DIR >= 0.80": all(new_metrics[f"dir_{attr}"] >= 0.80 for attr in PROTECTED),
    "p95_latency <= 1.2x": new_metrics["p95_ms"] <= prod_metrics["p95_ms"] * 1.20,
}

failed = [name for name, passed in gates.items() if not passed]
```

## Step 5.5: Champion/Challenger Statistical Gate (ADR-008)

Before promoting a challenger that passed quality gates, prove it is
statistically superior (or at least non-inferior) to the current champion
on the same holdout:

```bash
python -m src.{service}.evaluation.champion_challenger \
  --champion    models/champion/model.joblib \
  --challenger  models/model.joblib \
  --holdout     data/holdout.csv --target {target} \
  --config      configs/champion_challenger.yaml \
  --output      reports/champion_challenger.json
echo "exit_code=$?"
```

Three possible exit codes and their meanings:

| Exit | Decision | Action |
|------|----------|--------|
| 0 | promote | McNemar p < alpha AND ΔAUC > superiority margin → proceed to Step 6a |
| 1 | keep    | ΔAUC not statistically significant → keep champion, document in CHANGELOG |
| 2 | block   | Challenger CI lower bound < -non_inferiority margin → open incident issue |

Read `reports/champion_challenger.json` fields:
- `mcnemar.p_value`                    — H0: equal error rates
- `bootstrap.delta_auc_point`          — point estimate of ΔAUC
- `bootstrap.delta_auc_ci_lower/upper` — 95% CI (the ACTUAL decision driver)
- `decision.reason`                    — human-readable rationale

Exit 1 is common and NOT a failure — it means you re-trained but the new
model is not measurably better. This saves you from deploying models that
add risk without benefit.

Exit 2 is a regression — pause the workflow, investigate, and consider the
possibility of data leakage in the champion's holdout (D-06).

## Step 6a: ALL PASS (quality gates + C/C promote) → Promote

```bash
# Promote in MLflow Registry
python -c "
import mlflow
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage('{service}Model', version={V}, stage='Production')
client.transition_model_version_stage('{service}Model', version={V-1}, stage='Archived')
"

# Upload model to GCS/S3
gsutil cp models/model.joblib gs://{model-bucket}/{service}/model.joblib
aws s3 cp models/model.joblib s3://{model-bucket}/{service}/model.joblib

# Rolling restart to pick up new model
kubectl rollout restart deployment/{service}-predictor -n {namespace}
kubectl rollout status deployment/{service}-predictor -n {namespace}
```

## Step 6b: ANY FAIL → Do Not Promote

```bash
# Create GitHub Issue
gh issue create \
  --title "Retraining failed quality gates: {service}" \
  --body "Failed gates: ${failed}\nKeeping current model in production." \
  --label "ml-retraining,quality-gate-failure"
```

## Step 7: Post-Retraining Verification

- [ ] New model version in MLflow Registry = Production
- [ ] Previous model version = Archived
- [ ] Pods restarted and passing health checks
- [ ] `/predict` returning valid predictions
- [ ] Grafana showing new model_version label
- [ ] No new alerts in AlertManager

## Step 8: Update Reference Data

```bash
# Update drift reference to new training data distribution
python src/{service}/monitoring/drift_detection.py --update-reference
gsutil cp data/reference/{service}_reference.csv gs://{data-bucket}/{service}/reference/
```
