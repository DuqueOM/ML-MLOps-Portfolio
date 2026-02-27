# REST API Reference

All projects expose REST APIs via FastAPI with automatic OpenAPI documentation.

![Metrics Endpoint](../media/screenshots/apis/32-metrics-endpoint.png)
*Prometheus metrics endpoint (`/metrics`) exposed by each service*

## Common Endpoints

All APIs share these standard endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI (interactive) |
| `/redoc` | GET | ReDoc UI (static) |
| `/openapi.json` | GET | OpenAPI specification |

### Health Check Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-25T12:00:00Z"
}
```

---

## BankChurn API (Port 8001)

**Base URL**: `http://localhost:8001`

### POST /predict

Predict customer churn probability.

#### Request Body

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `CreditScore` | integer | Yes | Customer credit score | 300-850 |
| `Geography` | string | Yes | Customer country | France, Germany, Spain |
| `Gender` | string | Yes | Customer gender | Male, Female |
| `Age` | integer | Yes | Customer age | 18-100 |
| `Tenure` | integer | Yes | Years as customer | 0-10 |
| `Balance` | float | Yes | Account balance | ≥0 |
| `NumOfProducts` | integer | Yes | Number of products | 1-4 |
| `HasCrCard` | integer | Yes | Has credit card | 0 or 1 |
| `IsActiveMember` | integer | Yes | Is active member | 0 or 1 |
| `EstimatedSalary` | float | Yes | Estimated salary | ≥0 |

#### Example Request

```bash
curl -X POST "http://localhost:8001/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "CreditScore": 650,
    "Geography": "France",
    "Gender": "Female",
    "Age": 40,
    "Tenure": 3,
    "Balance": 60000.0,
    "NumOfProducts": 2,
    "HasCrCard": 1,
    "IsActiveMember": 1,
    "EstimatedSalary": 50000.0
  }'
```

#### Success Response (200 OK)

