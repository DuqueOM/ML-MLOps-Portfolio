# 🔧 Ejercicios Prácticos — Guía MLOps

> **Ejercicios organizados por módulo para practicar cada concepto**

---

## 📋 Índice de Ejercicios

| Módulo | Tema | Dificultad |
|:-------|:-----|:----------:|
| 01 | Python Moderno | ⭐⭐ |
| 07 | sklearn Pipelines | ⭐⭐⭐ |
| 08 | Feature Engineering | ⭐⭐⭐ |
| 11 | Testing ML | ⭐⭐⭐ |
| 12 | CI/CD | ⭐⭐ |
| 13 | Docker | ⭐⭐ |
| 14 | FastAPI | ⭐⭐⭐ |

---

## 📝 Módulo 01: Python Moderno

### Ejercicio 1.1: Type Hints
**Objetivo**: Añadir type hints a funciones existentes.

```python
# ANTES (sin tipos)
def load_data(path):
    return pd.read_csv(path)

def train_model(X, y, params):
    model = RandomForestClassifier(**params)
    return model.fit(X, y)

# TU TAREA: Añadir type hints completos
# Hint: usa pd.DataFrame, np.ndarray, dict[str, Any]
```

### Ejercicio 1.2: Pydantic Config
**Objetivo**: Crear configuración validada con Pydantic.

```python
# Crear una clase ModelConfig que valide:
# - n_estimators: int entre 10 y 500
# - max_depth: int opcional, entre 1 y 50
# - random_state: int, default 42

# TU CÓDIGO AQUÍ
from pydantic import BaseModel, Field

class ModelConfig(BaseModel):
    # ...
    pass
```

### Ejercicio 1.3: src/ Layout
**Objetivo**: Reorganizar código en estructura profesional.

```
# Dado este código en un solo archivo main.py:
# - load_data()
# - preprocess()
# - train()
# - predict()
# - FastAPI app

# TU TAREA: Crear estructura src/ con:
# src/myproject/data.py
# src/myproject/training.py
# src/myproject/prediction.py
# app/fastapi_app.py
```

---

## 📝 Módulo 07: sklearn Pipelines

### Ejercicio 7.1: Pipeline Básico
**Objetivo**: Crear un pipeline con preprocesamiento.

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# TU TAREA: Crear pipeline con:
# 1. StandardScaler para features numéricas
# 2. RandomForestClassifier

pipe = Pipeline([
    # TU CÓDIGO
])
```

### Ejercicio 7.2: ColumnTransformer
**Objetivo**: Procesar columnas numéricas y categóricas por separado.

```python
# Dado un DataFrame con:
# - numeric_cols = ['age', 'balance', 'salary']
# - categorical_cols = ['geography', 'gender']

# TU TAREA: Crear ColumnTransformer que:
# - Aplique StandardScaler a numéricas
# - Aplique OneHotEncoder a categóricas

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

preprocessor = ColumnTransformer([
    # TU CÓDIGO
])
```

### Ejercicio 7.3: Custom Transformer
**Objetivo**: Crear un transformer personalizado.

```python
from sklearn.base import BaseEstimator, TransformerMixin

# TU TAREA: Crear AgeGroupTransformer que:
# - Añada columna 'age_group' basada en rangos de edad
# - 0-30: 'young', 31-50: 'middle', 51+: 'senior'

class AgeGroupTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        # TU CÓDIGO
        return self
    
    def transform(self, X):
        # TU CÓDIGO
        pass
```

---

## 📝 Módulo 08: Feature Engineering

### Ejercicio 8.1: Detectar Data Leakage
**Objetivo**: Identificar leakage en un pipeline.

```python
# CÓDIGO CON LEAKAGE - Encuentra los 3 errores:

df = pd.read_csv('data.csv')

# Error 1: ¿Dónde está?
df['price_category'] = pd.cut(df['price'], bins=3, labels=['low', 'mid', 'high'])

# Error 2: ¿Dónde está?
scaler = StandardScaler()
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

X_train, X_test, y_train, y_test = train_test_split(df.drop('target', axis=1), df['target'])

