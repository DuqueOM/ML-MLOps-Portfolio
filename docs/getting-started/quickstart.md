# Quick Start Guide

Get the ML-MLOps Portfolio running in under 5 minutes.

## Prerequisites

- **Docker** and **Docker Compose** installed
- **Git** for cloning the repository
- (Optional) **Python 3.11+** for local development

## One-Command Demo

The fastest way to see the portfolio in action:

```bash
# Clone the repository
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio

# Generate demo models (required for first run)
bash scripts/setup_demo_models.sh

# Start the full demo stack
docker-compose -f docker-compose.demo.yml up -d --build

# Verify all services are running
docker-compose -f docker-compose.demo.yml ps
```

## Access Points

Once the stack is running, access the services:

| Service | URL | Description |
|---------|-----|-------------|
| **BankChurn API** | [http://localhost:8001/docs](http://localhost:8001/docs) | Swagger UI for churn prediction |
| **CarVision API** | [http://localhost:8002/docs](http://localhost:8002/docs) | Swagger UI for price prediction |
| **CarVision Dashboard** | [http://localhost:8501](http://localhost:8501) | Interactive Streamlit dashboard |
| **TelecomAI API** | [http://localhost:8003/docs](http://localhost:8003/docs) | Swagger UI for plan recommendations |
| **MLflow UI** | [http://localhost:5000](http://localhost:5000) | Experiment tracking interface |

## Test the APIs

### BankChurn Prediction

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

**Expected Response:**
```json
{
  "prediction": 0,
  "probability": 0.23,
  "risk_level": "low"
}
```

### CarVision Price Prediction

```bash
curl -X POST "http://localhost:8002/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "model_year": 2020,
    "model": "ford f-150",
    "condition": "excellent",
    "odometer": 25000,
    "fuel": "gas",
    "transmission": "automatic"
  }'
```

### TelecomAI Plan Recommendation

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

## Run Integration Tests

Verify all services are working correctly:

```bash
bash scripts/run_demo_tests.sh
```

## Stop the Demo

```bash
docker-compose -f docker-compose.demo.yml down
```

## Next Steps

- [Installation Guide](installation.md) - Detailed setup instructions
- [Development Setup](development.md) - Set up local development environment
- [Project Overview](../projects/overview.md) - Deep dive into each project

---

!!! tip "Troubleshooting"
    If services fail to start, check the logs:
    ```bash
    docker-compose -f docker-compose.demo.yml logs --tail 50
    ```
    
    Common issues:
    
    - **Port conflicts**: Ensure ports 5000, 8001-8003, 8501 are available
    - **Missing models**: Run `scripts/setup_demo_models.sh` first
    - **Memory**: Ensure at least 4GB RAM available for Docker
