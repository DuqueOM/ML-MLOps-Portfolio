# 🔧 Ejercicios Prácticos — Guía MLOps

> **Ejercicios organizados por módulo para practicar cada concepto**

---

## 📋 Índice de Ejercicios

| Módulo | Tema | Dificultad | Ejercicios |
|:------:|:-----|:----------:|:----------:|
| 01 | Python Moderno | ⭐⭐ | 3 |
| 02 | Diseño de Sistemas | ⭐⭐ | 2 |
| 03 | Estructura de Proyecto | ⭐ | 2 |
| 04 | Entornos | ⭐ | 2 |
| 05 | Git Profesional | ⭐⭐ | 2 |
| 06 | Versionado de Datos | ⭐⭐ | 2 |
| 07 | sklearn Pipelines | ⭐⭐⭐ | 3 |
| 08 | Feature Engineering | ⭐⭐⭐ | 2 |
| 09 | Training Profesional | ⭐⭐⭐ | 2 |
| 10 | Experiment Tracking | ⭐⭐ | 2 |
| 11 | Testing ML | ⭐⭐⭐ | 3 |
| 12 | CI/CD | ⭐⭐ | 1 |
| 13 | Docker | ⭐⭐ | 2 |
| 14 | FastAPI | ⭐⭐⭐ | 2 |
| 15 | Streamlit | ⭐⭐ | 1 |
| 16 | Observabilidad | ⭐⭐ | 1 |
| 17 | Despliegue | ⭐⭐⭐ | 2 |
| 18 | Infraestructura | ⭐⭐⭐ | 2 |
| 19 | Documentación | ⭐⭐ | 2 |
| 20 | Proyecto Integrador | ⭐⭐⭐ | 2 |
| 21 | Glosario | ⭐ | 1 |
| 22 | Checklist | ⭐⭐ | 1 |
| 23 | Recursos | ⭐ | 1 |

**Total: 43 ejercicios**

> 📺 **Recursos externos**: Ver [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) para videos y cursos complementarios organizados por módulo.

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

## 📝 Módulo 02: Diseño de Sistemas

### Ejercicio 2.1: ML Canvas
**Objetivo**: Completar un ML Canvas para un proyecto.

```markdown
# ML Canvas: [Tu Proyecto]

## 1. Propuesta de Valor
- ¿Qué problema de negocio resuelve?
- ¿Cuál es el impacto medible?

## 2. Datos
- ¿De dónde vienen los datos?
- ¿Qué features son necesarias?

## 3. Modelo
- ¿Qué tipo de modelo (clasificación/regresión)?
- ¿Métricas de éxito?

# TU TAREA: Completar para BankChurn-Predictor
```

### Ejercicio 2.2: ADR (Architecture Decision Record)
**Objetivo**: Documentar una decisión técnica.

```markdown
# ADR-001: Elección de Framework de API

## Estado
Propuesto | Aceptado | Deprecado

## Contexto
¿Por qué necesitamos tomar esta decisión?

## Opciones Consideradas
1. FastAPI
2. Flask
3. Django REST

## Decisión
¿Cuál elegimos y por qué?

## Consecuencias
- Positivas:
- Negativas:

# TU TAREA: Crear ADR para decisión de modelo en TelecomAI
```

---

## 📝 Módulo 03: Estructura de Proyecto

### Ejercicio 3.1: Crear src/ Layout
**Objetivo**: Organizar código en estructura profesional.

```bash
# TU TAREA: Crear la siguiente estructura para un proyecto "fraud_detector"

fraud-detector/
├── src/
│   └── frauddetector/
│       ├── __init__.py
│       ├── config.py      # Crear con Pydantic
│       ├── data.py        # load_data()
│       ├── features.py    # FeatureEngineer
│       ├── training.py    # FraudTrainer
│       └── pipeline.py    # build_pipeline()
├── tests/
│   └── conftest.py
├── configs/
│   └── config.yaml
├── pyproject.toml
└── Makefile
```

### Ejercicio 3.2: pyproject.toml
**Objetivo**: Configurar proyecto Python moderno.

