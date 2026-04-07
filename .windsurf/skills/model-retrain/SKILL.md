---
name: model-retrain
description: Guides model retraining for any of the 3 ML services, including data validation, training, evaluation against baseline metrics, MLflow registration, and deployment preparation.
---

## Retraining Process

### Step 1: Determine Trigger
- **Drift detected**: PSI > 0.25 from drift-detection CronJob
- **Scheduled**: Quarterly retraining cadence
- **Manual**: New data available, feature engineering changes

### Step 2: Data Validation
```bash
# Verify data integrity
python -c "
import pandas as pd
df = pd.read_csv('data/train.csv')
print(f'Rows: {len(df)}, Cols: {len(df.columns)}')
print(f'Nulls:\n{df.isnull().sum()}')
print(f'Dtypes:\n{df.dtypes}')
"
```

### Step 3: Train
```bash
# Use the production training script
python scripts/train_production_models.py --service <service-name>
```

### Step 4: Evaluate Against Baseline

See `validation-criteria.md` for per-service acceptance criteria.

| Service | Metric | Minimum Threshold | Current Baseline |
|---------|--------|-------------------|-----------------|
| BankChurn | AUC | ≥ 0.85 | 0.8693 |
| BankChurn | F1 | ≥ 0.60 | 0.6243 |
| NLPInsight | Accuracy | ≥ 0.95 | 0.9691 |
| ChicagoTaxi | R² | ≥ 0.75 | 0.7955 |

**Rule**: New model must meet minimum threshold AND not regress >2% from current baseline.

### Step 5: Register in MLflow
```bash
# Log metrics and register model
python -c "
import mlflow
mlflow.set_tracking_uri('http://localhost:5000')
with mlflow.start_run(run_name='retrain-v{VERSION}'):
    mlflow.log_metrics({...})
    mlflow.sklearn.log_model(model, 'model')
    mlflow.register_model(f'runs:/{run_id}/model', '<service>-model')
"
```

### Step 6: Prepare for Deployment
1. Serialize model with joblib (sklearn) or save as model.tar.gz (FinBERT)
2. Upload to GCS: `gsutil cp model.joblib gs://ml-portfolio-duque-om-202602-ml-models-production/<service>/`
3. Update model version in deployment ConfigMap
4. Follow deploy-gke skill for deployment
