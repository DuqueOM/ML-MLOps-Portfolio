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

<div align="center">

[← Volver a Ejercicios](EJERCICIOS.md) | [Índice](00_INDICE.md)

</div>