```toml
# TU TAREA: Completar pyproject.toml

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "fraud-detector"
version = "0.1.0"
# ... completar dependencies, optional-dependencies, scripts
```

---

## 📝 Módulo 04: Entornos

### Ejercicio 4.1: Makefile
**Objetivo**: Crear Makefile con comandos esenciales.

```makefile
# TU TAREA: Crear Makefile con estos targets

.PHONY: install test lint format train serve clean

install:
    # Instalar dependencias

test:
    # Ejecutar tests con coverage

lint:
    # Ejecutar ruff check

format:
    # Formatear con ruff format

train:
    # Entrenar modelo

serve:
    # Iniciar API

clean:
    # Limpiar artefactos
```

### Ejercicio 4.2: Entorno Reproducible
**Objetivo**: Configurar entorno desde cero.

```bash
# TU TAREA: Ejecutar estos comandos y documentar cualquier problema

# 1. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# 2. Instalar proyecto en modo editable
pip install -e ".[dev]"

# 3. Verificar instalación
python -c "import frauddetector; print(frauddetector.__version__)"

# 4. Ejecutar tests
pytest tests/ -v
```

---

## 📝 Módulo 05: Git Profesional

### Ejercicio 5.1: Conventional Commits
**Objetivo**: Escribir commits con formato profesional.

```bash
# TU TAREA: Convertir estos mensajes a Conventional Commits

# MAL: "fixed bug"
# BIEN: ???

# MAL: "added tests"
# BIEN: ???

# MAL: "updated readme"
# BIEN: ???

# MAL: "refactored code"
# BIEN: ???

# Formato: <type>(<scope>): <description>
# Types: feat, fix, docs, style, refactor, test, chore
```

### Ejercicio 5.2: Pre-commit Hooks
**Objetivo**: Configurar hooks de calidad.

```yaml
# .pre-commit-config.yaml
# TU TAREA: Completar configuración

repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      # ¿Qué hooks de ruff necesitas?

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      # ¿Qué hooks básicos necesitas?

# Después: pre-commit install && pre-commit run --all-files
```

---

## 📝 Módulo 06: Versionado de Datos

### Ejercicio 6.1: Inicializar DVC
**Objetivo**: Configurar DVC en un proyecto.

```bash
# TU TAREA: Ejecutar y documentar cada paso

# 1. Inicializar DVC
dvc init

# 2. Añadir remote local (para práctica)
dvc remote add -d localremote /tmp/dvc-storage

# 3. Trackear datos
dvc add data/raw/dataset.csv

# 4. Commitear archivos .dvc
git add data/raw/dataset.csv.dvc data/raw/.gitignore
git commit -m "chore(data): track dataset with DVC"

# PREGUNTA: ¿Qué archivos se crean? ¿Qué contiene el .dvc?
```

### Ejercicio 6.2: Pipeline DVC
**Objetivo**: Definir pipeline reproducible.

```yaml
# dvc.yaml
# TU TAREA: Definir pipeline de 3 stages

stages:
  prepare:
    cmd: python src/data.py
    deps:
      # ¿Qué dependencias?
    outs:
      # ¿Qué outputs?

  train:
    cmd: python src/training.py
    deps:
      # ???
    outs:
      # ???
    metrics:
      # ???

  evaluate:
    cmd: python src/evaluate.py
    deps:
      # ???
    metrics:
      # ???
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

## 📝 Módulo 09: Training Profesional

### Ejercicio 9.1: Trainer Class
**Objetivo**: Implementar clase de entrenamiento profesional.

```python
# TU TAREA: Completar la clase FraudTrainer

from pathlib import Path
import pandas as pd
from sklearn.model_selection import cross_val_score

class FraudTrainer:
    """Entrenador profesional siguiendo patrón del portafolio."""
    
    def __init__(self, config: dict):
        self.config = config
        self.model_ = None
        self.metrics_ = {}
    
    def run(self, input_path: Path, output_dir: Path) -> dict:
        """Flujo completo de entrenamiento."""
        # TODO: Implementar:
        # 1. load_data()
        # 2. split_data()
        # 3. cross_validate()
        # 4. fit modelo final
        # 5. evaluate()
        # 6. save_artifacts()
        pass
    
    def cross_validate(self, X, y) -> dict:
        """Cross-validation con métricas."""
        # TODO: Implementar CV estratificada
        pass
