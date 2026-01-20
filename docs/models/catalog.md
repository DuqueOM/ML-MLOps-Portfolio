# 📚 Model Catalog

**Production Model Registry** — All models tracked via MLflow for full reproducibility

---

## 📊 Overview

| Project | Model ID | Algorithm | Version | Status | Primary Metric | Last Updated |
|---------|----------|-----------|---------|--------|----------------|--------------|
| **BankChurn** | `bankchurn-voting-v1.5.0` | VotingClassifier (LR + RF) | 1.5.0 | ✅ Production | AUC-ROC: 0.853 | January 2026 |
| **CarVision** | `carvision-rf-v1.5.0` | RandomForestRegressor | 1.5.0 | ✅ Production | R²: 0.766 | January 2026 |
| **TelecomAI** | `telecomai-voting-v1.5.0` | VotingClassifier (3 models) | 1.5.0 | ✅ Production | AUC-ROC: 0.84 | January 2026 |

---

## 🏦 BankChurn Predictor

### Production Model

| Attribute | Value |
|-----------|-------|
| **Model ID** | `bankchurn-voting-v1.5.0` |
| **Model Name** | BankChurn Customer Churn Classifier |
| **Version** | 1.5.0 |
| **Algorithm** | VotingClassifier (Logistic Regression + RandomForest) |
| **Framework** | Scikit-learn 1.3+ |
| **Status** | ✅ **Production** |
| **Artifact Path** | `artifacts/model.joblib` (unified pipeline) |
| **Model Size** | 4.0 MB |
| **Created** | January 2026 |
| **Last Updated** | January 2026 |

### Performance Metrics (Test Set, n=2,000)

| Metric | Value | Business Impact |
|--------|-------|-----------------|
| **AUC-ROC** | **0.853** | Excellent discrimination |
| **Accuracy** | 85.7% | Overall correctness |
| **Precision (Churn)** | 69.2% | 31% false alarms |
| **Recall (Churn)** | 53.6% | Catches 54% of churners |
| **F1-Score (Churn)** | **0.604** | Balanced metric |
| **Precision@10%** | 84% | Top 10% contains 84% churners |

### Architecture

```python
Pipeline:
  [Preprocessor] → [VotingClassifier]

Preprocessor:
  ├─ SimpleImputer (numerical: median, categorical: constant)
  ├─ StandardScaler (numerical features)
  └─ OneHotEncoder (Geography, Gender)

VotingClassifier (soft voting, weights=[1, 2]):
  ├─ LogisticRegression(C=1.0, max_iter=1000, random_state=42)
  └─ RandomForestClassifier(n_estimators=100, max_depth=10, 
                            class_weight='balanced', random_state=42)
```

### Key Features

- **SHAP Explainability**: Global and individual feature importance
- **Drift Detection**: Evidently AI monitoring (PSI thresholds)
- **Fairness Analysis**: Geography (Germany +28% churn), Age (55+ = 2.3× risk)
- **Retraining Triggers**: AUC <0.75, drift >0.3, quarterly scheduled

### Model Card

Full documentation: [BankChurn Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/BankChurn-Predictor/models/model_card.md)

---

## 🚗 CarVision Market Intelligence

### Production Model

| Attribute | Value |
|-----------|-------|
| **Model ID** | `carvision-rf-v1.5.0` |
| **Model Name** | CarVision Vehicle Price Predictor |
| **Version** | 1.5.0 |
| **Algorithm** | RandomForestRegressor |
| **Framework** | Scikit-learn 1.3+ |
| **Status** | ✅ **Production** |
| **Artifact Path** | `artifacts/model.joblib` (full pipeline) |
| **Model Size** | 6 KB |
| **Created** | January 2026 |
| **Last Updated** | January 2026 |

### Performance Metrics (Test Set, n=9,566)

