# BankChurn Predictor

Customer churn prediction for banking institutions.

![BankChurn API](../media/screenshots/apis/25-fastapi-swagger-bankchurn.png)

## Performance (v2.0.0)

| Metric | Value |
|--------|-------|
| **AUC-ROC** | 0.8626 |
| **F1 Score** | 0.616 |
| **Precision** | 67.35% |
| **Recall** | 56.76% |
| **CV AUC (5-fold)** | 0.856 ± 0.005 |

## Architecture

`Request → Pydantic Validation → ColumnTransformer(SimpleImputer + StandardScaler + OneHotEncoder) → VotingClassifier(LR + RF, soft voting) → Prediction + Risk Level`

## Key Features

- **SHAP Explainability**: CPU-only, lazy via `?explain=true`
- **Drift Detection**: Evidently AI (PSI/KS monitoring)
- **Unified Pipeline**: Single `model.joblib` (preprocessor + model)
- **Fairness Analysis**: By geography and age group

## Operational

| Metric | Value |
|--------|-------|
| Test Coverage | 88% (168 tests) |
| Docker Image | 2.11 GB (with SHAP 0.50.0) |
| Model Size | 4.1 MB |
| P95 Latency | <250ms |

## API

```bash
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"CreditScore":650,"Geography":"France","Gender":"Male","Age":40,"Tenure":5,"Balance":60000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":50000}'
```

---

*Last Updated: March 2026*
