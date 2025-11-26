# BankChurn Predictor

Customer churn prediction system for banking institutions.

<!-- MEDIA PLACEHOLDER: Demo GIF pending -->
<!-- To add: Record 6-8 second GIF showing API request/response -->
<!-- Path: media/gifs/bankchurn-demo.gif -->
<!-- ![BankChurn API Demo](../media/gifs/bankchurn-demo.gif){ .off-glb } -->

## Overview

**BankChurn Predictor** is a production-ready machine learning system that predicts customer churn probability for banking customers. It demonstrates enterprise-grade practices including MLflow experiment tracking, Pydantic configuration validation, and comprehensive testing.

## Model Performance

### Production Metrics (Test Set)

| Metric | Value | Description |
|--------|-------|-------------|
| **AUC-ROC** | 0.853 | Area under ROC curve |
| **Accuracy** | 85.7% | Overall classification accuracy |
| **Precision** | 69.2% | Positive predictive value |
| **Recall** | 53.6% | True positive rate |
| **F1 Score** | 0.604 | Harmonic mean of precision/recall |

### Cross-Validation Results (5-Fold)

| Metric | Mean | Std Dev |
|--------|------|---------|
| **AUC-ROC** | 0.844 | ±0.018 |
| **F1 Score** | 0.596 | ±0.031 |
| **Precision** | 0.672 | ±0.026 |
| **Recall** | 0.537 | ±0.038 |

### Confusion Matrix

```
              Predicted
              Neg    Pos
Actual Neg   1496    97
       Pos    189   218
```

### Operational Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| **Test Coverage** | 78% | Unit + integration tests |
| **P95 Latency** | <50ms | Inference time |
| **Model Size** | ~2 MB | Serialized pipeline |

## Quick Start

### Using Docker

```bash
cd BankChurn-Predictor
docker build -t ml-portfolio-bankchurn:latest .
docker run -p 8001:8000 ml-portfolio-bankchurn:latest
```

### Using Python

```bash
cd BankChurn-Predictor
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m bankchurn.cli train --config configs/config.yaml
```

## API Reference

### Predict Endpoint

**POST** `/predict`

```bash
curl -X POST "http://localhost:8001/predict" \
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

**Response:**

```json
{
  "prediction": 0,
  "probability": 0.23,
  "risk_level": "low"
}
```

### Health Endpoint

**GET** `/health`

```json
{"status": "healthy", "version": "1.0.0"}
```

## Model Architecture

```mermaid
graph LR
    INPUT["Customer Data"] --> VAL["Pydantic Validation"]
    VAL --> PRE["ColumnTransformer<br/>(Imputer + Scaler + OneHot)"]
    PRE --> ENS["VotingClassifier<br/>(LR + RF + XGB)"]
    ENS --> PRED["Churn Probability"]
    PRED --> RISK["Risk Level<br/>(low/medium/high)"]
```

### Pipeline Components

1. **Preprocessing (`ColumnTransformer`)**
   - Numerical: `SimpleImputer(median)` → `StandardScaler`
   - Categorical: `SimpleImputer(constant)` → `OneHotEncoder`

2. **Model (`VotingClassifier`)**
   - Logistic Regression
   - Random Forest
   - XGBoost (optional)

3. **Post-processing**
   - Probability → Risk Level mapping
   - Threshold customization support

## Configuration

Configuration is managed via Pydantic models in `configs/config.yaml`:

```yaml
data:
  train_path: "data/raw/train.csv"
  target_column: "Exited"
  categorical_features:
    - Geography
    - Gender
  numerical_features:
    - CreditScore
    - Age
    - Balance
    - EstimatedSalary

model:
  logistic_regression:
    C: 1.0
    max_iter: 1000
  random_forest:
    n_estimators: 100
    max_depth: 10
```

## Training

### CLI

```bash
python -m bankchurn.cli train --config configs/config.yaml
```

### Programmatic

```python
from bankchurn.training import ChurnTrainer
from bankchurn.config import BankChurnConfig

config = BankChurnConfig.from_yaml("configs/config.yaml")
trainer = ChurnTrainer(config)
trainer.train()
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/bankchurn --cov-report=html

# Run specific test file
pytest tests/test_training.py -v
```

## Project Structure

```
BankChurn-Predictor/
├── src/bankchurn/          # Core package
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Pydantic configuration
│   ├── training.py         # Training logic
│   ├── prediction.py       # Inference logic
│   ├── evaluation.py       # Metrics computation
│   └── models.py           # Custom model wrappers
├── app/
│   └── fastapi_app.py      # REST API
├── tests/                  # Test suite
├── configs/                # YAML configs
├── models/                 # Saved models
│   └── model_card.md       # Model documentation
└── Dockerfile              # Multi-stage build
```

## Known Limitations

1. **Imbalanced Classes**: Uses class weights; SMOTE available but not default
2. **Feature Engineering**: Limited to basic preprocessing
3. **Explainability**: Basic feature importance; SHAP not integrated

## Related Documentation

- [Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/BankChurn-Predictor/models/model_card.md)
- [API Reference](../api/rest-apis.md)
- [Deployment Guide](../operations/deployment.md)
