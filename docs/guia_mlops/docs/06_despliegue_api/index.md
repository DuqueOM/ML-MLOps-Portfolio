# 06 — Despliegue API

> **Tiempo estimado**: 3 días (24 horas)
> 
> **Prerrequisitos**: Módulos 01-05 completados

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Crear una **API REST con FastAPI**
2. ✅ Definir **schemas Pydantic** para request/response
3. ✅ Implementar **tests de integración** para la API
4. ✅ Crear un **Dockerfile** para containerizar

---

## 📖 Contenido Teórico

### 1. FastAPI Básico

```python
"""app/main.py — API principal."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import joblib
import numpy as np

# Crear app
app = FastAPI(
    title="Churn Prediction API",
    description="API para predicción de abandono de clientes",
    version="1.0.0",
)


# ===== Schemas =====
class CustomerInput(BaseModel):
    """Input para predicción."""
    
    age: int = Field(..., ge=18, le=120, description="Edad del cliente")
    balance: float = Field(..., ge=0, description="Balance de la cuenta")
    tenure: int = Field(..., ge=0, description="Meses como cliente")
    num_products: int = Field(..., ge=1, le=4, description="Número de productos")
    is_active: bool = Field(..., description="Si el cliente está activo")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "age": 35,
                    "balance": 50000.0,
                    "tenure": 24,
                    "num_products": 2,
                    "is_active": True,
                }
            ]
        }
    }


class PredictionOutput(BaseModel):
    """Output de predicción."""
    
    customer_id: Optional[str] = None
    churn_probability: float = Field(..., ge=0, le=1)
    churn_prediction: bool
    confidence: str = Field(..., description="low/medium/high")


class HealthResponse(BaseModel):
    """Response de health check."""
    
    status: str
    model_loaded: bool
    version: str


# ===== Cargar modelo =====
MODEL_PATH = "models/pipeline.pkl"
model = None

@app.on_event("startup")
async def load_model():
    """Carga el modelo al iniciar."""
    global model
    try:
        model = joblib.load(MODEL_PATH)
    except FileNotFoundError:
        print(f"⚠️ Modelo no encontrado en {MODEL_PATH}")


# ===== Endpoints =====
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Verifica el estado de la API."""
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        version="1.0.0",
    )


@app.post("/predict", response_model=PredictionOutput, tags=["Prediction"])
async def predict(customer: CustomerInput):
    """Realiza una predicción de churn."""
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    # Preparar features
    features = np.array([[
        customer.age,
        customer.balance,
        customer.tenure,
        customer.num_products,
        int(customer.is_active),
    ]])
    
    # Predecir
    probability = model.predict_proba(features)[0, 1]
    prediction = probability > 0.5
    
    # Calcular confianza
    if probability < 0.3 or probability > 0.7:
        confidence = "high"
    elif probability < 0.4 or probability > 0.6:
        confidence = "medium"
    else:
        confidence = "low"
    
    return PredictionOutput(
        churn_probability=round(probability, 4),
        churn_prediction=prediction,
        confidence=confidence,
    )


@app.post("/predict/batch", tags=["Prediction"])
async def predict_batch(customers: list[CustomerInput]):
    """Predicción en batch."""
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    results = []
    for customer in customers:
        result = await predict(customer)
        results.append(result)
    
    return results
```

---

### 2. Tests de Integración

```python
"""tests/test_api.py — Tests de la API."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Cliente de test."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests para /health."""
    
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_response_schema(self, client):
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "version" in data


class TestPredictEndpoint:
    """Tests para /predict."""
    
    @pytest.fixture
    def valid_customer(self):
        return {
            "age": 35,
            "balance": 50000.0,
            "tenure": 24,
            "num_products": 2,
            "is_active": True,
        }
    
    def test_predict_returns_200(self, client, valid_customer):
        response = client.post("/predict", json=valid_customer)
        # 200 si modelo cargado, 503 si no
        assert response.status_code in [200, 503]
    
    def test_predict_invalid_age(self, client, valid_customer):
        valid_customer["age"] = 150  # Inválido
        response = client.post("/predict", json=valid_customer)
        assert response.status_code == 422
    
    def test_predict_missing_field(self, client):
        incomplete = {"age": 35}  # Faltan campos
        response = client.post("/predict", json=incomplete)
        assert response.status_code == 422
    
    def test_predict_response_schema(self, client, valid_customer):
        response = client.post("/predict", json=valid_customer)
        if response.status_code == 200:
            data = response.json()
            assert "churn_probability" in data
            assert "churn_prediction" in data
            assert "confidence" in data
            assert 0 <= data["churn_probability"] <= 1
```

---

### 3. Dockerfile

```dockerfile
# Dockerfile — Multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependencias de build
RUN pip install --no-cache-dir --upgrade pip

# Copiar requirements
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ===== Stage final =====
FROM python:3.11-slim

WORKDIR /app

# Crear usuario non-root
RUN useradd --create-home --shell /bin/bash appuser

# Instalar dependencias desde wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copiar código
COPY app/ ./app/
COPY models/ ./models/

# Cambiar a usuario non-root
USER appuser

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 4. Docker Compose (Desarrollo)

```yaml
# docker-compose.yml
version: "3.8"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models:ro
    environment:
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 🔧 Mini-Proyecto: API de Predicción

### Objetivo

1. Crear API FastAPI con endpoint `/predict`
2. Definir schemas Pydantic
3. Escribir tests de integración
4. Crear Dockerfile

### Estructura

```
work/06_despliegue_api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── schemas.py
├── models/
│   └── pipeline.pkl
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── pyproject.toml
```

### Comandos

```bash
# Ejecutar localmente
uvicorn app.main:app --reload

# Ejecutar tests
pytest tests/ -v

# Build Docker
docker build -t churn-api .

# Run Docker
docker run -p 8000:8000 churn-api
```

### Criterios de Éxito

- [ ] API responde en http://localhost:8000/docs
- [ ] `/health` retorna status "healthy"
- [ ] `/predict` acepta input válido
- [ ] Tests pasan

---

## ✅ Validación

```bash
make check-06
```

---

## ➡️ Siguiente Módulo

**[07 — Dashboard](../07_dashboard/index.md)**

---

*Última actualización: 2024-12*