```json
{
  "prediction": 0,
  "probability": 0.23,
  "risk_level": "low"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `prediction` | integer | 0 = No churn, 1 = Churn |
| `probability` | float | Churn probability (0-1) |
| `risk_level` | string | low (<0.3), medium (0.3-0.7), high (>0.7) |

#### Error Responses

**422 Validation Error**

```json
{
  "detail": [
    {
      "loc": ["body", "CreditScore"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

**500 Internal Server Error**

```json
{
  "detail": "Model inference failed: [error message]"
}
```

### POST /predict/batch

Predict churn for multiple customers.

#### Example Request

```bash
curl -X POST "http://localhost:8001/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "customers": [
      {"CreditScore": 650, "Geography": "France", "Gender": "Female", "Age": 40, "Tenure": 3, "Balance": 60000, "NumOfProducts": 2, "HasCrCard": 1, "IsActiveMember": 1, "EstimatedSalary": 50000},
      {"CreditScore": 500, "Geography": "Germany", "Gender": "Male", "Age": 55, "Tenure": 1, "Balance": 0, "NumOfProducts": 1, "HasCrCard": 0, "IsActiveMember": 0, "EstimatedSalary": 30000}
    ]
  }'
```

#### Success Response

```json
{
  "predictions": [
    {"prediction": 0, "probability": 0.23, "risk_level": "low"},
    {"prediction": 1, "probability": 0.78, "risk_level": "high"}
  ],
  "count": 2
}
```

---

## CarVision API (Port 8002)

**Base URL**: `http://localhost:8002`

### POST /predict

Predict vehicle price.

#### Request Body

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `model_year` | integer | Yes | Vehicle model year | 2020 |
| `model` | string | Yes | Vehicle model name | "ford f-150" |
| `condition` | string | Yes | Vehicle condition | excellent, good, fair, salvage |
| `odometer` | integer | Yes | Mileage in miles | 25000 |
| `fuel` | string | Yes | Fuel type | gas, diesel, electric, hybrid |
| `transmission` | string | Yes | Transmission type | automatic, manual |
| `manufacturer` | string | No | Vehicle manufacturer | ford, toyota, honda |
| `cylinders` | string | No | Engine cylinders | "6 cylinders" |
| `drive` | string | No | Drive type | 4wd, fwd, rwd |
| `type` | string | No | Vehicle type | sedan, SUV, truck |
| `paint_color` | string | No | Exterior color | white, black, silver |

#### Example Request

```bash
curl -X POST "http://localhost:8002/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "model_year": 2020,
    "model": "ford f-150",
    "condition": "excellent",
    "odometer": 25000,
    "fuel": "gas",
    "transmission": "automatic",
    "manufacturer": "ford",
    "type": "truck"
  }'
```

#### Success Response (200 OK)

```json
{
  "predicted_price": 35420.50,
  "prediction_timestamp": "2026-02-27T16:00:00Z"
}
```

### POST /predict_batch

Predict prices for multiple vehicles (max 500).

#### Example Request

```bash
curl -X POST "http://localhost:8002/predict_batch" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicles": [
      {"model_year": 2020, "model": "ford f-150", "condition": "excellent", "odometer": 25000},
      {"model_year": 2018, "model": "toyota camry", "condition": "good", "odometer": 45000}
    ]
  }'
```

#### Success Response

```json
{
  "predictions": [
    {"predicted_price": 35420.50, "prediction_timestamp": "2026-02-27T16:00:00Z"},
    {"predicted_price": 22150.00, "prediction_timestamp": "2026-02-27T16:00:00Z"}
  ],
  "batch_id": "batch_1740700800",
  "total_vehicles": 2,
  "processing_time_seconds": 0.045
}
```

---

## TelecomAI API (Port 8003)

**Base URL**: `http://localhost:8003`

### POST /predict

Predict plan upgrade recommendation.

#### Request Body

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `calls` | float | Yes | Number of calls made | ≥0 |
| `minutes` | float | Yes | Total call minutes | ≥0 |
| `messages` | float | Yes | Number of SMS sent | ≥0 |
| `mb_used` | float | Yes | Data usage in MB | ≥0 |

#### Example Request

```bash
curl -X POST "http://localhost:8003/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "calls": 50,
    "minutes": 500.0,
    "messages": 100,
    "mb_used": 20000.0
  }'
```

#### Success Response (200 OK)

```json
{
  "prediction": 1,
  "plan": "Ultra",
  "probability_is_ultra": 0.78,
  "feature_importance": {
    "calls": 0.15,
    "minutes": 0.35,
    "messages": 0.12,
    "mb_used": 0.38
  },
  "prediction_timestamp": "2026-02-27T16:00:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `prediction` | integer | 0 = Standard, 1 = Ultra |
| `plan` | string | Human-readable plan name |
| `probability_is_ultra` | float | Ultra plan probability (0-1) |
| `feature_importance` | object | Feature importance scores from the model |

### POST /predict_batch

Predict plan for multiple customers (max 500).

#### Example Request

```bash
curl -X POST "http://localhost:8003/predict_batch" \
  -H "Content-Type: application/json" \
  -d '{
    "customers": [
      {"calls": 50, "minutes": 500.0, "messages": 100, "mb_used": 20000.0},
      {"calls": 10, "minutes": 100.0, "messages": 20, "mb_used": 5000.0}
    ]
  }'
```

#### Success Response

```json
{
  "predictions": [
    {"prediction": 1, "plan": "Ultra", "probability_is_ultra": 0.78, "feature_importance": {}, "prediction_timestamp": "2026-02-27T16:00:00Z"},
    {"prediction": 0, "plan": "Standard", "probability_is_ultra": 0.22, "feature_importance": {}, "prediction_timestamp": "2026-02-27T16:00:00Z"}
  ],
  "batch_id": "batch_1740700800",
  "total_customers": 2,
  "processing_time_seconds": 0.012
}
```

---

## Authentication

!!! note "Current Status"
    These APIs currently do not require authentication for demonstration purposes.
    In production, implement API key or OAuth2 authentication.

### Recommended Production Setup

```python
# Example: API Key authentication header
headers = {
    "X-API-Key": "your-api-key-here",
    "Content-Type": "application/json"
}
```

---

## Rate Limiting

| Environment | Limit | Window |
|-------------|-------|--------|
| Demo | 100 requests | per minute |
| Production | Configurable | per API key |

---

## SDK Examples

### Python

```python
import requests

def predict_churn(customer_data: dict) -> dict:
    response = requests.post(
        "http://localhost:8001/predict",
        json=customer_data
    )
    response.raise_for_status()
    return response.json()

# Usage
result = predict_churn({
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
})
print(f"Churn risk: {result['risk_level']}")
```

### JavaScript

```javascript
async function predictChurn(customerData) {
  const response = await fetch('http://localhost:8001/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(customerData)
  });
  return response.json();
}

// Usage
const result = await predictChurn({
  CreditScore: 650,
  Geography: "France",
  Gender: "Female",
  Age: 40,
  Tenure: 3,
  Balance: 60000,
  NumOfProducts: 2,
  HasCrCard: 1,
  IsActiveMember: 1,
  EstimatedSalary: 50000
});
console.log(`Churn risk: ${result.risk_level}`);
```

---

## OpenAPI Specification

Each API provides a complete OpenAPI 3.0 specification:

- **BankChurn**: http://localhost:8001/openapi.json
- **CarVision**: http://localhost:8002/openapi.json
- **TelecomAI**: http://localhost:8003/openapi.json

Download and import into Postman, Insomnia, or other API clients for interactive testing

---

**Last Updated**: February 2026