```

### Ejercicio 9.2: Reproducibilidad
**Objetivo**: Garantizar resultados reproducibles.

```python
# TU TAREA: Hacer este código 100% reproducible

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# ¿Qué seeds faltan?
X_train, X_test, y_train, y_test = train_test_split(X, y)
model = RandomForestClassifier()
model.fit(X_train, y_train)

# PISTA: np.random.seed, random_state en split, random_state en modelo
```

---

## 📝 Módulo 10: Experiment Tracking

### Ejercicio 10.1: MLflow Básico
**Objetivo**: Loggear experimento con MLflow.

```python
import mlflow

# TU TAREA: Completar el tracking

mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("fraud-detection")

with mlflow.start_run():
    # TODO: Log parámetros
    mlflow.log_params({
        # ???
    })
    
    # TODO: Entrenar modelo
    model.fit(X_train, y_train)
    
    # TODO: Log métricas
    mlflow.log_metrics({
        # ???
    })
    
    # TODO: Log modelo
    mlflow.sklearn.log_model(???)
```

### Ejercicio 10.2: Comparar Experimentos
**Objetivo**: Ejecutar y comparar múltiples runs.

```python
# TU TAREA: Crear script que entrene 3 modelos diferentes
# y los compare en MLflow UI

models = [
    ("rf", RandomForestClassifier(n_estimators=100)),
    ("gb", GradientBoostingClassifier(n_estimators=100)),
    ("lr", LogisticRegression()),
]

for name, model in models:
    with mlflow.start_run(run_name=name):
        # TODO: Entrenar, evaluar, loggear
        pass

# Después: mlflow ui -> comparar runs
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

### Ejercicio 13.2: Docker Compose Avanzado
**Objetivo**: Orquestar stack ML completo.

```yaml
# docker-compose.ml.yml
# TU TAREA: Crear compose que levante:
# 1. API de ML (tu Dockerfile)
# 2. MLflow server
# 3. Prometheus para métricas
# 4. Red compartida entre servicios
# 5. Volúmenes para persistencia

version: '3.8'

services:
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.9.0
    # TODO: ports, volumes, environment, healthcheck
    
  api:
    build: .
    # TODO: ports, depends_on, environment, healthcheck
    
  prometheus:
    image: prom/prometheus:v2.47.0
    # TODO: ports, volumes, command

networks:
  # TODO: Red compartida

volumes:
  # TODO: Volúmenes persistentes
```

> 📺 Ver [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) - Módulo 13 para videos de Docker Compose

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

## 📝 Módulo 15: Streamlit

### Ejercicio 15.1: Dashboard de Predicción
**Objetivo**: Crear dashboard interactivo.

```python
# app/streamlit_app.py
# TU TAREA: Crear dashboard con:
# 1. Sidebar con inputs para features
# 2. Botón de predicción
# 3. Mostrar resultado con probabilidad
# 4. Visualización de importancia de features

import streamlit as st
import pandas as pd
import joblib

st.title("🔮 Fraud Predictor")

# TODO: Sidebar con inputs
with st.sidebar:
    # st.number_input, st.selectbox, etc.
    pass

# TODO: Cargar modelo
@st.cache_resource
def load_model():
    # ???
    pass

# TODO: Botón y predicción
if st.button("Predecir"):
    # ???
    pass

# TODO: Mostrar resultado
# st.success(), st.error(), st.metric()
```

---

## 📝 Módulo 16: Observabilidad

### Ejercicio 16.1: Logging Estructurado
**Objetivo**: Implementar logging profesional.

```python
# TU TAREA: Configurar logging estructurado

import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Formatter que produce logs en JSON."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            # TODO: Añadir más campos útiles
        }
        return json.dumps(log_data)

# TODO: Configurar logger
logger = logging.getLogger(__name__)
# ???

# Uso:
logger.info("Prediction made", extra={"customer_id": 123, "prediction": 1})
```

