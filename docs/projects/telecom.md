# TelecomAI Customer Intelligence

Strategic customer intelligence for telecommunications.

<!-- MEDIA PLACEHOLDER: Demo GIF pending -->
<!-- To add: Record 6-8 second GIF showing API request/response -->
<!-- Path: media/gifs/telecom-demo.gif -->

![TelecomAI API Demo](../media/gifs/telecom-demo.gif){ .off-glb style="display:none" }

## Overview

**TelecomAI Customer Intelligence** predicts whether customers should be recommended an upgraded plan based on their usage patterns. It demonstrates advanced ensemble methods with VotingClassifier and domain-specific feature engineering.

## Model Performance

### Production Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| **AUC-ROC** | 0.840 | Area under ROC curve |
| **Accuracy** | 81.2% | Overall classification accuracy |
| **Precision** | 81.7% | Positive predictive value |
| **Recall** | 49.7% | True positive rate |
| **F1 Score** | 0.618 | Harmonic mean of precision/recall |

### Model Interpretation

```mermaid
graph TD
    subgraph "Prediction Distribution"
        A["81.2% Accuracy"] --> B["High Precision<br/>81.7%"]
        A --> C["Conservative Recall<br/>49.7%"]
    end
    
    subgraph "Business Impact"
        B --> D["Low false positive rate<br/>Fewer wrong upgrades"]
        C --> E["May miss some<br/>upgrade candidates"]
    end
```

!!! tip "Business Insight"
    The model prioritizes precision over recall, meaning it's conservative about 
    recommending upgrades—reducing the risk of recommending expensive plans to 
    customers who won't benefit.

### Operational Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| **Test Coverage** | 96% | Unit + integration tests |
| **P95 Latency** | <30ms | Inference time |
| **Model Size** | ~1.5 MB | Serialized pipeline |

## Quick Start

### Using Docker

```bash
cd TelecomAI-Customer-Intelligence
docker build -t telecom:latest .
docker run -p 8000:8000 telecom:latest
```

### API Access

http://localhost:8003/docs

## API Reference

### Predict Endpoint

**POST** `/predict`

```bash
curl -X POST "http://localhost:8003/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "calls": 50,
    "minutes": 500,
    "messages": 100,
    "mb_used": 20000,
    "is_ultimate": 0
  }'
```

**Response:**

```json
{
  "prediction": 1,
  "probability": 0.78,
  "recommendation": "upgrade_recommended"
}
```

## Model Architecture

```mermaid
graph LR
    INPUT["Usage Metrics"] --> FE["Feature Engineering"]
    FE --> PRE["Preprocessing"]
    PRE --> VC["VotingClassifier"]
    
    subgraph "Ensemble"
        LR["LogisticRegression"]
        RF["RandomForest"]
        XGB["XGBoost"]
    end
    
    VC --> LR
    VC --> RF
    VC --> XGB
    
    LR --> VOTE["Soft Voting"]
    RF --> VOTE
    XGB --> VOTE
    
    VOTE --> PRED["Prediction"]
```

## Configuration

```yaml
# configs/config.yaml
data:
  train_path: "data/raw/telecom.csv"
  target_column: "is_ultra"

model:
  voting: "soft"
  estimators:
    - logistic_regression
    - random_forest
```

## Project Structure

```
TelecomAI-Customer-Intelligence/
├── src/telecom/
│   ├── __init__.py
│   ├── data.py           # Data loading
│   ├── training.py       # Model training
│   ├── prediction.py     # Batch inference
│   └── evaluation.py     # Metrics
├── app/
│   └── fastapi_app.py    # REST API
├── tests/
├── configs/
└── Dockerfile
```

## Known Limitations

1. **Single Carrier**: Model trained on specific carrier data
2. **Usage Only**: Doesn't consider customer demographics
3. **Binary Output**: Only upgrade/no-upgrade recommendation

## Related Documentation

- [Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/TelecomAI-Customer-Intelligence/models/model_card.md)
- [API Reference](../api/rest-apis.md)
