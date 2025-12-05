# ✅ Soluciones — Ejercicios Guía MLOps

> **Soluciones detalladas con explicaciones**

---

## Módulo 01: Python Moderno

### Solución 1.1: Type Hints

```python
from typing import Any
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

def load_data(path: str) -> pd.DataFrame:
    """Load CSV data from path."""
    return pd.read_csv(path)

def train_model(
    X: pd.DataFrame, 
    y: np.ndarray, 
    params: dict[str, Any]
) -> RandomForestClassifier:
    """Train RandomForest with given parameters."""
    model = RandomForestClassifier(**params)
    return model.fit(X, y)
```

**Explicación**: Los type hints documentan qué tipos espera y retorna cada función, facilitando el mantenimiento y detectando errores con mypy.

---

### Solución 1.2: Pydantic Config

```python
from pydantic import BaseModel, Field

class ModelConfig(BaseModel):
    """Configuration for RandomForest model."""
    
    n_estimators: int = Field(
        default=100,
        ge=10,
        le=500,
        description="Number of trees in the forest"
    )
    max_depth: int | None = Field(
        default=None,
        ge=1,
        le=50,
        description="Maximum depth of trees"
    )
    random_state: int = Field(
        default=42,
        description="Random seed for reproducibility"
    )

# Uso:
config = ModelConfig(n_estimators=200, max_depth=10)
# Validación automática - esto fallaría:
# config = ModelConfig(n_estimators=1000)  # Error: > 500
```

---

## Módulo 07: sklearn Pipelines

### Solución 7.1: Pipeline Básico

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("model", RandomForestClassifier(n_estimators=100, random_state=42))
])

# Uso:
pipe.fit(X_train, y_train)
predictions = pipe.predict(X_test)
```

---

### Solución 7.2: ColumnTransformer

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

numeric_cols = ['age', 'balance', 'salary']
categorical_cols = ['geography', 'gender']

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numeric_cols),
    ("cat", OneHotEncoder(handle_unknown='ignore'), categorical_cols)
])

# Pipeline completo:
pipe = Pipeline([
    ("preprocess", preprocessor),
    ("model", RandomForestClassifier())
])
```

---

### Solución 7.3: Custom Transformer

```python
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class AgeGroupTransformer(BaseEstimator, TransformerMixin):
    """Transform age into categorical groups."""
    
    def fit(self, X, y=None):
        return self  # Stateless transformer
    
    def transform(self, X):
        X = X.copy()
        X['age_group'] = pd.cut(
            X['age'],
            bins=[0, 30, 50, 100],
            labels=['young', 'middle', 'senior']
        )
        return X

# Uso en pipeline:
pipe = Pipeline([
    ("age_groups", AgeGroupTransformer()),
    ("preprocess", preprocessor),
    ("model", RandomForestClassifier())
])
```

---

## Módulo 08: Feature Engineering

### Solución 8.1: Detectar Data Leakage

```python
# ERROR 1: price_category usa el target (price) antes del split
# Esto causa TARGET LEAKAGE

# ERROR 2: StandardScaler se ajusta a TODO el dataset
# Esto causa TRAIN-TEST CONTAMINATION

# ERROR 3: No hay error aquí, pero los errores anteriores
# ya contaminaron los datos
```

---

### Solución 8.2: Pipeline Sin Leakage

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv('data.csv')

# CORRECCIÓN 1: NO crear price_category (depende del target)
# Si necesitas esta feature, créala SOLO con datos de training

# CORRECCIÓN 2: Split ANTES de cualquier transformación
X = df.drop('target', axis=1)
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

# CORRECCIÓN 3: Scaler DENTRO del pipeline
pipe = Pipeline([
    ("scaler", StandardScaler()),  # Se ajusta solo en fit()
    ("model", RandomForestClassifier())
])

# El scaler solo ve X_train durante fit
pipe.fit(X_train, y_train)
score = pipe.score(X_test, y_test)
```

---

## Módulo 11: Testing ML

### Solución 11.1: Test de Datos

```python
import pytest
import pandas as pd

def test_no_nulls(sample_data):
    """Critical columns should have no null values."""
    critical_cols = ['age', 'balance', 'target']
    for col in critical_cols:
        assert sample_data[col].isnull().sum() == 0, f"Nulls found in {col}"

def test_age_range(sample_data):
    """Age should be between 18 and 100."""
    assert sample_data['age'].min() >= 18, "Age below 18 found"
    assert sample_data['age'].max() <= 100, "Age above 100 found"

def test_target_binary(sample_data):
    """Target should only contain 0 and 1."""
    unique_values = set(sample_data['target'].unique())
    assert unique_values <= {0, 1}, f"Invalid target values: {unique_values}"
```

---

### Solución 11.2: Test de Modelo

```python
import numpy as np
from sklearn.metrics import accuracy_score