---

## 📝 Módulo 17: Despliegue

### Ejercicio 17.1: Dockerfile Multi-stage
**Objetivo**: Crear un Dockerfile optimizado para producción.

```dockerfile
# TU TAREA: Crear Dockerfile multi-stage para una API de ML
# Requisitos:
# 1. Stage "builder": Instalar dependencias
# 2. Stage "runtime": Imagen mínima para producción
# 3. Usuario no-root
# 4. Health check

# STAGE 1: Builder
FROM python:3.11-slim AS builder

# TODO: Instalar dependencias de compilación
# TODO: Copiar requirements e instalar

# STAGE 2: Runtime
FROM python:3.11-slim

# TODO: Crear usuario no-root
# TODO: Copiar solo lo necesario del builder
# TODO: Configurar HEALTHCHECK
# TODO: CMD para ejecutar uvicorn
```

### Ejercicio 17.2: Docker Compose para Stack ML
**Objetivo**: Orquestar múltiples servicios ML.

```yaml
# docker-compose.yml
# TU TAREA: Crear stack con:
# 1. API de ML (FastAPI)
# 2. MLflow server
# 3. Prometheus
# 4. Red compartida
# 5. Volúmenes persistentes

version: '3.8'

services:
  mlflow:
    # TODO: Configurar MLflow server
    
  api:
    # TODO: Configurar API con dependencia de MLflow
    
  prometheus:
    # TODO: Configurar Prometheus con config file

networks:
  # TODO: Red compartida

volumes:
  # TODO: Volúmenes persistentes
```

---

## 📝 Módulo 18: Infraestructura

### Ejercicio 18.1: Kubernetes Deployment
**Objetivo**: Crear manifests K8s para una API ML.

```yaml
# k8s/deployment.yaml
# TU TAREA: Crear Deployment con:
# 1. 2 replicas
# 2. Resource limits (CPU, memoria)
# 3. Liveness y readiness probes
# 4. Environment variables desde ConfigMap

apiVersion: apps/v1
kind: Deployment
metadata:
  name: bankchurn-api
  # TODO: labels
spec:
  replicas: # ???
  selector:
    # TODO: matchLabels
  template:
    spec:
      containers:
      - name: api
        image: # ???
        ports:
        - containerPort: 8000
        resources:
          # TODO: limits y requests
        livenessProbe:
          # TODO: Configurar probe
        readinessProbe:
          # TODO: Configurar probe
        envFrom:
          # TODO: ConfigMap reference
```

### Ejercicio 18.2: Horizontal Pod Autoscaler
**Objetivo**: Configurar autoscaling basado en CPU.

```yaml
# k8s/hpa.yaml
# TU TAREA: Crear HPA que:
# 1. Escale entre 2 y 10 pods
# 2. Target CPU utilization: 70%
# 3. Scale down stabilization: 5 minutos

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bankchurn-api-hpa
spec:
  scaleTargetRef:
    # TODO: Referencia al Deployment
  minReplicas: # ???
  maxReplicas: # ???
  metrics:
  - type: Resource
    resource:
      # TODO: Configurar métrica de CPU
  behavior:
    scaleDown:
      # TODO: Configurar estabilización
```

---

## 📝 Módulo 19: Documentación

### Ejercicio 19.1: Model Card
**Objetivo**: Documentar un modelo siguiendo estándares.

```markdown
<!-- model_card.md -->
<!-- TU TAREA: Completar Model Card para BankChurn -->

# Model Card: BankChurn Predictor

## Model Details
- **Developed by**: ???
- **Model type**: ???
- **Language**: ???
- **License**: ???

## Intended Use
- **Primary use case**: ???
- **Primary users**: ???
- **Out-of-scope uses**: ???

## Training Data
- **Dataset**: ???
- **Size**: ???
- **Features**: ???

## Evaluation Metrics
| Metric | Value |
|--------|-------|
| ROC-AUC | ??? |
| Recall | ??? |
| Precision | ??? |

## Ethical Considerations
- ???

## Limitations
- ???
```

