# REST API Reference

All services expose FastAPI with automatic Swagger UI at `/docs`, Prometheus metrics at `/metrics`, and health checks at `/health`.

| BankChurn Swagger | NLPInsight Swagger | ChicagoTaxi Swagger |
|:---:|:---:|:---:|
| ![BankChurn](../media/screenshots/apis/25-fastapi-swagger-bankchurn.png) | ![NLPInsight](../media/screenshots/apis/27-fastapi-swagger-nlpinsight.png) | ![ChicagoTaxi](../media/screenshots/apis/29-fastapi-swagger-chicagotaxi.png) |

## Endpoints

### BankChurn (`:8001`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/predict` | Churn prediction (add `?explain=true` for SHAP contributions) |
| GET | `/metrics` | Prometheus metrics |
| GET | `/docs` | Swagger UI |

**Predict Request:**
```json
{"CreditScore":650,"Geography":"France","Gender":"Male","Age":40,"Tenure":5,"Balance":60000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":50000}
```

**Response:**
```json
{"prediction":0,"probability":0.15,"risk_level":"LOW"}
```

### NLPInsight (`:8003`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/predict` | Sentiment analysis |
| GET | `/metrics` | Prometheus metrics |
| GET | `/docs` | Swagger UI |

**Predict Request:**
```json
{"text":"The company reported strong quarterly earnings growth"}
```

**Response:**
```json
{"label":"positive","confidence":0.92,"scores":{"positive":0.92,"neutral":0.06,"negative":0.02}}
```

### ChicagoTaxi (`:8004`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/demand` | Query demand predictions by area/hour |
| GET | `/areas` | List all areas ranked by demand |
| GET | `/pipeline/status` | ETL pipeline metadata |
| GET | `/metrics` | Prometheus metrics |
| GET | `/docs` | Swagger UI |

**Demand Request:**
```bash
curl "http://localhost:8004/demand?area=8&hour=14&limit=5"
```

**Response:**
```json
{"predictions":[{"pickup_community_area":8,"hour":14,"predicted_demand":42.3}],"total":1}
```

## Live Predictions

| BankChurn (with SHAP) | NLPInsight (Sentiment) | ChicagoTaxi (Demand) |
|:---:|:---:|:---:|
| ![BankChurn](../media/screenshots/apis/26-bankchurn-prediccion-real.png) | ![NLPInsight](../media/screenshots/apis/28-nlpinsight-prediccion.png) | ![ChicagoTaxi](../media/screenshots/apis/30-chicagotaxi-prediccion.png) |

| SHAP Explanation | Prometheus Metrics |
|:---:|:---:|
| ![SHAP](../media/screenshots/apis/82-shap-prediction-response.png) | ![Metrics](../media/screenshots/apis/32-metrics-endpoint.png) |

## Common Patterns

- **Health Check**: All services return `{"status":"healthy"}` at `/health`
- **Metrics**: Prometheus format at `/metrics` — custom counters per service
- **Validation**: Pydantic schemas with automatic 422 error responses
- **CORS**: Enabled for all origins
- **Structured Logging**: JSON format in K8s, human-readable locally

---

*Last Updated: March 2026 — v3.5.3*
