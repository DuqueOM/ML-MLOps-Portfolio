# REST API Reference

All services expose FastAPI with automatic Swagger UI at `/docs`.

## Endpoints

### BankChurn (`:8001`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/predict` | Churn prediction |
| GET | `/docs` | Swagger UI |

**Predict Request:**
```json
{"CreditScore":650,"Geography":"France","Gender":"Male","Age":40,"Tenure":5,"Balance":60000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":50000}
```

**Response:**
```json
{"prediction":0,"probability":0.15,"risk_level":"LOW"}
```

### CarVision (`:8002`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/predict` | Price prediction |
| GET | `/docs` | Swagger UI |

**Predict Request:**
```json
{"model_year":2020,"odometer":30000,"fuel":"gas","transmission":"automatic","type":"sedan","condition":"excellent"}
```

**Response:**
```json
{"predicted_price":25430.50}
```

### NLPInsight (`:8003`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/predict` | Sentiment analysis |
| GET | `/docs` | Swagger UI |

**Predict Request:**
```json
{"text":"The company reported strong quarterly earnings growth"}
```

**Response:**
```json
{"label":"positive","confidence":0.92,"scores":{"positive":0.92,"neutral":0.06,"negative":0.02}}
```

## Common Patterns

- **Health Check**: All services return `{"status":"healthy"}` at `/health`
- **Metrics**: Prometheus format at `/metrics`
- **Validation**: Pydantic schemas with automatic 422 error responses
- **CORS**: Enabled for all origins

---

*Last Updated: March 2026*