### Ejercicio 19.2: Dataset Card
**Objetivo**: Documentar un dataset siguiendo estándares.

```markdown
<!-- dataset_card.md -->
<!-- TU TAREA: Completar Dataset Card -->

# Dataset Card: Bank Customer Churn

## Dataset Description
- **Source**: ???
- **Size**: ??? rows, ??? columns
- **Time period**: ???

## Features
| Feature | Type | Description |
|---------|------|-------------|
| CreditScore | int | ??? |
| Geography | str | ??? |
| ... | ... | ... |

## Data Quality
- **Missing values**: ???
- **Class balance**: ???

## Ethical Considerations
- **Sensitive attributes**: ???
- **Potential biases**: ???
```

---

## 📝 Módulo 20: Proyecto Integrador

### Ejercicio 20.1: Integración End-to-End
**Objetivo**: Crear script que ejecute pipeline completo.

```python
# scripts/run_e2e.py
# TU TAREA: Script que:
# 1. Cargue datos
# 2. Entrene modelo
# 3. Evalúe métricas
# 4. Guarde artefactos
# 5. Registre en MLflow
# 6. Pruebe API localmente

import subprocess
import requests
from pathlib import Path

def run_e2e_pipeline():
    """Ejecuta pipeline completo de ML."""
    
    # 1. Verificar datos
    data_path = Path("data/raw/dataset.csv")
    assert data_path.exists(), "Dataset no encontrado"
    
    # 2. Entrenar modelo
    # TODO: Ejecutar training script
    
    # 3. Verificar artefactos
    # TODO: Verificar que model.joblib existe
    
    # 4. Levantar API
    # TODO: subprocess.Popen para uvicorn
    
    # 5. Test de integración
    # TODO: requests.post("/predict", ...)
    
    # 6. Cleanup
    # TODO: Terminar proceso de API

if __name__ == "__main__":
    run_e2e_pipeline()
```

### Ejercicio 20.2: Health Check Script
**Objetivo**: Verificar salud de todos los servicios.

```python
# scripts/health_check.py
# TU TAREA: Script que verifique:
# 1. Todos los servicios responden
# 2. Modelos están cargados
# 3. MLflow está accesible
# 4. Genera reporte de estado

import requests
from dataclasses import dataclass
from typing import List

@dataclass
class ServiceHealth:
    name: str
    url: str
    healthy: bool
    details: str

def check_service(name: str, url: str) -> ServiceHealth:
    """Verifica salud de un servicio."""
    # TODO: Implementar
    pass

def check_all_services() -> List[ServiceHealth]:
    """Verifica todos los servicios del stack."""
    services = [
        ("MLflow", "http://localhost:5000/health"),
        ("BankChurn API", "http://localhost:8001/health"),
        ("CarVision API", "http://localhost:8002/health"),
        ("TelecomAI API", "http://localhost:8003/health"),
    ]
    
    results = []
    for name, url in services:
        # TODO: Verificar cada servicio
        pass
    
    return results

def generate_report(results: List[ServiceHealth]) -> str:
    """Genera reporte de salud."""
    # TODO: Implementar
    pass

if __name__ == "__main__":
    results = check_all_services()
    print(generate_report(results))
```

---

## 📝 Módulo 21: Glosario (Autoestudio)

### Ejercicio 21.1: Flashcards de Términos
**Objetivo**: Crear set de flashcards para memorizar términos clave.

```markdown
<!-- Formato: Pregunta | Respuesta -->

¿Qué es Data Drift? | Cambio en la distribución de features entre training y producción

¿Qué es Concept Drift? | Cambio en la relación P(Y|X) entre features y target

¿Diferencia entre Precision y Recall? | Precision=TP/(TP+FP), Recall=TP/(TP+FN)

¿Qué resuelve class_weight='balanced'? | Penaliza más los errores en la clase minoritaria

<!-- TU TAREA: Añadir 20 flashcards más con términos del glosario -->
```

---

## 📝 Módulo 22: Checklist de Producción

