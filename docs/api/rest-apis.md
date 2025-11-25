# REST API Reference

All projects expose REST APIs via FastAPI with automatic OpenAPI documentation.

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
  "currency": "USD",
  "confidence": {
    "lower_bound": 32500.00,
    "upper_bound": 38340.00
  },
  "model_version": "1.0.0"
}
```

#### Error Responses

**422 Validation Error**

```json
{
  "detail": [
    {
      "loc": ["body", "model_year"],
      "msg": "ensure this value is greater than 1900",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### GET /analyze/market

Get market analysis summary.

#### Example Request

```bash
curl -X GET "http://localhost:8002/analyze/market"
```

#### Success Response

```json
{
  "total_vehicles": 51525,
  "average_price": 18543.21,
  "price_range": {
    "min": 1000,
    "max": 450000
  },
  "top_brands": [
    {"brand": "ford", "count": 8234},
    {"brand": "chevrolet", "count": 7123},
    {"brand": "toyota", "count": 5432}
  ]
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
| `calls` | integer | Yes | Number of calls made | ≥0 |
| `minutes` | float | Yes | Total call minutes | ≥0 |
| `messages` | integer | Yes | Number of SMS sent | ≥0 |
| `mb_used` | float | Yes | Data usage in MB | ≥0 |
| `is_ultimate` | integer | Yes | Current plan type | 0=Smart, 1=Ultimate |

#### Example Request

```bash
curl -X POST "http://localhost:8003/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "calls": 50,
    "minutes": 500.0,
    "messages": 100,
    "mb_used": 20000.0,
    "is_ultimate": 0
  }'
```

#### Success Response (200 OK)

```json
{
  "prediction": 1,
  "probability": 0.78,
  "recommendation": "upgrade_recommended",
  "confidence": "high"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `prediction` | integer | 0 = Keep current, 1 = Upgrade |
| `probability` | float | Upgrade probability (0-1) |
| `recommendation` | string | Human-readable recommendation |
| `confidence` | string | low, medium, high |

#### Interpretation Guide

| Probability Range | Confidence | Recommendation |
|-------------------|------------|----------------|
| 0.0 - 0.3 | High | Keep current plan |
| 0.3 - 0.5 | Low | Consider reviewing usage |
| 0.5 - 0.7 | Medium | Upgrade may be beneficial |
| 0.7 - 1.0 | High | Upgrade recommended |

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