def test_model_fit(sample_data):
    """Model should fit without errors."""
    X = sample_data.drop('target', axis=1)
    y = sample_data['target']
    
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)  # Should not raise
    
    assert hasattr(model, 'classes_'), "Model not fitted"

def test_predictions_shape(trained_model, sample_data):
    """Predictions should match input shape."""
    X = sample_data.drop('target', axis=1)
    predictions = trained_model.predict(X)
    
    assert predictions.shape[0] == len(X), "Prediction count mismatch"

def test_accuracy_above_baseline(trained_model, sample_data):
    """Model should beat random baseline."""
    X = sample_data.drop('target', axis=1)
    y = sample_data['target']
    
    predictions = trained_model.predict(X)
    accuracy = accuracy_score(y, predictions)
    
    assert accuracy > 0.5, f"Accuracy {accuracy} below baseline 0.5"
```

---

### Solución 11.3: conftest.py

```python
# tests/conftest.py

import pytest
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

@pytest.fixture
def sample_data():
    """Generate sample data for testing."""
    np.random.seed(42)
    n_samples = 100
    
    return pd.DataFrame({
        'age': np.random.randint(18, 70, n_samples),
        'balance': np.random.uniform(0, 100000, n_samples),
        'salary': np.random.uniform(30000, 150000, n_samples),
        'target': np.random.randint(0, 2, n_samples)
    })

@pytest.fixture
def trained_model(sample_data):
    """Return a trained model."""
    X = sample_data.drop('target', axis=1)
    y = sample_data['target']
    
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    return model

@pytest.fixture
def config():
    """Return test configuration."""
    return {
        'model': {'n_estimators': 10, 'random_state': 42},
        'data': {'test_size': 0.2}
    }
```

---

## Módulo 12: CI/CD

### Solución 12.1: GitHub Actions

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -e ".[dev]"
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src/ --cov-report=xml --cov-fail-under=80
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

---

## Módulo 13: Docker

### Solución 13.1: Dockerfile Multi-stage

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir --upgrade pip

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/deps /usr/local/lib/python3.11/site-packages/

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser artifacts/ ./artifacts/

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Módulo 14: FastAPI

### Solución 14.1 y 14.2: Schemas y Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd

# Schemas
class PredictionRequest(BaseModel):
    age: int = Field(..., ge=18, le=100)
    balance: float = Field(..., ge=0)
    salary: float = Field(..., ge=0)
    geography: str = Field(..., pattern="^(France|Germany|Spain)$")
    gender: str = Field(..., pattern="^(Male|Female)$")

class PredictionResponse(BaseModel):
    prediction: int = Field(..., ge=0, le=1)
    probability: float = Field(..., ge=0, le=1)
    status: str = "success"

# App
app = FastAPI(title="ML Prediction API")

# Load model at startup
model = None

@app.on_event("startup")
async def load_model():
    global model
    model = joblib.load("artifacts/model.joblib")

@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame([request.model_dump()])
        
        # Get prediction and probability
        prediction = int(model.predict(df)[0])
        probability = float(model.predict_proba(df)[0, 1])
        
        return PredictionResponse(
            prediction=prediction,
            probability=probability
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Módulo 02: Diseño de Sistemas

### Solución 2.1: ML Canvas

```markdown
# ML Canvas: BankChurn-Predictor

## 1. Propuesta de Valor
- Reducir churn de clientes bancarios
- Impacto: Retener 15% más clientes = $2M/año ahorro estimado

## 2. Datos
- Fuente: Base de datos CRM bancaria (10K clientes)
- Features: CreditScore, Age, Balance, Geography, NumOfProducts, IsActiveMember

## 3. Modelo
- Tipo: Clasificación binaria (churn: 0/1)
- Métricas: ROC-AUC > 0.85, Recall > 0.75 (priorizar capturar churners)
- Baseline: 79.6% (predecir siempre "no churn")
```

### Solución 2.2: ADR

```markdown
# ADR-001: Elección de RandomForest sobre XGBoost

## Estado
Aceptado

## Contexto
Necesitamos un modelo para predicción de churn que sea interpretable y robusto.

## Opciones Consideradas
1. RandomForest - Interpretable, feature importances nativas
2. XGBoost - Mejor performance en benchmarks
3. LogisticRegression - Muy interpretable pero menos potente

## Decisión
RandomForest porque:
- Feature importances integradas (útil para equipo de negocio)
- No requiere tuning extensivo
- Buen balance accuracy/interpretabilidad

## Consecuencias
- Positivas: Fácil de explicar a stakeholders, pipeline simple
- Negativas: Puede perder 1-2% accuracy vs XGBoost tuneado
```

---

## Módulo 03: Estructura de Proyecto

### Solución 3.1: src/ Layout

```bash
mkdir -p fraud-detector/{src/frauddetector,tests,configs,app,artifacts}

