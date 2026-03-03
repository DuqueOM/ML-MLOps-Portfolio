# BankChurn Predictor

Customer churn prediction for banking institutions.

![BankChurn API](../media/screenshots/apis/25-fastapi-swagger-bankchurn.png)

## Performance (v3.3.0)

| Metric | Value |
|--------|-------|
| **AUC-ROC** | 0.87 |
| **F1 Score** | 0.62 |

## Architecture

`Request → Pydantic Validation → ColumnTransformer(SimpleImputer + StandardScaler + OneHotEncoder) → StackingClassifier(RF+GB+XGB+LGB→LR) → Prediction + Risk Level`

## Key Features

- **SHAP Explainability**: CPU-only, lazy via `?explain=true`
- **Drift Detection**: Evidently AI (PSI/KS monitoring)
- **Unified Pipeline**: Single `model.joblib` (preprocessor + model)
- **Fairness Audits**: Disparate impact ratio, equal opportunity difference (by Gender, Geography)
- **Data Validation**: Pandera schemas (raw + inference)

## Operational

| Metric | Value |
|--------|-------|
| Test Coverage | 90% (198 tests) |
| Docker Image | 1.09 GB (optimized, -48%) |
| Model Size | 4.1 MB |
| P95 Latency | <360ms (K8s port-forward) |

## API

```bash
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"CreditScore":650,"Geography":"France","Gender":"Male","Age":40,"Tenure":5,"Balance":60000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":50000}'
```

---

*Last Updated: March 2026 — v3.3.0*