| Metric | Value | Description |
|--------|-------|-------------|
| **R²** | **0.766** | Explains 77% of variance |
| **RMSE** | **$4,794** | Average prediction error |
| **MAE** | $3,450 | Median absolute error |
| **MAPE** | 17.8% | Percentage error |
| **Cross-Validation R²** | 0.758 ± 0.023 | 5-fold stability |
| **Bootstrap 95% CI** | $4,512 - $5,076 | RMSE confidence interval |

### Architecture

```python
Pipeline:
  [FeatureEngineer] → [Preprocessor] → [RandomForestRegressor]

FeatureEngineer (custom class):
  ├─ vehicle_age = 2026 - model_year
  ├─ brand = first word of model
  └─ price_per_mile (training only, excluded from inference)

Preprocessor:
  ├─ SimpleImputer (median/mode strategies)
  ├─ StandardScaler (numerical features)
  └─ OneHotEncoder (categorical: fuel, transmission, condition, etc.)

RandomForestRegressor:
  n_estimators=100, max_depth=15, min_samples_split=5,
  random_state=42
```

### Key Features

- **Centralized Feature Engineering**: `FeatureEngineer` class prevents training-serving skew
- **Data Leakage Prevention**: Excludes `price_per_mile` from inference
- **Advanced Validation**: Temporal backtest (R²=0.742), bootstrap CI
- **Performance by Segment**: <$10K (R²=0.68), $10K-$30K (R²=0.78), >$60K (R²=0.52)
- **Interactive Dashboard**: Streamlit app with 4 tabs (Portfolio, Market, Metrics, Predictor)

### Model Card

Full documentation: [CarVision Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/CarVision-Market-Intelligence/models/model_card.md)

---

## 📱 TelecomAI Customer Intelligence

### Production Model

| Attribute | Value |
|-----------|-------|
| **Model ID** | `telecomai-voting-v1.5.0` |
| **Model Name** | TelecomAI Plan Predictor |
| **Version** | 1.5.0 |
| **Algorithm** | VotingClassifier (LR + GB + RF) |
| **Framework** | Scikit-learn 1.3+ |
| **Status** | ✅ **Production** |
| **Artifact Path** | `artifacts/model.joblib` (unified pipeline) |
| **Model Size** | 156 KB |
| **Created** | January 2026 |
| **Last Updated** | January 2026 |

### Performance Metrics (Test Set, n=643)

| Metric | Value | Business Impact |
|--------|-------|-----------------|
| **AUC-ROC** | **0.84** | Strong discrimination |
| **Accuracy** | **82%** | Overall correctness |
| **Precision (Ultra)** | 72% | 28% false upgrades |
| **Recall (Ultra)** | 56% | Catches 56% of Ultra candidates |
| **F1-Score (Ultra)** | **0.63** | Balanced metric |
| **Cross-Validation Acc** | 0.818 ± 0.012 | 5-fold stability |

### Architecture

```python
Pipeline:
  [Preprocessor] → [VotingClassifier]

Preprocessor:
  └─ StandardScaler() on 4 numerical features
      (calls, minutes, messages, mb_used)

VotingClassifier (soft voting, weights=[1, 2, 2]):
  ├─ LogisticRegression(C=1.0, class_weight={0: 0.4, 1: 0.6})
  ├─ GradientBoostingClassifier(n_estimators=100, learning_rate=0.1)
  └─ RandomForestClassifier(n_estimators=100, max_depth=10, 
                            class_weight='balanced')
```

### Key Features

- **Threshold Optimization**: Conservative (0.5), Balanced (0.42), Aggressive (0.35)
- **Business Impact**: $5.4M annual revenue recovery (100K customer base)
- **Usage Segmentation**: Heavy data users (>30GB), light users (<5GB)
- **Feature Importance**: `mb_used` (45%), `minutes` (28%), `messages` (18%), `calls` (9%)
- **Ethical Targeting**: Contact frequency limits, opt-out mechanisms

### Model Card

Full documentation: [TelecomAI Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/TelecomAI-Customer-Intelligence/models/model_card.md)

---

## 📋 Model Lifecycle

### Version History