# Crear archivos base
touch fraud-detector/src/frauddetector/{__init__,config,data,features,training,pipeline}.py
touch fraud-detector/tests/conftest.py
touch fraud-detector/configs/config.yaml
touch fraud-detector/{pyproject.toml,Makefile,README.md}
```

### Solución 3.2: pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "fraud-detector"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "pandas>=2.0",
    "scikit-learn>=1.3",
    "pydantic>=2.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0", "pytest-cov>=4.0", "ruff>=0.1"]

[project.scripts]
train = "frauddetector.training:main"
```

---

## Módulo 04: Entornos

### Solución 4.1: Makefile

```makefile
.PHONY: install test lint format train serve clean

install:
	pip install -e ".[dev]"

test:
	pytest tests/ --cov=src/frauddetector --cov-report=term-missing --cov-fail-under=80

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

train:
	python -m frauddetector.training --config configs/config.yaml

serve:
	uvicorn app.fastapi_app:app --reload --port 8000

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache htmlcov .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
```

---

## Módulo 05: Git Profesional

### Solución 5.1: Conventional Commits

```bash
# "fixed bug" → 
fix(pipeline): handle NaN values in categorical columns

# "added tests" →
test(training): add integration tests for cross-validation

# "updated readme" →
docs(readme): add quick start guide and badges

# "refactored code" →
refactor(features): extract FeatureEngineer to separate module
```

### Solución 5.2: Pre-commit Hooks

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
```

---

## Módulo 06: Versionado de Datos

### Solución 6.1: Inicializar DVC

```bash
# Los archivos creados:
# - .dvc/ (directorio de configuración)
# - .dvcignore (gitignore para DVC)
# - data/raw/dataset.csv.dvc (archivo de tracking)
# - data/raw/.gitignore (ignora el CSV real)

# Contenido de dataset.csv.dvc:
# outs:
# - md5: abc123def456...
#   size: 1234567
#   path: dataset.csv
```

### Solución 6.2: Pipeline DVC

```yaml
stages:
  prepare:
    cmd: python src/data.py
    deps:
      - data/raw/dataset.csv
      - src/data.py
    outs:
      - data/processed/train.csv
      - data/processed/test.csv

  train:
    cmd: python src/training.py
    deps:
      - data/processed/train.csv
      - src/training.py
      - configs/config.yaml
    outs:
      - artifacts/model.joblib
    metrics:
      - artifacts/metrics.json:
          cache: false

  evaluate:
    cmd: python src/evaluate.py
    deps:
      - data/processed/test.csv
      - artifacts/model.joblib
    metrics:
      - artifacts/evaluation.json:
          cache: false
```

---

## Módulo 09: Training Profesional

### Solución 9.1: Trainer Class

```python
from pathlib import Path
import pandas as pd
import joblib
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import accuracy_score, f1_score

class FraudTrainer:
    def __init__(self, config: dict):
        self.config = config
        self.model_ = None
        self.metrics_ = {}
    
    def run(self, input_path: Path, output_dir: Path) -> dict:
        df = self.load_data(input_path)
        X, y = df.drop('target', axis=1), df['target']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        self.metrics_['cv_scores'] = self.cross_validate(X_train, y_train)
        
        self.model_ = self.build_pipeline()
        self.model_.fit(X_train, y_train)
        
        self.metrics_.update(self.evaluate(X_test, y_test))
        self.save_artifacts(output_dir)
        
        return self.metrics_
    
    def cross_validate(self, X, y) -> dict:
        scores = cross_val_score(self.build_pipeline(), X, y, cv=5, scoring='f1')
        return {'mean': scores.mean(), 'std': scores.std()}
```

### Solución 9.2: Reproducibilidad

```python
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

SEED = 42

# 1. Seed global de numpy
np.random.seed(SEED)

# 2. random_state en train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED
)

# 3. random_state en modelo
model = RandomForestClassifier(n_estimators=100, random_state=SEED)
model.fit(X_train, y_train)
```

---

## Módulo 10: Experiment Tracking

### Solución 10.1: MLflow Básico

```python
import mlflow
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("fraud-detection")

with mlflow.start_run():
    mlflow.log_params({
        "model_type": "RandomForest",
        "n_estimators": 100,
        "max_depth": 10,
        "random_state": 42
    })
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    mlflow.log_metrics({
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba)
    })
    
    mlflow.sklearn.log_model(model, "model")
```

---

## Módulo 15: Streamlit

### Solución 15.1: Dashboard de Predicción

```python
import streamlit as st
import pandas as pd
import joblib

st.title("🔮 Fraud Predictor")