### Ejercicio 22.1: Auditoría de Proyecto
**Objetivo**: Aplicar checklist a un proyecto existente.

```markdown
# Auditoría: CarVision-Market-Intelligence

## Código
- [ ] Type hints en todas las funciones
- [ ] Docstrings en clases y métodos públicos
- [ ] Sin secretos hardcodeados
- [ ] Linting pasando (ruff check)

## Testing
- [ ] Coverage >= 80%
- [ ] Tests de datos (schema, rangos)
- [ ] Tests de modelo (predicciones válidas)
- [ ] Tests de integración (API funcional)

## CI/CD
- [ ] Pipeline ejecuta en cada PR
- [ ] Tests ejecutan en múltiples versiones Python
- [ ] Security scanning configurado
- [ ] Docker build automatizado

## Documentación
- [ ] README actualizado
- [ ] Model Card completado
- [ ] API documentada (Swagger)

## Observabilidad
- [ ] Logging estructurado
- [ ] Métricas de Prometheus
- [ ] Health endpoint implementado

<!-- TU TAREA: Ejecutar esta auditoría en el proyecto real -->
<!-- Marcar items completados y crear issues para pendientes -->
```

---

## 📝 Módulo 23: Recursos (Práctica)

### Ejercicio 23.1: Plan de Estudio Personalizado
**Objetivo**: Crear plan basado en gaps identificados.

```markdown
# Mi Plan de Estudio MLOps

## Autoevaluación (1-5)
| Área | Nivel | Prioridad |
|------|:-----:|:---------:|
| Python moderno | ??? | ??? |
| sklearn Pipelines | ??? | ??? |
| Docker | ??? | ??? |
| CI/CD | ??? | ??? |
| Testing | ??? | ??? |
| Observabilidad | ??? | ??? |

## Gaps Identificados
1. ???
2. ???
3. ???

## Recursos Seleccionados
| Gap | Recurso | Tipo | Tiempo |
|-----|---------|------|:------:|
| ??? | ??? | Video/Curso/Doc | ???h |

## Timeline
| Semana | Módulos | Recursos Externos | Entregable |
|:------:|---------|-------------------|------------|
| 1 | ??? | ??? | ??? |
| 2 | ??? | ??? | ??? |

<!-- TU TAREA: Completar basándote en tu autoevaluación honesta -->
```

---

## ✅ Soluciones

Ver [EJERCICIOS_SOLUCIONES.md](EJERCICIOS_SOLUCIONES.md) para las soluciones detalladas.

---

## 📌 Cómo Usar los Ejercicios

1. **Lee el módulo** correspondiente primero
2. **Intenta resolver** sin mirar la solución
3. **Compara** con el código real del portafolio
4. **Valida** ejecutando tests cuando sea posible

### Referencia Rápida al Portafolio

| Módulo | Archivo de Referencia |
|:------:|:----------------------|
| 01 | `BankChurn-Predictor/src/bankchurn/config.py` |
| 03 | Estructura de cualquier proyecto |
| 07 | `BankChurn-Predictor/src/bankchurn/training.py` |
| 08 | `CarVision-Market-Intelligence/src/carvision/features.py` |
| 09 | `BankChurn-Predictor/src/bankchurn/training.py` |
| 11 | `CarVision-Market-Intelligence/tests/conftest.py` |
| 12 | `.github/workflows/ci-mlops.yml` |
| 13 | `BankChurn-Predictor/Dockerfile` |
| 14 | `BankChurn-Predictor/app/fastapi_app.py` |
| 15 | `CarVision-Market-Intelligence/app/streamlit_app.py` |
| 16 | `infra/prometheus-rules.yaml` |
| 17 | `docker-compose.demo.yml` |
| 18 | `k8s/bankchurn-deployment.yaml` |
| 19 | `BankChurn-Predictor/docs/model_card.md` |
| 20 | `scripts/run_demo_tests.sh` |
| 22 | `CHECKLIST_RELEASE.md` |

---

<div align="center">

[← Volver al Índice](00_INDICE.md) | [Ver Soluciones →](EJERCICIOS_SOLUCIONES.md)

</div>
