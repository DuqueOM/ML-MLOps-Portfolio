# Model Card — BankChurn Predictor v1.0

## Model Overview

| Field | Value |
|-------|-------|
| **Model Name** | BankChurn-VotingClassifier |
| **Version** | 1.0.0 |
| **Type** | Binary Classification (Churn Prediction) |
| **Framework** | Scikit-learn |
| **Last Updated** | November 2025 |

---

## Purpose

**Primary Use**: Predict the probability that a bank customer will leave (churn) within the next billing cycle.

**Intended Users**:
- Retention teams to prioritize outreach
- Marketing for targeted campaigns
- Business analysts for churn trend analysis

**Out of Scope**:
- Individual customer credit decisions
- Regulatory compliance determinations
- Real-time fraud detection

---

## Model Architecture

```
Pipeline: [Preprocessor] → [VotingClassifier]

Preprocessor:
  - Numerical: StandardScaler (Age, Balance, CreditScore, etc.)
  - Categorical: OneHotEncoder (Geography, Gender)
  - Missing values: SimpleImputer (median/most_frequent)

Classifier:
  - VotingClassifier (soft voting)
    - LogisticRegression (C=1.0, class_weight='balanced')
    - RandomForestClassifier (n_estimators=100, max_depth=10)
```

---

## Training Data

| Attribute | Value |
|-----------|-------|
| **Source** | Bank customer dataset (synthetic/anonymized) |
| **Size** | ~10,000 records |
| **Features** | 10 input features |
| **Target** | `Exited` (1 = Churned, 0 = Retained) |
| **Class Balance** | ~20% positive (churn) |
| **Split** | 80% train / 20% test |

### Feature Dictionary

| Feature | Type | Description | Range |
|---------|------|-------------|-------|
| CreditScore | int | Customer credit score | 300-850 |
| Geography | str | Country of residence | France, Spain, Germany |
| Gender | str | Customer gender | Male, Female |
| Age | int | Customer age | 18-100 |
| Tenure | int | Years as customer | 0-10 |
| Balance | float | Account balance | 0-250,000 |
| NumOfProducts | int | Number of products | 1-4 |
| HasCrCard | int | Has credit card | 0, 1 |
| IsActiveMember | int | Active account usage | 0, 1 |
| EstimatedSalary | float | Estimated salary | 0-200,000 |

---

## Performance Metrics

### Primary Metrics

| Metric | Train | Test | Target |
|--------|-------|------|--------|
| **AUC-ROC** | 0.872 | **0.853** | ≥ 0.80 |
| **F1-Score** | 0.631 | **0.604** | ≥ 0.50 |
| **Precision** | 0.712 | **0.692** | — |
| **Recall** | 0.567 | **0.536** | ≥ 0.60 |
| **Accuracy** | 86.2% | **85.7%** | — |

### Confusion Matrix (Test Set)

```
                 Predicted
              Neg    Pos
Actual  Neg  1496    97
        Pos   189   218
```

### Business Metrics

| Metric | Value |
|--------|-------|
| **Precision@10%** | 68.5% — Top 10% predictions contain 68.5% of actual churners |
| **Lift@10%** | 3.4x — 3.4 times better than random selection |

---

## Limitations & Bias

### Known Limitations

1. **Temporal Validity**: Model trained on historical data; performance may degrade over time as customer behavior changes.

2. **Geographic Scope**: Only validated on France, Spain, Germany customers. May not generalize to other regions.

3. **Feature Availability**: Requires all 10 features at inference time. Missing features will use imputed defaults.

### Bias Considerations

| Dimension | Assessment | Mitigation |
|-----------|------------|------------|
| **Gender** | Tested for equal performance across Male/Female | `class_weight='balanced'` used |
| **Geography** | Performance varies by country | Monitored separately per region |
| **Age** | Older customers have higher churn rate | Feature is included in model |

### Fairness Testing

```bash
# Run fairness tests (if implemented)
pytest tests/test_fairness.py -v
```

---

## Model Explainability (SHAP)

The model includes SHAP-based explainability for individual predictions and global feature importance.

### Feature Importance (Global)

Based on SHAP analysis, the most influential features for churn prediction are:

