# Reproducibility Guide

## Environment

| Component | Version |
|-----------|---------|
| Python | 3.11.14 |
| scikit-learn | 1.8.0 |
| LightGBM | 4.6+ |
| Transformers | 4.48+ |
| SHAP | 0.50.0 |
| MLflow | 3.10 |

## Reproduce Training

```bash
# 1. Create environment
conda create -n ml-py311 python=3.11.14 -y
conda activate ml-py311

# 2. Install dependencies (per project)
pip install -r BankChurn-Predictor/requirements.txt
pip install -r requirements.txt
pip install -r NLPInsight-Analyzer/requirements.txt

# 3. Train all models
python scripts/train_production_models.py

# 4. Verify metrics
# BankChurn: AUC 0.87, F1 0.62 (StackingClassifier)
# NLPInsight: Acc 97%, F1-w 0.97 (FinBERT)
```

## Random Seeds

All models use `random_state=42` for reproducibility.

## Model Artifacts

| Project | Path | Size | Format |
|---------|------|------|--------|
| BankChurn | `models/model.joblib` | 4.1 MB | Joblib (compress=3) |
| NLPInsight | `models/model.joblib` | 309 KB | Joblib (compress=3) |

## Data Sources

| Project | Dataset | Rows | Source |
|---------|---------|------|--------|
| BankChurn | Churn.csv | 10,000 | Kaggle |
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

*Last Updated: March 2026 — v3.5.0*