with st.sidebar:
    st.header("Input Features")
    age = st.number_input("Age", 18, 100, 35)
    balance = st.number_input("Balance", 0.0, 250000.0, 50000.0)
    salary = st.number_input("Salary", 0.0, 200000.0, 60000.0)
    geography = st.selectbox("Geography", ["France", "Germany", "Spain"])

@st.cache_resource
def load_model():
    return joblib.load("artifacts/model.joblib")

model = load_model()

if st.button("🔮 Predecir"):
    input_df = pd.DataFrame([{
        "age": age, "balance": balance,
        "salary": salary, "geography": geography
    }])
    
    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0, 1]
    
    col1, col2 = st.columns(2)
    col1.metric("Predicción", "Fraude" if prediction else "No Fraude")
    col2.metric("Probabilidad", f"{probability:.1%}")
    
    if prediction:
        st.error("⚠️ Alto riesgo de fraude detectado")
    else:
        st.success("✅ Transacción normal")
```

---

## Módulo 16: Observabilidad

### Solución 16.1: Logging Estructurado

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        # Add extra fields if present
        if hasattr(record, 'customer_id'):
            log_data['customer_id'] = record.customer_id
        if hasattr(record, 'prediction'):
            log_data['prediction'] = record.prediction
        return json.dumps(log_data)

# Configurar logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Uso:
logger.info("Prediction made", extra={"customer_id": 123, "prediction": 1})
# Output: {"timestamp": "2024-12-04T...", "level": "INFO", "message": "Prediction made", "customer_id": 123, "prediction": 1}
```

---

## Módulo 17: Despliegue

### Solución 17.1: Dockerfile Multi-stage

```dockerfile
# ═══════════════════════════════════════════════════════════════════════════
# STAGE 1: Builder - Todas las herramientas de compilación
# ═══════════════════════════════════════════════════════════════════════════
FROM python:3.11-slim AS builder

WORKDIR /app

# Dependencias de compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python en directorio aislado
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

# ═══════════════════════════════════════════════════════════════════════════
# STAGE 2: Runtime - Solo lo necesario
# ═══════════════════════════════════════════════════════════════════════════
FROM python:3.11-slim

# Usuario no-root (seguridad)
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copiar dependencias del builder
COPY --from=builder /app/deps /usr/local/lib/python3.11/site-packages/

# Copiar código y artefactos
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser artifacts/ ./artifacts/

# Cambiar a usuario no-root
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Explicación**: 
- Stage 1 tiene todas las herramientas de build (compiladores, headers)
- Stage 2 solo tiene Python runtime + dependencias instaladas
- Usuario non-root previene escalación de privilegios
- HEALTHCHECK permite orquestadores (K8s, Docker Swarm) verificar salud

---

### Solución 17.2: Docker Compose para Stack ML

```yaml
version: '3.8'

services:
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.9.0
    container_name: mlflow-server
    ports:
      - "5000:5000"
    volumes:
      - mlflow-data:/mlflow
    environment:
      - MLFLOW_TRACKING_URI=sqlite:///mlflow/mlflow.db
      - MLFLOW_DEFAULT_ARTIFACT_ROOT=/mlflow/artifacts
    command: >
      mlflow server
      --host 0.0.0.0
      --port 5000
      --backend-store-uri sqlite:///mlflow/mlflow.db
      --default-artifact-root /mlflow/artifacts
    networks:
      - mlops-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: bankchurn-api
    ports:
      - "8001:8000"
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - MODEL_PATH=/app/artifacts/model.joblib
    volumes:
      - ./artifacts:/app/artifacts:ro
    depends_on:
      mlflow:
        condition: service_healthy
    networks:
      - mlops-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  prometheus:
    image: prom/prometheus:v2.47.0
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./infra/prometheus-config.yaml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - mlops-network

networks:
  mlops-network:
    driver: bridge

volumes:
  mlflow-data:
  prometheus-data:
```

**Explicación**:
- `depends_on` con `condition: service_healthy` asegura orden de inicio
- Volúmenes nombrados persisten datos entre reinicios
- Red compartida permite comunicación por nombre de servicio
- Health checks permiten auto-recuperación

---

## Módulo 18: Infraestructura

### Solución 18.1: Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bankchurn-api
  namespace: mlops
  labels:
    app: bankchurn
    tier: api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: bankchurn
  template:
    metadata:
      labels:
        app: bankchurn
        tier: api
    spec:
      containers:
      - name: api
        image: ghcr.io/duqueom/bankchurn-api:latest
        ports:
        - containerPort: 8000
          name: http
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 2
        envFrom:
        - configMapRef:
            name: bankchurn-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: bankchurn-config
  namespace: mlops
data:
  MLFLOW_TRACKING_URI: "http://mlflow-service:5000"
  LOG_LEVEL: "INFO"
  MODEL_PATH: "/app/artifacts/model.joblib"
---
apiVersion: v1
kind: Service
metadata:
  name: bankchurn-service
  namespace: mlops
spec:
  selector:
    app: bankchurn
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

**Explicación**:
- `livenessProbe`: K8s reinicia el pod si falla (container muerto)
- `readinessProbe`: K8s deja de enviar tráfico si falla (container sobrecargado)
- `resources.requests`: Mínimo garantizado
- `resources.limits`: Máximo permitido (OOMKilled si excede)
- ConfigMap externaliza configuración del código

---

### Solución 18.2: Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bankchurn-api-hpa
  namespace: mlops
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bankchurn-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # 5 minutos
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
```

