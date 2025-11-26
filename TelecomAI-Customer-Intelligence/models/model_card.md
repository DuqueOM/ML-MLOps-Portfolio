# Model Card — TelecomAI Plan Predictor v1.0

## Model Overview

| Field | Value |
|-------|-------|
| **Model Name** | TelecomAI-VotingClassifier |
| **Version** | 1.0.0 |
| **Type** | Binary Classification (Plan Recommendation) |
| **Framework** | Scikit-learn |
| **Last Updated** | November 2025 |

---

## Purpose

**Primary Use**: Predict whether a telecom customer should be on the "Ultra" plan based on their usage patterns.

**Intended Users**:
- Sales teams for upselling opportunities
- Customer success for plan optimization
- Product teams for usage analysis

**Out of Scope**:
- Churn prediction (separate model)
- Credit risk assessment
- Network capacity planning

---

## Model Architecture

```
Pipeline: [Preprocessor] → [VotingClassifier]

Preprocessor:
  - Numerical: StandardScaler (calls, minutes, messages, mb_used)
  - No categorical features in this dataset

Classifier:
  - VotingClassifier (soft voting)
    - LogisticRegression
    - RandomForestClassifier
    - GradientBoostingClassifier (optional)
```

---

## Training Data

| Attribute | Value |
|-----------|-------|
| **Source** | User behavior dataset (`users_behavior.csv`) |
| **Size** | ~3,000 records |
| **Features** | 4 input features |
| **Target** | `is_ultra` (1 = Ultra plan, 0 = Standard plan) |
| **Class Balance** | ~30% Ultra users |
| **Split** | 80% train / 20% test |

### Feature Dictionary

| Feature | Type | Description | Range |
|---------|------|-------------|-------|
| calls | float | Number of calls made | 0-200 |
| minutes | float | Total call duration (minutes) | 0-1000 |
| messages | float | Number of text messages | 0-200 |
| mb_used | float | Mobile data used (MB) | 0-100,000 |

---

## Performance Metrics

### Primary Metrics

| Metric | Train | Test | Target |
|--------|-------|------|--------|
| **AUC-ROC** | 0.867 | **0.840** | ≥ 0.85 |
| **Accuracy** | 83.4% | **81.2%** | ≥ 0.80 |
| **Precision** | 84.2% | **81.7%** | — |
| **Recall** | 52.3% | **49.7%** | — |
| **F1-Score** | 0.645 | **0.618** | — |

### Confusion Matrix (Test Set)

```
                 Predicted
              Standard  Ultra
Actual  Std    412       18
        Ultra   98       97
```

---

## Limitations & Bias

### Known Limitations

1. **Usage Patterns Only**: Does not consider demographics, tenure, or payment history.

2. **Binary Classification**: Only two plan options. Does not support multi-tier recommendations.

3. **Static Thresholds**: Plan recommendations based on training data patterns; may not reflect current plan pricing.

### Bias Considerations

| Dimension | Assessment | Mitigation |
|-----------|------------|------------|
| **Heavy Users** | Model favors recommending Ultra to high-data users | Expected behavior |
| **Usage Correlation** | Calls/minutes/messages are correlated | PCA considered but not applied |

---

## How to Reproduce

### Training

```bash
cd TelecomAI-Customer-Intelligence

# 1. Install dependencies
pip install -r requirements.txt

# 2. Ensure data is available
# Place users_behavior.csv in data/raw/

# 3. Train model
python main.py --mode train

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
       "calls": 40.0,
       "minutes": 311.9,
       "messages": 83.0,
       "mb_used": 19915.42
     }'
```

**Expected Response**:
```json
{
  "prediction": 0,
  "probability_is_ultra": 0.12
}
```

---

## Deployment

| Environment | URL | Status |
|-------------|-----|--------|
| **Local Docker** | `http://localhost:8000` | ✅ Available |
| **GHCR Image** | `ghcr.io/duqueom/telecom-api:latest` | **[PENDING PUSH]** |

### Docker Deployment

```bash
# Pull and run
docker pull ghcr.io/duqueom/telecom-api:latest
docker run -p 8000:8000 ghcr.io/duqueom/telecom-api:latest

# Health check
curl http://localhost:8000/health
```

---

## Monitoring & Maintenance

### Drift Detection

- **Feature Drift**: Monitor usage distributions (especially `mb_used` trends)
- **Concept Drift**: Plan definitions may change; retrain if pricing tiers updated

### Retraining Triggers

| Trigger | Threshold | Action |
|---------|-----------|--------|
| AUC drop | < 0.80 | Alert + investigate |
| Plan changes | Business trigger | Full retrain |
| Quarterly | — | Scheduled refresh |

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

- [Architecture Documentation](docs/ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/docs)
- [Experiment Tracking (MLflow)](http://localhost:5000)