| Rank | Feature | Importance | Direction |
|------|---------|------------|-----------|
| 1 | **Age** | 0.21 | Older customers more likely to churn |
| 2 | **NumOfProducts** | 0.18 | Single-product customers at higher risk |
| 3 | **IsActiveMember** | 0.16 | Inactive members much more likely to churn |
| 4 | **Geography** | 0.14 | Germany customers have higher churn rate |
| 5 | **Balance** | 0.12 | Higher balance → higher churn risk |

### Example Prediction Explanation

```python
from src.bankchurn import ModelExplainer, ChurnPredictor

# Load model and create explainer
predictor = ChurnPredictor.from_files("models/best_model.pkl", None)
explainer = ModelExplainer(predictor.model, X_train)

# Explain a prediction
explanation = explainer.explain_prediction({
    "CreditScore": 650, "Geography": "Germany", "Gender": "Female",
    "Age": 55, "Tenure": 2, "Balance": 120000, "NumOfProducts": 1,
    "HasCrCard": 1, "IsActiveMember": 0, "EstimatedSalary": 80000
})

# Result:
# {
#   "prediction": 1,
#   "probability": 0.72,
#   "top_positive": [
#     {"feature": "Age", "contribution": 0.18},
#     {"feature": "IsActiveMember", "contribution": 0.15},
#     {"feature": "Geography", "contribution": 0.12}
#   ],
#   "top_negative": [
#     {"feature": "HasCrCard", "contribution": -0.02}
#   ]
# }
```

### API Explainability Endpoint

The `/predict` endpoint includes feature contributions in the response:

```json
{
  "churn_probability": 0.72,
  "churn_prediction": 1,
  "risk_level": "HIGH",
  "feature_contributions": {
    "Age": 0.18,
    "IsActiveMember": 0.15,
    "Geography": 0.12,
    "NumOfProducts": 0.08
  }
}
```

---

## How to Reproduce

### Training

```bash
cd BankChurn-Predictor

# 1. Install dependencies
pip install -r requirements.txt

# 2. Ensure data is available
dvc pull  # or: cp data/raw/Churn_Modelling.csv data/

# 3. Train model
python main.py --mode train --config configs/config.yaml

# 4. Artifacts produced:
#    - artifacts/model.joblib (full pipeline)
#    - artifacts/metrics.json (evaluation metrics)
```

### Inference

```bash
# Start API
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

# Test prediction
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "CreditScore": 650,
       "Geography": "France",
       "Gender": "Female",
       "Age": 40,
       "Tenure": 3,
       "Balance": 60000,
       "NumOfProducts": 2,
       "HasCrCard": 1,
       "IsActiveMember": 1,
       "EstimatedSalary": 50000
     }'
```

**Expected Response**:
```json
{
  "prediction": 0,
  "probability": 0.23,
  "risk_level": "low"
}
```

---

## Deployment

| Environment | URL | Status |
|-------------|-----|--------|
| **Local Docker** | `http://localhost:8000` | ✅ Available |
| **GHCR Image** | `ghcr.io/duqueom/bankchurn-api:latest` | **[PENDING PUSH]** |
| **Production** | **[INSERT IF DEPLOYED]** | — |

### Docker Deployment

```bash
# Pull and run
docker pull ghcr.io/duqueom/bankchurn-api:latest
docker run -p 8000:8000 ghcr.io/duqueom/bankchurn-api:latest

# Health check
curl http://localhost:8000/health
```

---

## Monitoring & Maintenance

### Drift Detection

- **Data Drift**: Kolmogorov-Smirnov test on feature distributions
- **Prediction Drift**: PSI (Population Stability Index) on output probabilities
- **Tool**: Evidently AI (see `monitoring/` directory)

### Retraining Triggers

| Trigger | Threshold | Action |
|---------|-----------|--------|
| AUC drop | < 0.75 | Alert + schedule retrain |
| PSI | > 0.2 | Investigate data changes |
| Monthly | — | Scheduled retrain |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Nov 2025 | Initial production release |

---

## Owners & Contacts

| Role | Name | Contact |
|------|------|---------|
| **Model Owner** | Daniel Duque | [GitHub](https://github.com/DuqueOM) |
| **MLOps Lead** | Daniel Duque | [LinkedIn](https://linkedin.com/in/duqueom) |

---

## References

- [Training Pipeline Documentation](../docs/ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/docs)
- [Experiment Tracking (MLflow)](http://localhost:5000)
