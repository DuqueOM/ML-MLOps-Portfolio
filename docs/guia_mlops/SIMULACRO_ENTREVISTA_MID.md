# 🎯 Simulacro de Entrevista Mid-Level ML Engineer
## Portafolio MLOps — 60 Preguntas Técnicas

**Nivel**: Mid (2-4 años de experiencia)  
**Versión**: 1.0 | Diciembre 2025

---

## 📋 Índice

1. [Pipelines y Arquitectura](#1-pipelines-y-arquitectura-preguntas-1-15)
2. [MLOps Práctico](#2-mlops-práctico-preguntas-16-30)
3. [Testing y Calidad](#3-testing-y-calidad-preguntas-31-40)
4. [Deployment y APIs](#4-deployment-y-apis-preguntas-41-50)
5. [Escenarios Prácticos](#5-escenarios-prácticos-preguntas-51-60)

---

## 🎯 ¿Qué se espera de un Mid-Level?

| Sí se espera | No se espera (aún) |
|--------------|-------------------|
| Diseñar pipelines end-to-end | Arquitecturas distribuidas complejas |
| Implementar CI/CD funcional | Optimización de infraestructura a escala |
| Debugging autónomo | Mentoring de equipos |
| Code reviews | Decisiones de arquitectura críticas |
| Escribir tests comprehensivos | Diseño de sistemas desde cero |

---

# 1. Pipelines y Arquitectura (Preguntas 1-15)

## Pregunta 1: Pipeline Unificado
**¿Por qué usar un Pipeline unificado en lugar de artefactos separados?**

### Respuesta:
```python
# ❌ Antes: artefactos separados
preprocessor = joblib.load("preprocessor.pkl")
model = joblib.load("model.pkl")
X = preprocessor.transform(X)
pred = model.predict(X)

# ✅ Después: pipeline unificado
pipe = joblib.load("pipeline.joblib")
pred = pipe.predict(X)  # Todo en uno
```

**Beneficios**:
1. Elimina training-serving skew
2. Single source of truth
3. Versionado simple
4. Deploy más limpio

---

## Pregunta 2: ColumnTransformer
**Explica el ColumnTransformer del portafolio.**

### Respuesta:
```python
preprocessor = ColumnTransformer([
    ('num', Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ]), numerical_cols),
    ('cat', Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
        ('encoder', OneHotEncoder(handle_unknown='ignore'))
    ]), categorical_cols),
], remainder='drop')
```

**Procesa columnas en paralelo**: numéricas y categóricas tienen transformaciones distintas.

---

## Pregunta 3: Custom Transformer
**¿Cuándo crear un transformer personalizado?**

### Respuesta:
```python
class FeatureEngineer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X = X.copy()
        X['vehicle_age'] = 2024 - X['model_year']
        return X
```

**Cuándo usar**:
- Lógica de negocio específica
- Features derivadas
- Transformaciones no estándar

---

## Pregunta 4: Estratified Split
**¿Por qué stratify=y en train_test_split?**

### Respuesta:
```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
```

Con clases desbalanceadas (80/20 churn), `stratify=y` garantiza que train y test mantengan la misma proporción. Sin esto, un split aleatorio podría dar 85/15 en train y 70/30 en test.

---

## Pregunta 5: Hyperparameter Tuning
**¿Cómo optimizas hiperparámetros?**

### Respuesta:
```python
from sklearn.model_selection import RandomizedSearchCV

param_dist = {
    'model__n_estimators': [50, 100, 200],
    'model__max_depth': [5, 10, 20, None]
}

search = RandomizedSearchCV(
    pipe, param_dist, n_iter=20, cv=5, scoring='f1'
)
search.fit(X_train, y_train)
print(search.best_params_)
```

**GridSearch vs RandomizedSearch**: Random es más eficiente con muchos parámetros.

---

## Pregunta 6: Métricas de Negocio
**¿Cómo traduces métricas ML a valor de negocio?**

### Respuesta:
```python
# Costo de falsos negativos (cliente que churns sin detectar)
cost_fn = 500  # Costo de adquisición de nuevo cliente

# Costo de falsos positivos (retención innecesaria)
cost_fp = 50   # Costo de campaña de retención

# Costo total
total_cost = (FN * cost_fn) + (FP * cost_fp)
```

Optimizar para **minimizar costo total**, no solo accuracy.

---

## Pregunta 7: Ensemble Methods
**Explica VotingClassifier con soft voting.**

### Respuesta:
```python
ensemble = VotingClassifier([
    ('lr', LogisticRegression()),
    ('rf', RandomForestClassifier())
], voting='soft', weights=[0.4, 0.6])
```

- **Soft voting**: Promedia probabilidades (mejor que votos binarios)
- **Weights**: RF tiene más peso porque tiene mejor AUC individual
- **Complementariedad**: LR lineal + RF no-lineal = menor varianza

---

## Pregunta 8: Cross-Validation Avanzado
**¿Cuándo usar TimeSeriesSplit vs StratifiedKFold?**

### Respuesta:
| Tipo | Usar cuando |
|------|-------------|
| StratifiedKFold | Clasificación con clases desbalanceadas |
| TimeSeriesSplit | Datos temporales (evitar data leakage temporal) |
| GroupKFold | Datos con grupos (ej: múltiples muestras por paciente) |

```python
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
# Train: [1,2,3], Test: [4]
# Train: [1,2,3,4], Test: [5]
```

---

## Pregunta 9: Feature Importance
**¿Cómo explicas qué features son importantes?**

### Respuesta:
```python
# 1. Importancia de RF
importances = model.feature_importances_

# 2. Permutation importance (más robusto)
from sklearn.inspection import permutation_importance
perm = permutation_importance(model, X_test, y_test)

# 3. SHAP (más interpretable)
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)
```

---

## Pregunta 10: Handling Categorical High Cardinality
**¿Cómo manejas categorías con muchos valores únicos?**

### Respuesta:
```python
# 1. Target encoding (con cuidado de leakage)
from category_encoders import TargetEncoder
encoder = TargetEncoder()

# 2. Frequency encoding
X['brand_freq'] = X['brand'].map(X['brand'].value_counts(normalize=True))

# 3. Grouping rare categories
X['brand'] = X['brand'].apply(lambda x: x if freq[x] > 0.01 else 'Other')
```

---

## Pregunta 11: Reproducibilidad
**¿Cómo garantizas experimentos reproducibles?**

### Respuesta:
```python
# 1. Seeds
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

# 2. Config versionada
config = BankChurnConfig.from_yaml("configs/config.yaml")

# 3. MLflow tracking
mlflow.log_params(config.model.dict())
mlflow.log_artifact("configs/config.yaml")

# 4. Dependencias fijas
# pyproject.toml con versiones específicas
```

---

## Pregunta 12: Data Validation
**¿Cómo validas datos de entrada en producción?**

### Respuesta:
```python
from pydantic import BaseModel, Field, validator

class PredictionInput(BaseModel):
    credit_score: int = Field(ge=300, le=850)
    age: int = Field(ge=18, le=100)
    geography: str
    
    @validator('geography')
    def validate_geography(cls, v):
        valid = ['France', 'Germany', 'Spain']
        if v not in valid:
            raise ValueError(f'Must be one of {valid}')
        return v
```

Pydantic valida antes de que llegue al modelo.

---

## Pregunta 13: Config Management
**¿Por qué Pydantic para configuración?**

### Respuesta:
```python
class ModelConfig(BaseModel):
    model_type: Literal["rf", "lr", "xgb"]
    n_estimators: int = Field(ge=10, le=1000)
    
    @validator('n_estimators')
    def validate_estimators(cls, v, values):
        if values.get('model_type') == 'lr' and v != 1:
            raise ValueError('LR no usa n_estimators')
        return v
```

**Beneficios**: Validación automática, tipos claros, errores descriptivos, documentación implícita.

---

## Pregunta 14: Artifact Management
**¿Cómo organizas artefactos del modelo?**

### Respuesta:
```
artifacts/
├── pipeline.joblib       # Modelo + preprocessor
├── training_results.json # Métricas
├── config.yaml          # Config usada
└── feature_names.json   # Features esperadas
```

```python
# Guardar
joblib.dump(pipe, 'artifacts/pipeline.joblib')
with open('artifacts/training_results.json', 'w') as f:
    json.dump(metrics, f)
```

---

## Pregunta 15: Model Versioning
**¿Cómo versionas modelos?**

### Respuesta:
```python
# 1. MLflow Model Registry
mlflow.sklearn.log_model(pipe, "model")
# Registrar como v1, v2, etc.

# 2. Naming convention
model_name = f"bankchurn_v{version}_{timestamp}.joblib"

# 3. Git tags
git tag -a v1.0.0 -m "Model v1.0.0: AUC 0.85"
```

---

# 2. MLOps Práctico (Preguntas 16-30)

## Pregunta 16: MLflow Tracking
**¿Cómo usas MLflow para tracking?**

### Respuesta:
```python
import mlflow

with mlflow.start_run():
    mlflow.log_params({"n_estimators": 100, "max_depth": 10})
    mlflow.log_metrics({"auc": 0.85, "f1": 0.78})
    mlflow.sklearn.log_model(pipe, "model")
    mlflow.log_artifact("configs/config.yaml")
```

---

## Pregunta 17: DVC
**¿Para qué usas DVC?**

### Respuesta:
```bash
# Trackear datos
dvc add data/raw/Churn.csv

# Push a remote
dvc push

# Pull datos
dvc pull
```

**Beneficio**: Versionar datos grandes sin subirlos a Git.

---

## Pregunta 18: GitHub Actions CI
**Explica el workflow CI del portafolio.**

### Respuesta:
```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -e ".[dev]"
      - run: pytest tests/ --cov=src
      - run: ruff check src/
```

**Flujo**: Push → Install → Test → Lint → Pass/Fail badge.

---

## Pregunta 19: Pre-commit Hooks
**¿Qué hooks usas?**

### Respuesta:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
```

Ejecutan automáticamente antes de cada commit.

---

## Pregunta 20: Docker Multi-stage
**Explica el Dockerfile del portafolio.**

### Respuesta:
```dockerfile
# Build stage
FROM python:3.11-slim AS builder
COPY requirements.txt .
RUN pip wheel --no-cache-dir -w /wheels -r requirements.txt

# Runtime stage
FROM python:3.11-slim
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*
COPY . /app
USER nonroot
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]
```

**Multi-stage**: Build pesado en stage 1, runtime ligero en stage 2.

---

## Pregunta 21: Training-Serving Skew
**¿Qué es training-serving skew y cómo lo evitas?**

### Respuesta:
Training-serving skew ocurre cuando el modelo ve datos diferentes en producción vs entrenamiento.

**Causas comunes**:
```python
# ❌ MAL: Preprocesamiento diferente
# Training
X_train['age_normalized'] = (X_train['age'] - X_train['age'].mean()) / X_train['age'].std()

# Serving (usa stats de producción, no de training!)
X_prod['age_normalized'] = (X_prod['age'] - X_prod['age'].mean()) / X_prod['age'].std()
```

**Solución: Pipeline unificado**:
```python
# ✅ BIEN: Todo en un pipeline
pipe = Pipeline([
    ('scaler', StandardScaler()),  # Guarda mean/std de training
    ('model', RandomForestClassifier())
])
pipe.fit(X_train, y_train)
joblib.dump(pipe, 'model.joblib')

# En producción: mismo pipeline
pipe = joblib.load('model.joblib')
pred = pipe.predict(X_new)  # Usa stats de training
```

---

## Pregunta 22: Data Drift Detection
**¿Cómo detectas data drift en producción?**

### Respuesta:
```python
from evidently.metrics import DataDriftTable
from evidently.report import Report

# Comparar distribuciones
report = Report(metrics=[DataDriftTable()])
report.run(reference_data=X_train, current_data=X_prod)
report.save_html("drift_report.html")
```

**Métodos estadísticos**:
| Método | Uso | Umbral típico |
|--------|-----|---------------|
| **PSI** (Population Stability Index) | Categóricas | >0.2 = drift significativo |
| **KS-test** (Kolmogorov-Smirnov) | Numéricas | p-value < 0.05 |
| **JS Divergence** | Distribuciones | >0.1 = drift |

**En el portafolio**: Configurable en `16_OBSERVABILIDAD.md`.

---

## Pregunta 23: Métricas de Producción
**¿Qué métricas monitoreas en producción?**

### Respuesta:
```python
# Prometheus metrics en FastAPI
from prometheus_client import Counter, Histogram

PREDICTIONS = Counter('predictions_total', 'Total predictions', ['model_version'])
LATENCY = Histogram('prediction_latency_seconds', 'Prediction latency')

@app.post("/predict")
async def predict(data: Input):
    with LATENCY.time():
        result = model.predict(data)
    PREDICTIONS.labels(model_version="v1.2").inc()
    return result
```

**Métricas clave**:
| Categoría | Métricas |
|-----------|----------|
| **Rendimiento** | Latencia p50/p95/p99, throughput |
| **Disponibilidad** | Error rate, uptime |
| **ML específicas** | Prediction distribution, feature distributions |
| **Negocio** | Conversiones, costos evitados |

---

## Pregunta 24: Rollback de Modelos
**¿Cómo haces rollback si un modelo falla?**

### Respuesta:
```python
# 1. Versionado de modelos
models/
├── v1.0.0/pipeline.joblib  # ← Rollback aquí
├── v1.1.0/pipeline.joblib
└── v1.2.0/pipeline.joblib  # Actual (fallando)

# 2. Blue-Green deployment
# deployment.yaml
spec:
  replicas: 2
  selector:
    matchLabels:
      version: v1.1.0  # Cambiar a versión anterior

# 3. Con MLflow
client = MlflowClient()
client.transition_model_version_stage(
    name="bankchurn",
    version=3,
    stage="Production"  # Promover versión anterior
)
```

**Proceso de rollback**:
1. Detectar degradación (alertas de métricas)
2. Cambiar variable de entorno o config
3. Reiniciar pods / recargar modelo
4. Verificar métricas post-rollback

---

## Pregunta 25: A/B Testing en ML
**¿Cómo implementas A/B testing para modelos?**

### Respuesta:
```python
import random

@app.post("/predict")
async def predict(data: Input, user_id: str):
    # Asignar bucket consistente por usuario
    bucket = hash(user_id) % 100
    
    if bucket < 10:  # 10% tráfico
        model = model_v2  # Challenger
        version = "v2"
    else:
        model = model_v1  # Champion
        version = "v1"
    
    result = model.predict(data)
    
    # Logging para análisis
    log_prediction(user_id, version, result)
    
    return {"prediction": result, "model_version": version}
```

**Métricas a comparar**:
- Accuracy/F1 en cohortes
- Métricas de negocio (conversión, revenue)
- Latencia y error rate

---

## Pregunta 26: Manejo de Secrets
**¿Cómo manejas secrets y credenciales?**

### Respuesta:
```python
# ❌ MAL: Hardcoded
API_KEY = "TU_API_KEY_AQUI"  # EJEMPLO, NO USAR EN PRODUCCIÓN

# ✅ BIEN: Variables de entorno
import os
API_KEY = os.getenv("API_KEY")

# ✅ MEJOR: python-dotenv
from dotenv import load_dotenv
load_dotenv()  # Carga .env
API_KEY = os.getenv("API_KEY")
```

**.env (nunca en Git)**:
```bash
# .env (valores de ejemplo)
API_KEY=REEMPLAZAR_EN_ENTORNO_REAL
DB_PASSWORD=REEMPLAZAR_EN_ENTORNO_REAL
```

**.gitignore**:
```gitignore
.env
.env.*
!.env.example
```

**En CI/CD**: GitHub Secrets → `${{ secrets.API_KEY }}`

---

## Pregunta 27: Feature Store
**¿Qué es un feature store y cuándo usarlo?**

### Respuesta:
Feature store = repositorio centralizado de features reutilizables.

```python
# Sin feature store (problema)
# Equipo A: calcula age_bucket de una forma
# Equipo B: calcula age_bucket de otra forma
# → Inconsistencia

# Con feature store (solución)
from feast import FeatureStore

store = FeatureStore(repo_path=".")
features = store.get_online_features(
    features=["customer:age_bucket", "customer:tenure_months"],
    entity_rows=[{"customer_id": "C123"}]
)
```

**Cuándo usar**:
| Situación | Feature Store |
|-----------|---------------|
| 1-2 modelos, equipo pequeño | No necesario |
| Múltiples modelos, features compartidas | Recomendado |
| Features en tiempo real | Muy recomendado |

---

## Pregunta 28: Escalado de Inferencia
**¿Cómo escalas inferencia para alto tráfico?**

### Respuesta:
```yaml
# Kubernetes HPA (Horizontal Pod Autoscaler)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bankchurn-api
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
```

**Estrategias**:
| Estrategia | Cuándo |
|------------|--------|
| **HPA** | Tráfico variable, latencia crítica |
| **Batch processing** | Alto volumen, latencia flexible |
| **Caching** | Inputs repetidos frecuentes |
| **Model optimization** | Latencia muy baja requerida |

---

## Pregunta 29: Logging en ML
**¿Qué información loggeas en producción?**

### Respuesta:
```python
import logging
import json

logger = logging.getLogger(__name__)

@app.post("/predict")
async def predict(data: Input):
    request_id = str(uuid.uuid4())
    
    # Log de entrada
    logger.info(json.dumps({
        "event": "prediction_request",
        "request_id": request_id,
        "features": data.dict(),
        "timestamp": datetime.utcnow().isoformat()
    }))
    
    start = time.time()
    result = model.predict(data)
    latency = time.time() - start
    
    # Log de salida
    logger.info(json.dumps({
        "event": "prediction_response",
        "request_id": request_id,
        "prediction": result,
        "probability": float(proba),
        "latency_ms": latency * 1000,
        "model_version": "v1.2.0"
    }))
    
    return result
```

**Logs esenciales**: request_id, inputs, outputs, latencia, versión, errores.

---

## Pregunta 30: Retraining Automático
**¿Cómo automatizas el retraining?**

### Respuesta:
```yaml
# GitHub Actions scheduled workflow
name: Weekly Retrain
on:
  schedule:
    - cron: '0 2 * * 0'  # Domingos 2am
  workflow_dispatch:  # Manual trigger

jobs:
  retrain:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -e ".[dev]"
      - run: python main.py --config configs/config.yaml
      - run: python scripts/evaluate.py --threshold 0.80
      - run: |
          if [ $? -eq 0 ]; then
            echo "Model passed threshold, deploying..."
            # Deploy logic
          fi
```

**Triggers de retraining**:
| Trigger | Implementación |
|---------|----------------|
| **Scheduled** | Cron jobs, Airflow |
| **Data drift** | Alerta → trigger workflow |
| **Performance degradation** | Métricas bajo umbral |
| **New data volume** | X nuevos registros |

---

# 3. Testing y Calidad (Preguntas 31-40)

## Pregunta 31: Tipos de Tests
**¿Qué tipos de tests tiene el portafolio?**

### Respuesta:
```python
# Unit test
def test_feature_engineer():
    fe = FeatureEngineer()
    result = fe.transform(sample_df)
    assert 'vehicle_age' in result.columns

# Integration test
def test_training_pipeline():
    trainer = Trainer(config)
    trainer.fit(X, y)
    assert trainer.model_ is not None

# API test
def test_predict_endpoint():
    response = client.post("/predict", json=sample_input)
    assert response.status_code == 200
```

---

## Pregunta 32: Fixtures
**¿Cómo usas fixtures en pytest?**

### Respuesta:
```python
@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'CreditScore': [650, 700],
        'Age': [35, 45],
        'Exited': [0, 1]
    })

@pytest.fixture
def trained_model(sample_data):
    trainer = Trainer(config)
    trainer.fit(sample_data)
    return trainer

def test_predict(trained_model, sample_data):
    preds = trained_model.predict(sample_data)
    assert len(preds) == len(sample_data)
```

---

## Pregunta 33: Coverage
**¿Cuánto coverage es suficiente?**

### Respuesta:
```bash
pytest tests/ --cov=src --cov-report=html
```

| Nivel | Coverage | Comentario |
|-------|----------|------------|
| Mínimo | 70% | Lo básico |
| Bueno | 80% | Estándar industria |
| Excelente | 90%+ | Código crítico |

**El portafolio tiene 79% en BankChurn.**

---

## Pregunta 34: Property-Based Testing
**¿Qué es property-based testing?**

### Respuesta:
En lugar de casos específicos, defines **propiedades** que siempre deben cumplirse.

```python
from hypothesis import given, strategies as st

@given(
    credit_score=st.integers(min_value=300, max_value=850),
    age=st.integers(min_value=18, max_value=100)
)
def test_prediction_is_valid(credit_score, age):
    """Propiedad: la predicción siempre es 0 o 1."""
    input_data = {"credit_score": credit_score, "age": age}
    pred = model.predict(pd.DataFrame([input_data]))
    assert pred[0] in [0, 1]

@given(df=st.data())
def test_feature_engineer_preserves_rows(df):
    """Propiedad: FeatureEngineer no cambia número de filas."""
    sample = df.draw(st.dataframes(columns=[
        st.column("age", dtype=int),
        st.column("salary", dtype=float)
    ]))
    result = fe.transform(sample)
    assert len(result) == len(sample)
```

**Ventaja**: Encuentra edge cases que no pensaste.

---

## Pregunta 35: Testing de Modelos ML
**¿Cómo testeas que un modelo funciona correctamente?**

### Respuesta:
```python
# 1. Test de smoke: modelo carga y predice
def test_model_loads_and_predicts():
    model = joblib.load("artifacts/pipeline.joblib")
    sample = pd.DataFrame([{"CreditScore": 650, "Age": 35}])
    pred = model.predict(sample)
    assert len(pred) == 1

# 2. Test de formato de salida
def test_prediction_format():
    pred = model.predict(X_test)
    assert pred.shape == (len(X_test),)
    assert set(pred).issubset({0, 1})

# 3. Test de rendimiento mínimo
def test_model_performance():
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    assert accuracy >= 0.75, f"Accuracy {accuracy} below threshold"

# 4. Test de invarianza
def test_prediction_deterministic():
    pred1 = model.predict(X_test)
    pred2 = model.predict(X_test)
    assert np.array_equal(pred1, pred2)
```

---

## Pregunta 36: Mocking
**¿Qué es mocking y cuándo usarlo?**

### Respuesta:
Mocking = reemplazar dependencias reales con objetos simulados.

```python
from unittest.mock import Mock, patch

# Mockear llamada a API externa
@patch('myapp.external_api.get_customer_data')
def test_predict_with_external_data(mock_api):
    # Configurar mock
    mock_api.return_value = {"credit_score": 700, "age": 45}
    
    # Test usa el mock en lugar de API real
    result = predict_for_customer("C123")
    
    # Verificar que se llamó
    mock_api.assert_called_once_with("C123")
    assert result is not None

# Mockear modelo para test de API
@patch('app.fastapi_app.model')
def test_predict_endpoint(mock_model):
    mock_model.predict.return_value = np.array([1])
    mock_model.predict_proba.return_value = np.array([[0.2, 0.8]])
    
    response = client.post("/predict", json=sample_input)
    assert response.json()["prediction"] == 1
```

**Cuándo usar**: APIs externas, base de datos, servicios lentos.

---

## Pregunta 37: Testing de APIs
**¿Cómo testeas endpoints de FastAPI?**

### Respuesta:
```python
from fastapi.testclient import TestClient
from app.fastapi_app import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict_valid_input():
    response = client.post("/predict", json={
        "credit_score": 650,
        "age": 35,
        "geography": "France"
    })
    assert response.status_code == 200
    assert "prediction" in response.json()
    assert "probability" in response.json()

def test_predict_invalid_input():
    response = client.post("/predict", json={
        "credit_score": 9999,  # Fuera de rango
        "age": 35
    })
    assert response.status_code == 422  # Validation error

def test_predict_missing_field():
    response = client.post("/predict", json={
        "credit_score": 650
        # Falta age
    })
    assert response.status_code == 422
```

---

## Pregunta 38: Parametrized Tests
**¿Cómo evitas duplicación en tests?**

### Respuesta:
```python
import pytest

@pytest.mark.parametrize("credit_score,age,expected", [
    (300, 18, 0),   # Mínimos válidos
    (850, 100, 1),  # Máximos válidos
    (650, 45, 0),   # Caso típico
])
def test_prediction_cases(credit_score, age, expected):
    input_data = {"credit_score": credit_score, "age": age}
    pred = model.predict(pd.DataFrame([input_data]))
    # Solo verificamos que no falla, no el valor exacto
    assert pred[0] in [0, 1]

@pytest.mark.parametrize("invalid_input,expected_error", [
    ({"credit_score": -1}, "greater than or equal to 300"),
    ({"credit_score": 1000}, "less than or equal to 850"),
    ({"age": 5}, "greater than or equal to 18"),
])
def test_validation_errors(invalid_input, expected_error):
    response = client.post("/predict", json=invalid_input)
    assert response.status_code == 422
    assert expected_error in str(response.json())
```

---

## Pregunta 39: Testing de Edge Cases
**¿Cómo testeas edge cases en ML?**

### Respuesta:
```python
# 1. Inputs vacíos
def test_empty_dataframe():
    df = pd.DataFrame()
    with pytest.raises(ValueError):
        model.predict(df)

# 2. Nulls
def test_missing_values():
    df = pd.DataFrame([{"CreditScore": None, "Age": 35}])
    # Pipeline debe manejar o fallar graciosamente
    result = model.predict(df)  # O pytest.raises si debe fallar

# 3. Outliers extremos
def test_extreme_values():
    df = pd.DataFrame([{
        "CreditScore": 850,
        "Age": 100,
        "Balance": 1_000_000_000  # Outlier extremo
    }])
    pred = model.predict(df)
    assert pred[0] in [0, 1]  # No falla

# 4. Tipos incorrectos
def test_wrong_types():
    with pytest.raises(Exception):
        model.predict("not a dataframe")

# 5. Columnas faltantes
def test_missing_columns():
    df = pd.DataFrame([{"CreditScore": 650}])  # Falta Age
    with pytest.raises(KeyError):
        model.predict(df)
```

---

## Pregunta 40: Test-Driven Development (TDD)
**¿Cómo aplicas TDD en ML?**

### Respuesta:
TDD: Escribir test → Ver que falla → Implementar → Ver que pasa → Refactorizar.

```python
# 1. Escribir test primero
def test_feature_engineer_creates_age_bucket():
    df = pd.DataFrame({"age": [25, 45, 65]})
    fe = FeatureEngineer()
    result = fe.transform(df)
    
    assert "age_bucket" in result.columns
    assert list(result["age_bucket"]) == ["young", "middle", "senior"]

# 2. Test falla (FeatureEngineer no existe aún)
# 3. Implementar mínimo para pasar
class FeatureEngineer(BaseEstimator, TransformerMixin):
    def transform(self, X):
        X = X.copy()
        X["age_bucket"] = pd.cut(
            X["age"], 
            bins=[0, 30, 50, 100],
            labels=["young", "middle", "senior"]
        )
        return X

# 4. Test pasa ✓
# 5. Refactorizar si es necesario
```

**En ML, TDD es útil para**:
- Feature engineering (definir comportamiento esperado)
- Validación de datos
- APIs

---

# 4. Deployment y APIs (Preguntas 41-50)

## Pregunta 41: FastAPI Basics
**Muestra un endpoint de predicción.**

### Respuesta:
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Input(BaseModel):
    credit_score: int
    age: int

@app.post("/predict")
def predict(data: Input):
    X = pd.DataFrame([data.dict()])
    pred = model.predict(X)
    return {"prediction": int(pred[0])}
```

---

## Pregunta 42: Health Checks
**¿Por qué tener /health endpoint?**

### Respuesta:
```python
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "version": "1.0.0"
    }
```

Kubernetes usa esto para saber si el pod está listo.

---

## Pregunta 43: Uvicorn y ASGI
**¿Qué es uvicorn y por qué usarlo?**

### Respuesta:
Uvicorn = servidor ASGI (Asynchronous Server Gateway Interface) de alto rendimiento.

```bash
# Desarrollo
uvicorn app.fastapi_app:app --reload --port 8000

# Producción
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000 --workers 4
```

**Configuración para producción**:
```python
# Con gunicorn + uvicorn workers
gunicorn app.fastapi_app:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

**ASGI vs WSGI**:
| WSGI | ASGI |
|------|------|
| Sync only | Async + Sync |
| Flask, Django | FastAPI, Starlette |
| Una request a la vez por worker | Múltiples requests concurrentes |

---

## Pregunta 44: CORS Configuration
**¿Cómo manejas CORS en FastAPI?**

### Respuesta:
CORS = Cross-Origin Resource Sharing. Necesario cuando frontend y backend están en dominios distintos.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React dev
        "https://myapp.example.com",  # Production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

**En producción**: Especificar orígenes exactos, no usar `"*"`.

---

## Pregunta 45: Async en FastAPI
**¿Cuándo usar async def vs def?**

### Respuesta:
```python
# Sync: operaciones CPU-bound o librerías sync
@app.post("/predict")
def predict(data: Input):
    result = model.predict(data)  # sklearn es sync
    return {"prediction": result}

# Async: operaciones I/O-bound
@app.get("/external-data")
async def get_external():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
    return response.json()
```

**Regla general**:
| Operación | Usar |
|-----------|------|
| sklearn, pandas, joblib | `def` (sync) |
| HTTP requests, DB async | `async def` |
| File I/O masivo | `async def` con aiofiles |

---

## Pregunta 46: Model Caching
**¿Cómo evitas cargar el modelo en cada request?**

### Respuesta:
```python
# FastAPI: lru_cache
from functools import lru_cache

@lru_cache()
def get_model():
    return joblib.load("artifacts/pipeline.joblib")

@app.post("/predict")
def predict(data: Input):
    model = get_model()  # Cacheado después del primer call
    return model.predict(data)

# Alternativa: cargar al inicio
model = None

@app.on_event("startup")
async def load_model():
    global model
    model = joblib.load("artifacts/pipeline.joblib")
```

**Streamlit**:
```python
@st.cache_resource
def load_model():
    return joblib.load("artifacts/pipeline.joblib")

model = load_model()  # Cacheado entre reruns
```

---

## Pregunta 47: Streamlit Dashboard
**¿Cómo creas un dashboard de predicción?**

### Respuesta:
```python
import streamlit as st
import pandas as pd

st.title("🏦 BankChurn Predictor")

# Sidebar para inputs
st.sidebar.header("Customer Data")
credit_score = st.sidebar.slider("Credit Score", 300, 850, 650)
age = st.sidebar.slider("Age", 18, 100, 35)
geography = st.sidebar.selectbox("Geography", ["France", "Germany", "Spain"])

# Cargar modelo (cacheado)
@st.cache_resource
def load_model():
    return joblib.load("artifacts/pipeline.joblib")

model = load_model()

# Predicción
if st.sidebar.button("Predict"):
    input_df = pd.DataFrame([{
        "CreditScore": credit_score,
        "Age": age,
        "Geography": geography
    }])
    
    prediction = model.predict(input_df)[0]
    proba = model.predict_proba(input_df)[0, 1]
    
    col1, col2 = st.columns(2)
    col1.metric("Prediction", "Churn" if prediction else "Stay")
    col2.metric("Probability", f"{proba:.1%}")
```

---

## Pregunta 48: Docker Compose para ML
**¿Cómo orquestas múltiples servicios?**

### Respuesta:
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL_PATH=/app/artifacts/pipeline.joblib
    volumes:
      - ./artifacts:/app/artifacts:ro
    depends_on:
      - mlflow
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  mlflow:
    image: python:3.11-slim
    command: mlflow server --host 0.0.0.0
    ports:
      - "5000:5000"
    volumes:
      - ./mlruns:/mlflow/mlruns

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

```bash
docker-compose up -d
docker-compose logs -f api
```

---

## Pregunta 49: Kubernetes Deployment
**¿Cómo despliegas en Kubernetes?**

### Respuesta:
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bankchurn-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bankchurn-api
  template:
    metadata:
      labels:
        app: bankchurn-api
    spec:
      containers:
      - name: api
        image: bankchurn-api:v1.0.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: bankchurn-api
spec:
  selector:
    app: bankchurn-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

```bash
kubectl apply -f deployment.yaml
kubectl get pods
kubectl logs -f deployment/bankchurn-api
```

---

## Pregunta 50: Horizontal Pod Autoscaler
**¿Cómo escalas automáticamente?**

### Respuesta:
```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bankchurn-api-hpa
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
      stabilizationWindowSeconds: 300  # Esperar 5 min antes de escalar down
    scaleUp:
      stabilizationWindowSeconds: 60   # Escalar up más rápido
```

```bash
kubectl apply -f hpa.yaml
kubectl get hpa
# NAME                  REFERENCE              TARGETS   MINPODS   MAXPODS   REPLICAS
# bankchurn-api-hpa     Deployment/bankchurn   45%/70%   2         10        3
```

---

# 5. Escenarios Prácticos (Preguntas 51-60)

## Pregunta 51: Debug de Producción
**El modelo tiene accuracy 85% en dev pero 60% en prod. ¿Por qué?**

### Respuesta:
1. **Data drift**: Distribución de datos cambió
2. **Feature mismatch**: Features procesadas diferente
3. **Training-serving skew**: Preprocesamiento distinto
4. **Datos de prod con más ruido**: Edge cases no vistos

**Acciones**: Comparar distribuciones, revisar pipeline, logging de inputs.

---

## Pregunta 52: Code Review
**¿Qué buscas en un code review de ML?**

### Respuesta:
- [ ] Data leakage en split/preprocessing
- [ ] Tests para features y modelo
- [ ] Config externalizada (no hardcoded)
- [ ] Type hints y docstrings
- [ ] Reproducibilidad (seeds, versiones)
- [ ] Logging apropiado

---

## Pregunta 53: Explicabilidad del Modelo
**El cliente dice: "No puedo usar tu modelo si no me explicas por qué toma las decisiones".**

### Respuesta:
```python
import shap

# 1. SHAP para explicaciones individuales
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_sample)

# Waterfall plot para una predicción
shap.waterfall_plot(shap.Explanation(
    values=shap_values[0],
    base_values=explainer.expected_value,
    data=X_sample.iloc[0]
))

# 2. Feature importance global
shap.summary_plot(shap_values, X_sample)

# 3. En producción: incluir en respuesta
@app.post("/predict")
def predict(data: Input):
    pred = model.predict(X)[0]
    
    # Top 3 razones
    shap_vals = explainer.shap_values(X)
    top_features = sorted(
        zip(feature_names, shap_vals[0]),
        key=lambda x: abs(x[1]),
        reverse=True
    )[:3]
    
    return {
        "prediction": pred,
        "explanation": [
            {"feature": f, "impact": v} 
            for f, v in top_features
        ]
    }
```

---

## Pregunta 54: Optimización de Latencia
**El modelo tarda 500ms por predicción. El negocio necesita <100ms.**

### Respuesta:
```python
# 1. Profiling: ¿dónde está el cuello de botella?
import cProfile
cProfile.run('model.predict(X_sample)')

# 2. Opciones de optimización:

# a) Modelo más ligero
from sklearn.linear_model import LogisticRegression
# LR es 10x más rápido que RF

# b) Reducir features
from sklearn.feature_selection import SelectKBest
selector = SelectKBest(k=10)  # Solo top 10 features

# c) Batch predictions
@app.post("/predict/batch")
def predict_batch(items: List[Input]):
    X = pd.DataFrame([item.dict() for item in items])
    preds = model.predict(X)  # Una llamada, muchas predicciones
    return {"predictions": preds.tolist()}

# d) Caching de predicciones frecuentes
from functools import lru_cache

@lru_cache(maxsize=1000)
def predict_cached(credit_score: int, age: int):
    return model.predict([[credit_score, age]])[0]

# e) ONNX para inferencia rápida
from skl2onnx import convert_sklearn
onnx_model = convert_sklearn(model, initial_types=[...])
```

**Métricas de latencia**:
| Optimización | Latencia típica |
|--------------|-----------------|
| RF sklearn | 50-200ms |
| LR sklearn | 1-5ms |
| ONNX | 1-10ms |
| Caching (hit) | <1ms |

---

## Pregunta 55: Manejo de PII
**El dataset contiene nombres, emails y teléfonos. ¿Cómo lo manejas?**

### Respuesta:
```python
# 1. Identificar columnas PII
pii_columns = ["name", "email", "phone", "ssn", "address"]

# 2. Anonimización
import hashlib

def anonymize_pii(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in pii_columns:
        if col in df.columns:
            # Hash irreversible
            df[col] = df[col].apply(
                lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16]
            )
    return df

# 3. Drop antes de training (mejor opción)
X = df.drop(columns=pii_columns, errors='ignore')

# 4. En logs: nunca loggear PII
logger.info(f"Prediction for customer {customer_id[:4]}***")

# 5. En respuestas de API: mascarar
def mask_email(email: str) -> str:
    parts = email.split("@")
    return f"{parts[0][:2]}***@{parts[1]}"
```

**Compliance checklist**:
- [ ] PII no está en features del modelo
- [ ] PII no aparece en logs
- [ ] PII no se almacena en MLflow/tracking
- [ ] Acceso a datos restringido

---

## Pregunta 56: Fairness y Bias
**Producto detectó que el modelo rechaza más a clientes de cierta región.**

### Respuesta:
```python
from fairlearn.metrics import MetricFrame
from sklearn.metrics import accuracy_score, recall_score

# 1. Calcular métricas por grupo
metrics = MetricFrame(
    metrics={
        "accuracy": accuracy_score,
        "recall": recall_score
    },
    y_true=y_test,
    y_pred=y_pred,
    sensitive_features=df_test["geography"]
)

print(metrics.by_group)
#              accuracy  recall
# geography
# France         0.85     0.80
# Germany        0.83     0.78
# Spain          0.70     0.55  # ← Problema

# 2. Mitigación
from fairlearn.reductions import ExponentiatedGradient
from fairlearn.constraints import DemographicParity

mitigator = ExponentiatedGradient(
    estimator=base_model,
    constraints=DemographicParity()
)
mitigator.fit(X_train, y_train, sensitive_features=train_geography)

# 3. Monitoreo continuo
# Alertar si la diferencia entre grupos > 10%
```

---

## Pregunta 57: Tests Flaky en CI
**El CI pasa 80% de las veces y falla 20% sin cambios en código.**

### Respuesta:
```python
# 1. Problema común: Random sin seed
# ❌ Mal
model = RandomForestClassifier()

# ✅ Bien
model = RandomForestClassifier(random_state=42)

# 2. Problema: Orden de ejecución
# ❌ Mal: test depende de otro
def test_predict():
    assert model.predict(X) == [1]  # model de test anterior

# ✅ Bien: tests aislados
@pytest.fixture
def trained_model():
    m = Model()
    m.fit(X, y)
    return m

def test_predict(trained_model):
    assert trained_model.predict(X)

# 3. Problema: Timeouts en CI
# ❌ Mal
requests.get("https://external-api.com", timeout=5)

# ✅ Bien
@pytest.fixture
def mock_api():
    with patch("myapp.api.get") as mock:
        mock.return_value = {"data": "test"}
        yield mock

# 4. Debug: Correr múltiples veces
pytest tests/ --count=10  # Con pytest-repeat
```

---

## Pregunta 58: Modelo Grande para Deploy
**El modelo pesa 2GB y tarda 30s en cargar. ¿Cómo optimizas?**

### Respuesta:
```python
# 1. Quantization (reducir precisión)
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic

quantize_dynamic(
    "model.onnx",
    "model_quantized.onnx",
    weight_type=ort.QuantType.QInt8
)
# 2GB → ~500MB

# 2. Model distillation (modelo más pequeño que imita al grande)
teacher = load_large_model()
student = SmallModel()

# Entrenar student con outputs del teacher
student_preds = student(X)
teacher_preds = teacher(X)
loss = mse_loss(student_preds, teacher_preds)

# 3. Feature selection (menos features = modelo más pequeño)
from sklearn.feature_selection import SelectFromModel
selector = SelectFromModel(model, threshold="median")
X_reduced = selector.transform(X)  # Menos columnas

# 4. Lazy loading en API
model = None

@app.on_event("startup")
async def load():
    global model
    model = joblib.load("model.joblib")  # Solo una vez
```

---

## Pregunta 59: Muchos Falsos Positivos
**El modelo predice churn para clientes que claramente no van a irse.**

### Respuesta:
```python
# 1. Ajustar threshold (default=0.5)
y_proba = model.predict_proba(X_test)[:, 1]

# Encontrar threshold óptimo
from sklearn.metrics import precision_recall_curve

precision, recall, thresholds = precision_recall_curve(y_test, y_proba)

# Threshold que maximiza F1
f1_scores = 2 * (precision * recall) / (precision + recall)
optimal_threshold = thresholds[np.argmax(f1_scores)]
print(f"Optimal threshold: {optimal_threshold}")  # Ej: 0.65

# Usar nuevo threshold
y_pred = (y_proba >= optimal_threshold).astype(int)

# 2. Revisar balance de datos
print(y_train.value_counts(normalize=True))
# Si muy desbalanceado: SMOTE, class_weight

# 3. Verificar data leakage
# ¿Hay features que "predicen perfectamente"?
for col in X.columns:
    corr = X[col].corr(y)
    if abs(corr) > 0.9:
        print(f"⚠️ {col} tiene correlación {corr}")
```

---

## Pregunta 60: Comunicar a Stakeholders No Técnicos
**El VP de producto pregunta: "¿Funciona o no funciona tu modelo?"**

### Respuesta:
```python
# 1. Traducir métricas técnicas a impacto de negocio
"""
❌ Mal: "El modelo tiene AUC 0.85 y F1 0.78"

✅ Bien: 
"Por cada 100 clientes que van a hacer churn:
- Detectamos 78 antes de que se vayan
- De los que marcamos como riesgo, 82% efectivamente se iban

Impacto: Si cada cliente perdido cuesta $500,
el modelo puede prevenir $31,200 en pérdidas mensuales
(78 clientes × $500 × 80% tasa de retención con intervención)"
"""

# 2. Visualizaciones claras
import plotly.express as px

# Confusion matrix visual
fig = px.imshow(
    [[TN, FP], [FN, TP]],
    labels=dict(x="Predicted", y="Actual"),
    x=["Stay", "Churn"],
    y=["Stay", "Churn"],
    text_auto=True
)
fig.show()

# 3. Dashboard ejecutivo en Streamlit
st.metric("Clientes en Riesgo", "234", delta="-12 vs mes pasado")
st.metric("Precision Retención", "82%", delta="+5%")
st.metric("Ahorro Estimado", "$45,000/mes")
```

**Regla de oro**: Siempre conectar con dinero o KPIs que el stakeholder ya conoce.

---

# 📚 Recursos

| Tema | Módulo |
|------|--------|
| Pipelines | [07_SKLEARN_PIPELINES.md](07_SKLEARN_PIPELINES.md) |
| Testing | [11_TESTING_ML.md](11_TESTING_ML.md) |
| CI/CD | [12_CI_CD.md](12_CI_CD.md) |
| Docker | [13_DOCKER.md](13_DOCKER.md) |
| FastAPI | [14_FASTAPI.md](14_FASTAPI.md) |
| MLflow | [10_EXPERIMENT_TRACKING.md](10_EXPERIMENT_TRACKING.md) |

---

<div align="center">

**¡Éxito en tu entrevista! 🚀**

[← Simulacro Junior](SIMULACRO_ENTREVISTA_JUNIOR.md) | [Simulacro Senior →](SIMULACRO_ENTREVISTA_SENIOR_PARTE1.md)

</div>