# Error 3: ¿Dónde está?
model = RandomForestClassifier()
model.fit(X_train, y_train)
```

### Ejercicio 8.2: Pipeline Sin Leakage
**Objetivo**: Reescribir el código anterior sin leakage.

```python
# TU TAREA: Reescribir el ejercicio 8.1 sin data leakage
# Hint: El scaler debe estar DENTRO del pipeline
# Hint: No crear features basadas en el target antes del split
```

---

## 📝 Módulo 11: Testing ML

### Ejercicio 11.1: Test de Datos
**Objetivo**: Escribir tests para validar datos.

```python
# TU TAREA: Escribir tests que verifiquen:
# 1. No hay valores nulos en columnas críticas
# 2. Valores de 'age' están entre 18 y 100
# 3. 'target' solo contiene 0 y 1

import pytest

def test_no_nulls(sample_data):
    # TU CÓDIGO
    pass

def test_age_range(sample_data):
    # TU CÓDIGO
    pass

def test_target_binary(sample_data):
    # TU CÓDIGO
    pass
```

### Ejercicio 11.2: Test de Modelo
**Objetivo**: Testear que el modelo funciona correctamente.

```python
# TU TAREA: Escribir tests que verifiquen:
# 1. El modelo puede hacer fit sin errores
# 2. Las predicciones tienen el shape correcto
# 3. El accuracy es mayor que un baseline (ej: 0.5)

def test_model_fit(trained_model, sample_data):
    # TU CÓDIGO
    pass

def test_predictions_shape(trained_model, sample_data):
    # TU CÓDIGO
    pass

def test_accuracy_above_baseline(trained_model, sample_data):
    # TU CÓDIGO
    pass
```

### Ejercicio 11.3: Fixture con conftest.py
**Objetivo**: Crear fixtures reutilizables.

```python
# tests/conftest.py

import pytest
import pandas as pd

# TU TAREA: Crear fixtures para:
# 1. sample_data: DataFrame con datos de prueba
# 2. trained_model: Modelo ya entrenado
# 3. config: Configuración de prueba

@pytest.fixture
def sample_data():
    # TU CÓDIGO
    pass

@pytest.fixture
def trained_model(sample_data):
    # TU CÓDIGO
    pass
```

---

## 📝 Módulo 12: CI/CD

### Ejercicio 12.1: GitHub Actions Básico
**Objetivo**: Crear workflow de CI.

```yaml
# .github/workflows/ci.yml

# TU TAREA: Crear workflow que:
# 1. Se ejecute en push y PR a main
# 2. Use Python 3.11
# 3. Instale dependencias
# 4. Ejecute tests con coverage
# 5. Falle si coverage < 80%

name: CI

on:
  # TU CÓDIGO

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      # TU CÓDIGO
```

---

## 📝 Módulo 13: Docker

### Ejercicio 13.1: Dockerfile Multi-stage
**Objetivo**: Crear Dockerfile optimizado.

```dockerfile
# TU TAREA: Crear Dockerfile que:
# 1. Use multi-stage build
# 2. Stage 1: instalar dependencias
# 3. Stage 2: copiar solo lo necesario
# 4. Use usuario non-root
# 5. Exponga puerto 8000

# Stage 1: Builder
FROM python:3.11-slim AS builder
# TU CÓDIGO

# Stage 2: Runtime
FROM python:3.11-slim
# TU CÓDIGO
```

---

## 📝 Módulo 14: FastAPI

### Ejercicio 14.1: Schemas Pydantic
**Objetivo**: Crear schemas de request/response.

```python
# TU TAREA: Crear schemas para API de predicción

from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    # Features del modelo
    # TU CÓDIGO
    pass

class PredictionResponse(BaseModel):
    # prediction: int
    # probability: float
    # TU CÓDIGO
    pass
```

### Ejercicio 14.2: Endpoint de Predicción
**Objetivo**: Implementar /predict endpoint.

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

# TU TAREA: Implementar endpoint que:
# 1. Reciba PredictionRequest
# 2. Valide los datos
# 3. Haga predicción con modelo cargado
# 4. Retorne PredictionResponse
# 5. Maneje errores con HTTPException

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    # TU CÓDIGO
    pass
```

---

## ✅ Soluciones

Ver [EJERCICIOS_SOLUCIONES.md](EJERCICIOS_SOLUCIONES.md) para las soluciones detalladas.

---

<div align="center">

[← Volver al Índice](00_INDICE.md)

</div>
