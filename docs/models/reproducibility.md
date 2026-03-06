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
# NLPInsight: Acc 80.6%, F1-macro 0.748 (TF-IDF + LogReg)
# ChicagoTaxi: R² 0.96, RMSE 7.87 (RandomForest)
```

## Random Seeds

All models use `random_state=42` for reproducibility.

## Model Artifacts

| Project | Path | Size | Format |
|---------|------|------|--------|
| BankChurn | `models/model.joblib` | 4.1 MB | Joblib (compress=3) |
| NLPInsight | `models/model.joblib` | ~5 MB | Joblib (compress=3) |
| ChicagoTaxi | `models/model.joblib` | ~2 MB | Joblib (compress=3) |

## Data Sources

| Project | Dataset | Rows | Source |
|---------|---------|------|--------|
| BankChurn | Churn_Modelling.csv | 10,000 | Kaggle |
| NLPInsight | Twitter Financial News | 11,931 | HuggingFace (zeroshot) |
| ChicagoTaxi | Taxi Trips (2013-2023) | 6,364,313 | Chicago Open Data Portal |

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