| Project | v1.0.0 | v1.5.0 (Current) | Changes |
|---------|--------|------------------|---------|
| **BankChurn** | Sep 2025 (AUC=0.78) | **January 2026** (AUC=0.853) | Ensemble weights tuning, SHAP integration |
| **CarVision** | Sep 2025 (R²=0.72) | **January 2026** (R²=0.766) | FeatureEngineer centralization, bootstrap CI |
| **TelecomAI** | Sep 2025 (Acc=0.78) | **January 2026** (Acc=82%) | Added GradientBoosting, threshold optimization |

### Promotion Criteria (Staging → Production)

All models must pass these gates:

1. ✅ **Performance**: Primary metric exceeds baseline by ≥5%
2. ✅ **Stability**: Cross-validation std dev <3%
3. ✅ **Latency**: P95 inference time <200ms
4. ✅ **Coverage**: Test coverage >70%
5. ✅ **Security**: Clean security scans (Bandit, pip-audit)
6. ✅ **Documentation**: Model card and data card updated

---

## 🔄 Retraining Strategy

### Automated Triggers

| Trigger | BankChurn | CarVision | TelecomAI |
|---------|-----------|-----------|-----------|
| **Performance Drop** | AUC <0.75 | R² <0.70 | AUC <0.80 |
| **Data Drift** | >30% features (Evidently) | >30% features | >30% features |
| **Time-based** | Quarterly | Quarterly | Quarterly |
| **Business Event** | Plan pricing change | New model years | Plan pricing change |

### Retraining Pipeline

```bash
# 1. Monitor production metrics
python monitoring/check_drift.py --project <project>

# 2. If trigger activated, retrain
cd <project>
python main.py --mode train --config configs/config.yaml

# 3. Evaluate on holdout set
python main.py --mode eval

# 4. Compare with current production
mlflow experiments compare --baseline <current> --challenger <new>

# 5. If champion, promote to production
git tag -a v1.6.0 -m "Production model v1.6.0"
docker build -t <project>:v1.6.0 .
docker push ghcr.io/duqueom/<project>:v1.6.0
```

---

## 📊 MLflow Integration

### Experiment Tracking

All models logged to central MLflow server:

```bash
# Start MLflow server
docker-compose -f docker-compose.mlflow.yml up -d

# View experiments
open http://localhost:5000

# Total tracked runs: 9 (3 per project)
```

### Logged Artifacts

For each run, MLflow tracks:

- ✅ **Parameters**: Hyperparameters, config file
- ✅ **Metrics**: Performance metrics (AUC, RMSE, accuracy, etc.)
- ✅ **Artifacts**: Model file, preprocessor, config.yaml
- ✅ **System Info**: Python version, library versions
- ✅ **Metadata**: Training duration, dataset version (DVC SHA)

---

## 🔗 Related Documentation

- **[Model Reproducibility](reproducibility.md)** — How to reproduce model training
- **[API Reference](../api/rest-apis.md)** — Using models via REST APIs
- **[Operations Guide](../operations/deployment.md)** — Deploying models to production
- **[Architecture](../architecture/overview.md)** — Model serving infrastructure

### Per-Project Model Cards

- **[BankChurn Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/BankChurn-Predictor/models/model_card.md)** — Comprehensive documentation
- **[CarVision Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/CarVision-Market-Intelligence/models/model_card.md)** — Comprehensive documentation
- **[TelecomAI Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/TelecomAI-Customer-Intelligence/models/model_card.md)** — Comprehensive documentation

---

!!! info "Model Registry Status"
    All production models are **actively maintained** and monitored.  
    **Last Catalog Update**: January 2026  
    **Total Models in Production**: 3

!!! tip "Accessing Models"
    Models can be accessed via:
    
    - **REST APIs**: `http://localhost:800X/predict` (X = 1, 2, 3)
    - **Python SDK**: `from <project> import <Predictor>`
    - **MLflow UI**: `http://localhost:5000`
    - **Docker Images**: `ghcr.io/duqueom/<project>:v1.5.0`

---

**Last Updated**: January 2026
