# 📱 TelecomAI Customer Intelligence

**Sistema de Inteligencia de Clientes para recomendar el mejor plan (Smart vs Ultra) en telecomunicaciones**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3+-orange.svg)](https://scikit-learn.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Coverage](https://img.shields.io/badge/Coverage-72%25-green.svg)](tests/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **Sistema ML para recomendar el plan óptimo (Smart vs Ultra) en telecomunicaciones con modelo de clasificación, API REST y experimentación MLOps.**

---

## 🚀 Quick Start (3 Pasos)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Entrenar el mejor modelo (Gradient Boosting + feature engineering)
python main.py --mode train --config configs/config.yaml

# 3. Iniciar la API de inferencia
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000
# Abrir http://localhost:8000/docs para probar /predict
```

---

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#-descripción-del-proyecto)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Modelo](#-modelo)
- [API REST](#-api-rest)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Testing](#-testing)
- [Resultados](#-resultados)
- [Licencia](#-licencia)

---

## 🎯 Descripción del Proyecto

### Problema de Negocio

**Interconnect**, operador de telecomunicaciones, necesita:
- Predecir qué clientes están en riesgo de abandonar el servicio
- Implementar estrategias proactivas de retención
- Reducir el costo de adquisición vs retención (5-25x más barato retener)
- Identificar factores clave que causan churn

### Solución Implementada

- ✅ **Modelo de clasificación tabular** para recomendar plan **Ultra** vs **Smart**
- ✅ **API REST** de inferencia con FastAPI para integrar en productos o dashboards
- ✅ **Preprocesamiento con ingeniería de features** (ratios de uso por llamada y por minuto)
- ✅ **Pipeline reproducible** de entrenamiento, evaluación y predicción vía CLI
- ✅ **Experimentación sistemática** multi-modelo con MLflow (`scripts/run_experiments.py`)
- ✅ **Monitoreo de drift sencillo** con test estadísticos (KS, PSI) (`monitoring/check_drift.py`)

### Tecnologías

- **ML**: Scikit-learn (Logistic Regression, Random Forest, Gradient Boosting)
- **API**: FastAPI + Uvicorn
- **MLOps**: MLflow para tracking de experimentos + script propio de drift (KS/PSI)
- **Testing**: pytest (≈72% coverage)

### Dataset

- **Fuente**: `users_behavior.csv` (dataset educativo de TripleTen)
- **Registros**: ~3,214 clientes
- **Features de entrada**: `calls`, `minutes`, `messages`, `mb_used`
- **Target**: `is_ultra` (1 = recomendar plan Ultra, 0 = plan Smart)
- **Tipo**: datos tabulares numéricos de comportamiento mensual (uso de voz, SMS y datos)

---

## 💻 Instalación

### Requisitos

- Python 3.10+
- 4GB RAM
- 1GB espacio en disco

### Instalación Local

```bash
cd TelecomAI-Customer-Intelligence

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar
python -c "import sklearn, fastapi; print('✓ OK')"
```

### Con pyproject.toml

```bash
pip install -e ".[dev]"
```

### Docker

```bash
docker build -t telecomai:latest .
docker run -p 8000:8000 telecomai:latest
```

---

## 🚀 Uso

### CLI principal

#### 1. Entrenamiento

```bash
python main.py --mode train --config configs/config.yaml
```

**Salidas principales:**
- `artifacts/model.joblib`: modelo entrenado (scikit-learn estimator)
- `artifacts/preprocessor.joblib`: pipeline de preprocesamiento (incluye `FeatureEngineer` + escalado)
- `artifacts/metrics.json`: métricas (accuracy, precision, recall, f1, roc_auc)
- `artifacts/confusion_matrix.png`: matriz de confusión del split holdout
- `artifacts/roc_curve.png`: curva ROC del split holdout
- `models/model_v1.0.0.pkl`: pipeline completo (`preprocess` + `clf`) listo para carga directa

#### 2. Evaluación rápida

```bash
python main.py --mode eval --config configs/config.yaml
```

Reutiliza los artefactos guardados y vuelve a generar métricas y plots.

#### 3. Predicción batch

```bash
python main.py --mode predict \
  --config configs/config.yaml \
  --input_csv users_behavior.csv \
  --output_path artifacts/predictions.csv
```

Genera `artifacts/predictions.csv` con columnas `pred_is_ultra` y `proba_is_ultra`.

### Makefile

```bash
make install   # Instalar dependencias
make train     # Entrenar modelo con la config por defecto
make eval      # Evaluar modelo entrenado
make predict   # Predicción batch de ejemplo
make serve     # Lanzar API FastAPI en http://localhost:8000
```

### Experimentos con MLflow

```bash
# Búsqueda aleatoria de hiperparámetros y modelos (logreg, random_forest, gradient_boosting)
python scripts/run_experiments.py \
  --config configs/config.yaml \
  --n_iter 3 \
  --seed 42

# Run de logging de ejemplo usando artifacts/metrics.json
python scripts/run_mlflow.py

# UI de MLflow para explorar runs
mlflow ui --port 5000
# Abrir http://localhost:5000
```

---

## 🎓 Modelo

### Problema de ML

- **Tarea**: clasificación binaria `is_ultra` (1 = recomendar plan Ultra, 0 = plan Smart).
- **Entrada**: comportamiento de uso mensual (`calls`, `minutes`, `messages`, `mb_used`).
- **Salida**: probabilidad de que el cliente deba migrar al plan Ultra.

### Arquitectura del pipeline

- **Preprocesamiento** (`data/preprocess.py`):
  - Imputación mediana y estandarización de variables numéricas.
  - `FeatureEngineer` añade features derivadas:
    - `minutes_per_call`: minutos promedio por llamada.
    - `messages_per_call`: mensajes promedio por llamada.
    - `mb_per_minute`: MB usados por minuto de llamada.
- **Modelos soportados** (`main.build_model`):
  - `logreg`: `LogisticRegression` como baseline lineal interpretable.
  - `random_forest`: `RandomForestClassifier` para capturar relaciones no lineales.
  - `gradient_boosting`: `GradientBoostingClassifier` como modelo de alto rendimiento.

El modelo por defecto configurado en `configs/config.yaml` es:

- `GradientBoostingClassifier(n_estimators=200, max_depth=2, learning_rate=0.05)`.

### Métricas clave (holdout 20 %, seed=42)

Los experimentos ejecutados con `scripts/run_experiments.py` muestran que el mejor modelo (`gradient_boosting`) alcanza aproximadamente:

| Métrica   | Valor aproximado |
|-----------|------------------|
| Accuracy  | ~0.82            |
| Precision | ~0.83            |
| Recall    | ~0.53            |
| F1-Score  | ~0.65            |
| ROC AUC   | ~0.85            |

Los valores exactos para cada entrenamiento se registran en `artifacts/metrics.json` y en MLflow.

---

## 🌐 API REST

### Endpoints

#### Health Check

```bash
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

#### Predicción individual

```bash
POST /predict
```

Request body (JSON):

```json
{
  "calls": 100,
  "minutes": 500,
  "messages": 50,
  "mb_used": 20000
}
```

Response de ejemplo:

```json
{
  "prediction": 1,
  "probability_is_ultra": 0.71
}
```

- `prediction`: 1 = recomendar plan Ultra, 0 = plan Smart.
- `probability_is_ultra`: probabilidad estimada de que el cliente sea perfil Ultra.

### Documentación interactiva

`http://localhost:8000/docs` (Swagger UI)

---

## 📁 Estructura del Proyecto

```text
TelecomAI-Customer-Intelligence/
├── app/
│   └── fastapi_app.py          # API de inferencia (FastAPI)
├── configs/
│   └── config.yaml             # Configuración de datos, modelo y MLflow
├── data/
│   ├── preprocess.py           # Preprocesamiento + FeatureEngineer
│   └── __init__.py
├── monitoring/
│   └── check_drift.py          # Script simple de data drift (KS, PSI, Evidently opcional)
├── scripts/
│   ├── run_experiments.py      # Búsqueda aleatoria de modelos + logging en MLflow
│   └── run_mlflow.py           # Ejemplo de logging de métricas de negocio
├── artifacts/                  # Artefactos generados (modelo, métricas, plots)
├── models/                     # Modelos exportados (pipeline completo)
├── tests/                      # Tests unitarios
├── main.py                     # CLI de entrenamiento/evaluación/predicción
├── evaluate.py                 # Utilidades de métricas y visualizaciones
├── model_card.md               # Ficha del modelo
└── data_card.md                # Ficha del dataset
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Con coverage
pytest --cov=. --cov-report=term-missing

# Tests específicos
pytest tests/test_model.py -v
```

### Coverage: 72%

```
Name                    Stmts   Miss  Cover
--------------------------------------------
main.py                   263     74    72%
data/preprocess.py         89     25    72%
evaluate.py                78     22    72%
app/fastapi_app.py         65     18    72%
--------------------------------------------
TOTAL                     495    139    72%
```

---

## 📈 Resultados

### Rendimiento del modelo actual

Para el mejor modelo configurado actualmente (`gradient_boosting` con feature engineering) en un split holdout del 20 % se obtienen típicamente métricas en el rango:

| Métrica   | Valor aproximado |
|-----------|------------------|
| Accuracy  | ~0.82            |
| Precision | ~0.83            |
| Recall    | ~0.53            |
| F1-Score  | ~0.65            |
| ROC AUC   | ~0.85            |

Las métricas exactas por experimento se pueden consultar en:

- `artifacts/metrics.json`
- UI de MLflow (`mlruns/` o servidor remoto configurado)

### Artefactos generados

- `artifacts/confusion_matrix.png`: vista rápida de errores tipo FP/FN.
- `artifacts/roc_curve.png`: trade-off sensibilidad/especificidad.
- `artifacts/predictions.csv`: ejemplo de predicciones batch.

### Insights de negocio (ilustrativos)

- Usuarios con **alto uso combinado de minutos y datos** suelen ser buenos candidatos para el plan **Ultra**.
- Clientes con **bajo uso en todas las dimensiones** se mantienen mejor en el plan **Smart**.
- Los ratios derivados (`minutes_per_call`, `mb_per_minute`) ayudan a distinguir perfiles de heavy users vs uso ocasional.

---

## 🚀 Mejoras Futuras

- [ ] Deep Learning con redes neuronales
- [ ] Análisis de series temporales del comportamiento
- [ ] Sistema de recomendaciones personalizadas
- [ ] A/B testing de estrategias de retención
- [ ] Dashboard en tiempo real con Streamlit

---

## 📚 Documentación

- **[Model Card](model_card.md)**: Ficha técnica
- **[Data Card](data_card.md)**: Documentación de datos
- **[Notebooks](notebooks/)**: Análisis exploratorios

---

## 📄 Licencia

MIT License - Ver [LICENSE](../LICENSE)

### Autor
**Duque Ortega Mutis (DuqueOM)**

### Contacto
- Portfolio: [github.com/DuqueOM](https://github.com/DuqueOM)
- LinkedIn: [linkedin.com/in/duqueom](https://linkedin.com/in/duqueom)

---

**⭐ Star this project if you find it useful!**