**Explicación**:
- Escala entre 2 y 10 pods basado en CPU (70%) y memoria (80%)
- `scaleDown.stabilizationWindowSeconds: 300`: Espera 5 min antes de escalar hacia abajo (evita flapping)
- `scaleUp`: Agresivo (0s estabilización, hasta 4 pods o 100% más por cada 15s)
- `selectPolicy: Max`: Usa la política que escale más rápido

---

## Módulo 19: Documentación

### Solución 19.1: Model Card

```markdown
# Model Card: BankChurn Predictor

## Model Details
- **Developed by**: DuqueOM
- **Model type**: Random Forest Classifier
- **Language**: Python 3.11
- **License**: MIT
- **Version**: 1.0.0
- **Last updated**: 2024-12-04

## Intended Use
- **Primary use case**: Predecir probabilidad de abandono de clientes bancarios
- **Primary users**: Equipos de retención, analistas de negocio
- **Out-of-scope uses**: 
  - Decisiones de crédito automatizadas sin supervisión humana
  - Discriminación basada en atributos protegidos

## Training Data
- **Dataset**: Bank Customer Churn Dataset
- **Size**: 10,000 registros
- **Features**: 11 (CreditScore, Age, Geography, Gender, Tenure, Balance, NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary)
- **Target**: Exited (0/1)
- **Class distribution**: 80% no-churn, 20% churn

## Evaluation Metrics
| Metric | Value | Confidence Interval |
|--------|-------|---------------------|
| ROC-AUC | 0.86 | [0.84, 0.88] |
| Recall | 0.75 | [0.72, 0.78] |
| Precision | 0.62 | [0.58, 0.66] |
| F1 Score | 0.68 | [0.64, 0.72] |

## Ethical Considerations
- **Fairness**: El modelo usa Geography y Gender. Se recomienda auditar disparidad de tasas de predicción entre grupos.
- **Bias potencial**: El dataset es de una región específica; puede no generalizar a otros mercados.
- **Transparencia**: Feature importances disponibles; se recomienda usar SHAP para explicaciones individuales.

## Limitations
- Entrenado solo con datos históricos 2019-2023
- No considera factores macroeconómicos externos
- Performance puede degradar con drift significativo en distribución de clientes
- Umbral de decisión (0.5) puede necesitar ajuste según costo de FP vs FN

## How to Use
```python
import joblib
model = joblib.load("artifacts/model.joblib")
prediction = model.predict(customer_df)
probability = model.predict_proba(customer_df)[:, 1]
```
```

---

### Solución 19.2: Dataset Card

