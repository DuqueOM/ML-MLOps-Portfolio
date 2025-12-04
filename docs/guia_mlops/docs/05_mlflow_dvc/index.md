# 05 — MLflow & DVC

> **Tiempo estimado**: 3 días (24 horas)
> 
> **Prerrequisitos**: Módulos 01-04 completados

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Configurar **MLflow** para tracking local
2. ✅ Registrar **experimentos, métricas y artefactos**
3. ✅ Usar **DVC** para versionado de datos
4. ✅ Crear **pipelines DVC** reproducibles

---

## 📖 Contenido Teórico

### 1. MLflow Básico

#### Instalación y Setup

```bash
pip install mlflow
```

#### Tracking de Experimentos

```python
"""mlflow_tracking.py — Tracking con MLflow."""
import mlflow
from mlflow.models import infer_signature
import pandas as pd


def setup_mlflow(
    experiment_name: str = "default",
    tracking_uri: str = "file:./mlruns",
) -> None:
    """Configura MLflow para tracking local."""
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)


def train_with_tracking(
    pipeline,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    params: dict,
) -> str:
    """Entrena modelo con tracking de MLflow.
    
    Returns:
        run_id del experimento
    """
    with mlflow.start_run() as run:
        # Log parámetros
        mlflow.log_params(params)
        
        # Entrenar
        pipeline.fit(X_train, y_train)
        
        # Evaluar
        y_pred = pipeline.predict(X_val)
        y_proba = pipeline.predict_proba(X_val)[:, 1]
        
        from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
        
        metrics = {
            "accuracy": accuracy_score(y_val, y_pred),
            "roc_auc": roc_auc_score(y_val, y_proba),
            "f1": f1_score(y_val, y_pred),
        }
        
        # Log métricas
        mlflow.log_metrics(metrics)
        
        # Log modelo
        signature = infer_signature(X_train, y_pred)
        mlflow.sklearn.log_model(
            pipeline,
            artifact_path="model",
            signature=signature,
        )
        
        # Log artefactos adicionales
        # mlflow.log_artifact("reports/metrics.json")
        
        return run.info.run_id


# Uso
setup_mlflow("churn_prediction")
run_id = train_with_tracking(pipeline, X_train, y_train, X_val, y_val, params)
print(f"Run ID: {run_id}")
```

#### Iniciar UI de MLflow

```bash
# En terminal
mlflow ui --port 5000

# Abrir en navegador: http://localhost:5000
```

---

### 2. MLflow Model Registry

```python
"""registry.py — Registro de modelos."""
import mlflow
from mlflow.tracking import MlflowClient


def register_model(run_id: str, model_name: str) -> str:
    """Registra un modelo en el registry.
    
    Returns:
        Versión del modelo registrado
    """
    model_uri = f"runs:/{run_id}/model"
    result = mlflow.register_model(model_uri, model_name)
    return result.version


def transition_model_stage(
    model_name: str,
    version: str,
    stage: str = "Production",
) -> None:
    """Cambia el stage de un modelo."""
    client = MlflowClient()
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage=stage,
    )


def load_production_model(model_name: str):
    """Carga el modelo en producción."""
    model_uri = f"models:/{model_name}/Production"
    return mlflow.sklearn.load_model(model_uri)
```

---

### 3. DVC Básico

#### Inicialización

```bash
# Inicializar DVC en el proyecto
dvc init

# Agregar remote local (o S3, GCS, etc.)
dvc remote add -d local_remote /tmp/dvc-storage

# Estructura creada
# .dvc/
# ├── config
# └── .gitignore
```

#### Versionado de Datos

```bash
# Agregar archivo a DVC
dvc add data/raw/customers.csv

# Esto crea:
# data/raw/customers.csv.dvc  (metadatos)
# data/raw/.gitignore         (ignora el CSV)

# Commit los metadatos a Git
git add data/raw/customers.csv.dvc data/raw/.gitignore
git commit -m "feat: add customers dataset v1"

# Push datos al remote
dvc push
```

#### dvc.yaml — Pipeline Reproducible

```yaml
# dvc.yaml
stages:
  prepare:
    cmd: python src/prepare.py
    deps:
      - src/prepare.py
      - data/raw/customers.csv
    outs:
      - data/processed/train.parquet
      - data/processed/test.parquet

  train:
    cmd: python src/train.py
    deps:
      - src/train.py
      - data/processed/train.parquet
    params:
      - model.n_estimators
      - model.max_depth
    outs:
      - models/pipeline.pkl
    metrics:
      - reports/metrics.json:
          cache: false

  evaluate:
    cmd: python src/evaluate.py
    deps:
      - src/evaluate.py
      - models/pipeline.pkl
      - data/processed/test.parquet
    metrics:
      - reports/evaluation.json:
          cache: false
```

#### Comandos DVC

```bash
# Ejecutar pipeline
dvc repro

# Ver estado del pipeline
dvc status

# Ver métricas
dvc metrics show

# Comparar experimentos
dvc metrics diff

# Ver gráfico del pipeline
dvc dag
```

---

### 4. Integración MLflow + DVC

```python
"""train.py — Training con MLflow y DVC."""
import mlflow
import yaml
import json
from pathlib import Path


def load_params(params_file: str = "params.yaml") -> dict:
    """Carga parámetros desde params.yaml (DVC)."""
    with open(params_file) as f:
        return yaml.safe_load(f)


def main():
    # Cargar parámetros (versionados por DVC)
    params = load_params()
    model_params = params.get("model", {})
    
    # Setup MLflow
    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("churn_prediction")
    
    with mlflow.start_run():
        # Log params
        mlflow.log_params(model_params)
        
        # Cargar datos (versionados por DVC)
        train_df = pd.read_parquet("data/processed/train.parquet")
        
        # Entrenar
        # ...
        
        # Guardar métricas (DVC las rastrea)
        metrics = {"accuracy": 0.85, "f1": 0.78}
        Path("reports").mkdir(exist_ok=True)
        with open("reports/metrics.json", "w") as f:
            json.dump(metrics, f)
        
        # Log a MLflow también
        mlflow.log_metrics(metrics)
        
        # Guardar modelo (DVC lo rastrea)
        joblib.dump(pipeline, "models/pipeline.pkl")
        mlflow.sklearn.log_model(pipeline, "model")


if __name__ == "__main__":
    main()
```

---

## 🔧 Mini-Proyecto: Tracking Local

### Objetivo

1. Configurar MLflow tracking local
2. Entrenar modelo con logging
3. Inicializar DVC
4. Crear pipeline reproducible

### Estructura

```
work/05_mlflow_dvc/
├── src/
│   ├── prepare.py
│   ├── train.py
│   └── evaluate.py
├── data/
│   ├── raw/
│   └── processed/
├── models/
├── reports/
├── mlruns/           # MLflow tracking
├── dvc.yaml          # Pipeline DVC
├── params.yaml       # Parámetros
└── .dvc/             # Config DVC
```

### Criterios de Éxito

- [ ] `mlflow ui` muestra experimentos
- [ ] `dvc repro` ejecuta pipeline
- [ ] Métricas en `reports/metrics.json`
- [ ] Modelo en `models/pipeline.pkl`

---

## ✅ Validación

```bash
make check-05
```

---

## ➡️ Siguiente Módulo

**[06 — Despliegue API](../06_despliegue_api/index.md)**

---

*Última actualización: 2024-12*
