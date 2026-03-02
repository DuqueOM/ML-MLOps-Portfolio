# Reproducibility Guide

## Environment

| Component | Version |
|-----------|---------|
| Python | 3.11.14 |
| scikit-learn | 1.8.0 |
| XGBoost | 3.2.0 |
| SHAP | 0.50.0 |
| MLflow | 3.10 |

## Reproduce Training

```bash
# 1. Create environment
conda create -n ml-py311 python=3.11.14 -y
conda activate ml-py311

# 2. Install dependencies (per project)
pip install -r BankChurn-Predictor/requirements.txt
pip install -r CarVision-Market-Intelligence/requirements.txt
pip install -r NLPInsight-Customer-Intelligence/requirements.txt

# 3. Train all models
python scripts/train_production_models.py

# 4. Verify metrics
# BankChurn: AUC 0.8626, F1 0.616
# CarVision: R² 0.8246, RMSE $6,273
# NLPInsight: Accuracy 88.08%, F1-macro 0.826
```

## Random Seeds

All models use `random_state=42` for reproducibility.

## Model Artifacts

| Project | Path | Size | Format |
|---------|------|------|--------|
| BankChurn | `models/model.joblib` | 4.1 MB | Joblib (compress=3) |
| CarVision | `models/model.joblib` | 5.7 MB | Joblib (compress=3) |
| NLPInsight | `models/model.joblib` | 309 KB | Joblib (compress=3) |

## Data Sources

| Project | Dataset | Rows | Source |
|---------|---------|------|--------|
| BankChurn | Churn.csv | 10,000 | Kaggle |
| CarVision | vehicles_us.csv | ~500K | Practicum |
| NLPInsight | FinancialPhraseBank | 4,845 | Malo et al. |

## MLflow Tracking

```bash
# Local
export MLFLOW_TRACKING_URI=file:./mlruns

# GKE
kubectl port-forward svc/mlflow-service 5000:5000 -n ml-portfolio
export MLFLOW_TRACKING_URI=http://localhost:5000
```

---

*Last Updated: March 2026*