```markdown
# Dataset Card: Bank Customer Churn

## Dataset Description
- **Source**: Kaggle Bank Customer Churn Dataset
- **Size**: 10,000 rows, 14 columns
- **Time period**: 2019-2023 (simulado)
- **License**: CC0 Public Domain

## Features
| Feature | Type | Description | Range/Values |
|---------|------|-------------|--------------|
| CustomerId | int | Identificador único | - |
| Surname | str | Apellido (no usar en modelo) | - |
| CreditScore | int | Puntuación crediticia | 300-850 |
| Geography | str | País del cliente | France, Germany, Spain |
| Gender | str | Género | Male, Female |
| Age | int | Edad en años | 18-92 |
| Tenure | int | Años como cliente | 0-10 |
| Balance | float | Saldo en cuenta | 0-250K |
| NumOfProducts | int | Productos contratados | 1-4 |
| HasCrCard | int | Tiene tarjeta de crédito | 0, 1 |
| IsActiveMember | int | Cliente activo | 0, 1 |
| EstimatedSalary | float | Salario estimado | 10K-200K |
| Exited | int | **TARGET**: Abandonó el banco | 0, 1 |

## Data Quality
- **Missing values**: 0%
- **Duplicates**: 0 (verificado por CustomerId)
- **Class balance**: 79.6% no-churn, 20.4% churn

## Preprocessing Applied
1. Drop: CustomerId, Surname (no predictivos)
2. One-hot encoding: Geography, Gender
3. StandardScaler: Features numéricas
4. No se aplica SMOTE (usamos class_weight='balanced')

## Ethical Considerations
- **Sensitive attributes**: Geography, Gender pueden introducir sesgo
- **Potential biases**: Dataset europeo, puede no representar otros mercados
- **Recommendations**: Auditar equidad de predicciones por grupo demográfico

## Citation
```bibtex
@misc{bank_churn_dataset,
  title={Bank Customer Churn Dataset},
  author={Kaggle},
  year={2023},
  url={https://www.kaggle.com/datasets/...}
}
```
```

---

## Módulo 20: Proyecto Integrador

### Solución 20.1: Integración End-to-End

```python
#!/usr/bin/env python3
"""
scripts/run_e2e.py
Pipeline end-to-end: train → evaluate → serve → test API
"""

import subprocess
import requests
import time
import sys
from pathlib import Path

def run_e2e_pipeline():
    """Ejecuta pipeline completo de ML."""
    
    print("=" * 60)
    print("🚀 PIPELINE E2E - BankChurn Predictor")
    print("=" * 60)
    
    # 1. Verificar datos
    print("\n📊 [1/6] Verificando datos...")
    data_path = Path("data/raw/churn.csv")
    if not data_path.exists():
        print(f"❌ Dataset no encontrado: {data_path}")
        return False
    print(f"✅ Dataset encontrado: {data_path}")
    
    # 2. Entrenar modelo
    print("\n🎯 [2/6] Entrenando modelo...")
    result = subprocess.run(
        ["python", "-m", "bankchurn.train"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ Training falló: {result.stderr}")
        return False
    print("✅ Modelo entrenado")
    
    # 3. Verificar artefactos
    print("\n📦 [3/6] Verificando artefactos...")
    model_path = Path("artifacts/model.joblib")
    if not model_path.exists():
        print(f"❌ Modelo no encontrado: {model_path}")
        return False
    print(f"✅ Modelo guardado: {model_path}")
    
    # 4. Levantar API
    print("\n🌐 [4/6] Iniciando API...")
    api_process = subprocess.Popen(
        ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    time.sleep(5)  # Esperar inicio
    
    # 5. Test de integración
    print("\n🧪 [5/6] Ejecutando test de integración...")
    try:
        # Health check
        health = requests.get("http://localhost:8000/health", timeout=5)
        assert health.status_code == 200, f"Health check falló: {health.status_code}"
        print("✅ Health check OK")
        
        # Prediction test
        test_data = {
            "CreditScore": 650,
            "Geography": "France",
            "Gender": "Male",
            "Age": 35,
            "Tenure": 5,
            "Balance": 50000.0,
            "NumOfProducts": 2,
            "HasCrCard": 1,
            "IsActiveMember": 1,
            "EstimatedSalary": 60000.0
        }
        pred = requests.post("http://localhost:8000/predict", json=test_data, timeout=5)
        assert pred.status_code == 200, f"Prediction falló: {pred.status_code}"
        result = pred.json()
        assert "probability" in result, "Response sin probability"
        print(f"✅ Prediction OK: {result}")
        
    except Exception as e:
        print(f"❌ Test falló: {e}")
        api_process.terminate()
        return False
    
    # 6. Cleanup
    print("\n🧹 [6/6] Limpiando...")
    api_process.terminate()
    api_process.wait()
    print("✅ API terminada")
    
    print("\n" + "=" * 60)
    print("🎉 PIPELINE E2E COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_e2e_pipeline()
    sys.exit(0 if success else 1)
```

---

### Solución 20.2: Health Check Script

```python
#!/usr/bin/env python3
"""
scripts/health_check.py
Verifica salud de todos los servicios del stack MLOps
"""

import requests
from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class ServiceHealth:
    name: str
    url: str
    healthy: bool
    status_code: int | None
    response_time_ms: float
    details: str

def check_service(name: str, url: str, timeout: int = 5) -> ServiceHealth:
    """Verifica salud de un servicio."""
    start = datetime.now()
    try:
        response = requests.get(url, timeout=timeout)
        response_time = (datetime.now() - start).total_seconds() * 1000
        
        return ServiceHealth(
            name=name,
            url=url,
            healthy=response.status_code == 200,
            status_code=response.status_code,
            response_time_ms=response_time,
            details=response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:100]
        )
    except requests.exceptions.ConnectionError:
        return ServiceHealth(name, url, False, None, 0, "Connection refused")
    except requests.exceptions.Timeout:
        return ServiceHealth(name, url, False, None, timeout * 1000, "Timeout")
    except Exception as e:
        return ServiceHealth(name, url, False, None, 0, str(e))

def check_all_services() -> List[ServiceHealth]:
    """Verifica todos los servicios del stack."""
    services = [
        ("MLflow", "http://localhost:5000/health"),
        ("BankChurn API", "http://localhost:8001/health"),
        ("CarVision API", "http://localhost:8002/health"),
        ("CarVision Dashboard", "http://localhost:8501/healthz"),
        ("TelecomAI API", "http://localhost:8003/health"),
        ("Prometheus", "http://localhost:9090/-/healthy"),
        ("Grafana", "http://localhost:3000/api/health"),
    ]
    
    return [check_service(name, url) for name, url in services]

def generate_report(results: List[ServiceHealth]) -> str:
    """Genera reporte de salud."""
    healthy_count = sum(1 for r in results if r.healthy)
    total = len(results)
    
    lines = [
        "=" * 70,
        f"🏥 HEALTH CHECK REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70,
        f"Status: {healthy_count}/{total} services healthy",
        "",
        f"{'Service':<20} {'Status':<10} {'Code':<6} {'Time':<10} {'Details'}",
        "-" * 70,
    ]
    
    for r in results:
        status = "✅ UP" if r.healthy else "❌ DOWN"
        code = str(r.status_code) if r.status_code else "N/A"
        time_str = f"{r.response_time_ms:.0f}ms" if r.response_time_ms > 0 else "N/A"
        details = r.details[:30] + "..." if len(r.details) > 30 else r.details
        lines.append(f"{r.name:<20} {status:<10} {code:<6} {time_str:<10} {details}")
    
    lines.extend([
        "-" * 70,
        f"Overall: {'🟢 ALL HEALTHY' if healthy_count == total else '🔴 DEGRADED'}",
        "=" * 70,
    ])
    
    return "\n".join(lines)

if __name__ == "__main__":
    results = check_all_services()
    print(generate_report(results))
    
    # Exit code para CI/CD
    import sys
    sys.exit(0 if all(r.healthy for r in results) else 1)
```

---

## Módulo 21: Glosario (Autoestudio)

### Solución 21.1: Flashcards de Términos

```markdown
<!-- Formato: Pregunta | Respuesta -->

# Flashcards MLOps - 25 Términos Clave

¿Qué es Data Drift? | Cambio en la distribución de features P(X) entre training y producción

¿Qué es Concept Drift? | Cambio en la relación P(Y|X) entre features y target

¿Diferencia entre Precision y Recall? | Precision=TP/(TP+FP) "de los que predije positivos, cuántos eran reales". Recall=TP/(TP+FN) "de los positivos reales, cuántos detecté"

¿Qué resuelve class_weight='balanced'? | Penaliza más los errores en la clase minoritaria, inversamente proporcional a su frecuencia

¿Para qué sirve ColumnTransformer? | Aplicar diferentes transformaciones a diferentes columnas en paralelo dentro de un Pipeline sklearn

¿Qué es training-serving skew? | Diferencia entre el preprocesamiento en training vs producción que causa predicciones incorrectas

¿Por qué usar Pipeline en vez de pasos separados? | Evita data leakage, garantiza misma transformación en train/test/prod, serializa todo junto

¿Qué hace @st.cache_resource? | Cachea recursos pesados (modelos, conexiones DB) que no deben recargarse en cada interacción de Streamlit

¿Qué es un ADR? | Architecture Decision Record - documento que registra una decisión técnica con contexto, alternativas y consecuencias

¿Diferencia entre liveness y readiness probe? | Liveness: reinicia pod si falla (muerto). Readiness: deja de enviar tráfico si falla (sobrecargado)

¿Qué es multi-stage build en Docker? | Separar build (con compiladores) de runtime (solo binarios) para imágenes más pequeñas y seguras

¿Por qué usuario non-root en Docker? | Seguridad: si el container es comprometido, el atacante no tiene privilegios root

¿Qué es PSI (Population Stability Index)? | Métrica para detectar drift: <0.1 no drift, 0.1-0.2 moderado, >0.2 significativo

¿Qué hace DVC? | Versiona datasets y modelos grandes junto con Git, sin guardarlos en el repo

¿Qué es un Model Card? | Documentación estandarizada de un modelo: propósito, métricas, limitaciones, consideraciones éticas

¿Para qué sirve HPA en Kubernetes? | Horizontal Pod Autoscaler: escala réplicas automáticamente basado en métricas (CPU, memoria)

¿Qué es Feature Store? | Repositorio centralizado de features procesadas, reutilizables entre modelos y equipos

¿Qué mide ROC-AUC? | Capacidad discriminatoria del modelo: probabilidad de rankear un positivo por encima de un negativo

¿Por qué pytest fixtures? | Reutilizar setup de tests (datos, modelos) sin duplicar código, con scope controlado

¿Qué hace mlflow.log_artifact()? | Guarda archivos (gráficos, modelos, CSVs) asociados a un experimento para reproducibilidad

¿Qué es SMOTE? | Synthetic Minority Over-sampling: genera ejemplos sintéticos de clase minoritaria interpolando entre vecinos

¿Por qué src/ layout? | Evita importar código local en vez del paquete instalado, estructura profesional instalable

¿Qué son Conventional Commits? | Formato estandarizado de mensajes: type(scope): description. Permite generar CHANGELOGs automáticos

¿Qué hace conftest.py? | Define fixtures compartidas para todos los tests del directorio, pytest lo descubre automáticamente

¿Qué es Pydantic? | Librería de validación de datos usando type hints. Valida, serializa y documenta esquemas automáticamente
```

---

## Módulo 22: Checklist de Producción

### Solución 22.1: Auditoría de Proyecto

```markdown
# Auditoría: CarVision-Market-Intelligence

## Código ✅
- [x] Type hints en todas las funciones (verificado: 100% en src/)
- [x] Docstrings en clases y métodos públicos
- [x] Sin secretos hardcodeados (verificado con gitleaks)
- [x] Linting pasando (ruff check src/ → 0 errores)

## Testing ✅
- [x] Coverage >= 80% (actual: 97%)
- [x] Tests de datos (schema, rangos) → test_data.py
- [x] Tests de modelo (predicciones válidas) → test_pipeline.py
- [x] Tests de integración (API funcional) → test_api.py

## CI/CD ✅
- [x] Pipeline ejecuta en cada PR (ci-mlops.yml)
- [x] Tests ejecutan en múltiples versiones Python (3.10, 3.11)
- [x] Security scanning configurado (Bandit, pip-audit, Trivy)
- [x] Docker build automatizado (GHCR push en main)

## Documentación ⚠️
- [x] README actualizado (badges, quickstart, arquitectura)
- [ ] Model Card completado → PENDIENTE: crear docs/model_card.md
- [x] API documentada (Swagger en /docs)

## Observabilidad ⚠️
- [x] Logging estructurado (common_utils.logger)
- [ ] Métricas de Prometheus → PENDIENTE: añadir prometheus_client
- [x] Health endpoint implementado (/health)

## Issues Creados
1. #42: Crear Model Card para CarVision
2. #43: Añadir métricas Prometheus a FastAPI

## Puntuación Estimada
- Código: 18/20
- Pipeline: 18/20
- Testing/CI: 19/20
- APIs: 13/15
- Tracking: 8/10
- Docs: 12/15

**TOTAL: 88/100 → Senior Level 🥈**
```

---

## Módulo 23: Recursos (Práctica)

### Solución 23.1: Plan de Estudio Personalizado

```markdown
# Mi Plan de Estudio MLOps

## Autoevaluación (1-5)
| Área | Nivel | Prioridad |
|------|:-----:|:---------:|
| Python moderno | 4 | Baja |
| sklearn Pipelines | 3 | Alta |
| Docker | 2 | Alta |
| CI/CD | 2 | Alta |
| Testing | 4 | Media |
| Observabilidad | 1 | Alta |

## Gaps Identificados
1. **Docker**: Solo uso básico, no multi-stage ni compose
2. **CI/CD**: No he configurado GitHub Actions desde cero
3. **Observabilidad**: No conozco Prometheus/Grafana

## Recursos Seleccionados
| Gap | Recurso | Tipo | Tiempo |
|-----|---------|------|:------:|
| Docker | [Docker Tutorial - Nana](https://youtube.com/...) 🔴 | Video | 1h |
| Docker | Docker Mastery (Udemy) 🟡 | Curso | 10h |
| CI/CD | [GitHub Actions Tutorial](https://youtube.com/...) 🔴 | Video | 30m |
| CI/CD | Módulo 12 + Ejercicio 12.1 | Guía | 3h |
| Observabilidad | [Prometheus+Grafana - Nana](https://youtube.com/...) 🔴 | Video | 50m |
| Observabilidad | Módulo 16 + prometheus-rules.yaml | Guía | 4h |

## Timeline
| Semana | Módulos | Recursos Externos | Entregable |
|:------:|---------|-------------------|------------|
| 1 | 07, 08 | sklearn Pipeline video | FeatureEngineer class |
| 2 | 11, 12 | CI/CD video + ejercicio | GitHub Actions workflow |
| 3 | 13 | Docker tutorial + compose | Multi-stage Dockerfile |
| 4 | 14, 15 | FastAPI video | API + Streamlit |
| 5 | 16 | Prometheus/Grafana video | Métricas + alertas |
| 6 | 17, 18 | K8s tutorial | Deployment manifest |
| 7 | 19, 20 | - | Model Card + E2E script |
| 8 | 21-23 + Simulacros | - | Speech preparado |

## Checkpoints
- [ ] Semana 2: Primer proyecto con CI verde
- [ ] Semana 4: API funcionando con Docker
- [ ] Semana 6: Stack completo en Kubernetes local
- [ ] Semana 8: Portafolio completo, simulacros hechos
```

---

<div align="center">

[← Volver a Ejercicios](EJERCICIOS.md) | [Índice](00_INDICE.md)

</div>
