# 10. Experiment Tracking con MLflow

## 🎯 Objetivo del Módulo

Implementar tracking de experimentos como lo hace el portafolio con `run_mlflow.py`.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  SIN MLFLOW:                           CON MLFLOW:                           ║
║  ───────────                           ────────────                          ║
║  "¿Qué hiperparámetros usé hace        "MLflow run abc123: RF con            ║
║   2 semanas cuando obtuve F1=0.85?"    n_estimators=200, F1=0.85"            ║
║                                                                              ║
║  "¿Dónde guardé ese modelo bueno?"     "Artifacts en run abc123/model.pkl"   ║
║                                                                              ║
║  "¿Por qué este modelo es peor?"       "Comparar runs en UI: diff params"    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### 🧩 Cómo se aplica en este portafolio

- En **BankChurn-Predictor** ya tienes:
  - `scripts/run_mlflow.py` como script de logging posterior al entrenamiento.
  - Configuración de MLflow en `configs/config.yaml` y `src/bankchurn/config.py`.
- El archivo `docker-compose.mlflow.yml` en la raíz del repo levanta un servidor MLflow
  real que puedes usar para practicar este módulo.
- El mismo patrón de logging puedes aplicarlo a **CarVision** y **TelecomAI**, usando
  sus `artifacts/` y modelos entrenados como fuente de métricas y artifacts.

---

## 📋 Contenido

1. [Conceptos de MLflow](#101-conceptos-de-mlflow)
2. [Setup y Configuración](#102-setup-y-configuración)
3. [Logging de Experimentos](#103-logging-de-experimentos)
4. [Model Registry](#104-model-registry)
5. [Código Real del Portafolio](#105-código-real-del-portafolio)

---

## 10.1 Conceptos de MLflow

### Los 4 Componentes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MLFLOW COMPONENTS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. TRACKING                    2. PROJECTS                                 │
│  ─────────────                  ────────────                                │
│  • Log params, metrics          • Empaquetar código                         │
│  • Guardar artifacts            • MLproject file                            │
│  • Comparar runs                • Reproducibilidad                          │
│                                                                             │
│  3. MODELS                      4. REGISTRY                                 │
│  ──────────                     ─────────────                               │
│  • Formato estándar             • Versionado de modelos                     │
│  • Flavors (sklearn, pytorch)   • Staging → Production                      │
│  • Serving                      • Aprobaciones                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

EN ESTE PORTAFOLIO USAMOS: Tracking + Registry
```

### Jerarquía de MLflow

```
MLflow Server
└── Experiment: "BankChurn"
    ├── Run: abc123 (2024-01-15)
    │   ├── Parameters: {n_estimators: 100, max_depth: 10}
    │   ├── Metrics: {f1: 0.60, auc: 0.85}
    │   └── Artifacts: [model.pkl, config.yaml]
    │
    ├── Run: def456 (2024-01-16)
    │   ├── Parameters: {n_estimators: 200, max_depth: 15}
    │   ├── Metrics: {f1: 0.62, auc: 0.86}
    │   └── Artifacts: [model.pkl, config.yaml]
    │
    └── Run: ghi789 (2024-01-17) ← MEJOR
        ├── Parameters: {n_estimators: 200, max_depth: 10}
        ├── Metrics: {f1: 0.65, auc: 0.88}
        └── Artifacts: [model.pkl, config.yaml]
```

---

## 10.2 Setup y Configuración

### Opción 1: Local (File Store)

```python
# Más simple, para desarrollo local
import mlflow

mlflow.set_tracking_uri("file:./mlruns")  # Guarda en carpeta local
mlflow.set_experiment("my-experiment")
```

### Opción 2: Servidor MLflow (Producción)

```yaml
# docker-compose.mlflow.yml del portafolio
services:
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.9.2
    ports:
      - "5000:5000"
    volumes:
      - mlflow-artifacts:/mlflow
    command: >
      mlflow server
      --backend-store-uri sqlite:///mlflow/mlflow.db
      --default-artifact-root /mlflow/artifacts
      --host 0.0.0.0
      --port 5000
```

```python
# Conectar al servidor
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("BankChurn")
```

### Configuración en el Portafolio

```yaml
# configs/config.yaml (BankChurn)
mlflow:
  tracking_uri: "file:./mlruns"      # Local para desarrollo
  experiment_name: "bankchurn"
  enabled: true
```

```python
# src/bankchurn/config.py
class MLflowConfig(BaseModel):
    tracking_uri: str = "file:./mlruns"
    experiment_name: str = "bankchurn"
    enabled: bool = True
```

---

## 10.3 Logging de Experimentos

### API Básica

```python
import mlflow

# Iniciar un run
with mlflow.start_run(run_name="experiment-1"):
    
    # 1. LOG PARAMETERS (hiperparámetros, config)
    mlflow.log_param("n_estimators", 200)
    mlflow.log_param("max_depth", 10)
    mlflow.log_params({  # Múltiples a la vez
        "learning_rate": 0.1,
        "model_type": "random_forest"
    })
    
    # 2. LOG METRICS (resultados)
    mlflow.log_metric("f1_score", 0.65)
    mlflow.log_metric("auc_roc", 0.88)
    mlflow.log_metrics({  # Múltiples a la vez
        "precision": 0.70,
        "recall": 0.61
    })
    
    # 3. LOG ARTIFACTS (archivos)
    mlflow.log_artifact("configs/config.yaml")
    mlflow.log_artifact("artifacts/training_results.json")
    
    # 4. LOG MODEL (modelo serializado con metadata)
    mlflow.sklearn.log_model(
        pipeline,
        artifact_path="model",
        registered_model_name="BankChurnClassifier"
    )
```

### Métricas por Época/Paso

```python
# Para modelos que entrenan por épocas
for epoch in range(100):
    train_loss = train_one_epoch()
    val_loss = validate()
    
    mlflow.log_metrics({
        "train_loss": train_loss,
        "val_loss": val_loss
    }, step=epoch)  # ← step permite graficar evolución
```

---

## 10.4 Model Registry

### Registrar un Modelo

```python
# Durante el run
mlflow.sklearn.log_model(
    pipeline,
    artifact_path="model",
    registered_model_name="BankChurnClassifier"  # ← Registra automáticamente
)

# O después del run
mlflow.register_model(
    model_uri=f"runs:/{run_id}/model",
    name="BankChurnClassifier"
)
```

### Transiciones de Estado

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Promover a Staging
client.transition_model_version_stage(
    name="BankChurnClassifier",
    version=1,
    stage="Staging"
)

# Promover a Production (después de validación)
client.transition_model_version_stage(
    name="BankChurnClassifier",
    version=1,
    stage="Production"
)
```

### Cargar Modelo desde Registry

```python
# Cargar versión específica
model = mlflow.sklearn.load_model("models:/BankChurnClassifier/1")

# Cargar stage específico
model = mlflow.sklearn.load_model("models:/BankChurnClassifier/Production")

# Cargar último modelo (latest)
model = mlflow.sklearn.load_model("models:/BankChurnClassifier/latest")
```

---

## 10.5 Código Real del Portafolio

### scripts/run_mlflow.py (BankChurn)

```python
#!/usr/bin/env python3
"""Log training results to MLflow.

Este script se ejecuta DESPUÉS del entrenamiento para:
1. Leer resultados de artifacts/training_results.json
2. Calcular métricas de negocio (revenue saved, etc.)
3. Loguear todo a MLflow
4. Opcionalmente registrar el modelo

Uso:
    python scripts/run_mlflow.py

Environment Variables:
    MLFLOW_TRACKING_URI: URI del servidor MLflow
    MLFLOW_EXPERIMENT_NAME: Nombre del experimento
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import joblib

try:
    import mlflow
    import mlflow.sklearn
    from mlflow.tracking import MlflowClient
except ImportError:
    mlflow = None

from sklearn.pipeline import Pipeline


def main() -> None:
    # Configuración desde environment
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
    experiment = os.getenv("MLFLOW_EXPERIMENT_NAME", "BankChurn")
    
    # Cargar resultados del entrenamiento
    results_path = Path("artifacts/training_results.json")
    if not results_path.exists():
        print(f"No se encontró {results_path}. Ejecuta training primero.")
        return
    
    data = json.loads(results_path.read_text())
    
    # Extraer métricas
    cv = data.get("cv_results", {})
    test = data.get("test_results", {}).get("metrics", {})
    
    metrics = {}
    for k, v in cv.items():
        if isinstance(v, (int, float)):
            metrics[f"cv_{k}"] = float(v)
    for k, v in test.items():
        if isinstance(v, (int, float)):
            metrics[f"test_{k}"] = float(v)
    
    # Calcular métricas de negocio
    cm = data.get("test_results", {}).get("confusion_matrix")
    if cm and len(cm) == 2:
        tn, fp = cm[0]
        fn, tp = cm[1]
        
        # Parámetros de negocio (configurables)
        clv = float(os.getenv("BC_CLV_USD", "2300"))  # Customer Lifetime Value
        retention_rate = float(os.getenv("BC_RETENTION_RATE", "0.3"))
        
        saved_customers = tp * retention_rate
        saved_revenue = saved_customers * clv
        
        metrics.update({
            "biz_detected_churners": float(tp),
            "biz_saved_customers": saved_customers,
            "biz_saved_revenue_usd": saved_revenue,
            "biz_false_positives": float(fp),
            "biz_missed_churners": float(fn),
        })
    
    if mlflow is None:
        print("MLflow no instalado. Métricas:", metrics)
        return
    
    # Configurar MLflow
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment)
    
    # Crear run
    with mlflow.start_run(run_name="demo-logging"):
        # Log parámetros
        mlflow.log_params({
            "run_type": "demo",
            "source": "run_mlflow.py"
        })
        
        # Log métricas
        mlflow.log_metrics(metrics)
        
        # Log artifacts
        for artifact in [
            Path("artifacts/training_results.json"),
            Path("configs/config.yaml"),
        ]:
            if artifact.exists():
                try:
                    mlflow.log_artifact(str(artifact))
                except PermissionError:
                    print(f"Skipping {artifact}: permission denied")
        
        # Log modelo si existe
        model_path = Path("models/model_v1.0.0.pkl")
        if model_path.exists():
            try:
                obj = joblib.load(model_path)
                if isinstance(obj, dict) and "pipeline" in obj:
                    pipe = obj["pipeline"]
                elif isinstance(obj, Pipeline):
                    pipe = obj
                else:
                    pipe = None
                
                if pipe:
                    mlflow.sklearn.log_model(
                        pipe,
                        artifact_path="model",
                        registered_model_name="BankChurnClassifier"
                    )
            except Exception as e:
                print(f"Model logging skipped: {e}")
        
        print(f"✅ MLflow run logged to {tracking_uri}")
        print(f"   Experiment: {experiment}")
        print(f"   Metrics: {len(metrics)} logged")


if __name__ == "__main__":
    main()
```

### Makefile Integration

```makefile
# Makefile
.PHONY: mlflow-demo mlflow-ui

mlflow-demo:
@echo "Logging to MLflow..."
MLFLOW_TRACKING_URI=file:./mlruns python scripts/run_mlflow.py

mlflow-ui:
@echo "Starting MLflow UI at http://localhost:5000"
mlflow ui --host 0.0.0.0 --port 5000
```

---

## 🧨 Errores habituales y cómo depurarlos en MLflow

MLflow añade una capa extra (servidor, rutas, artefactos), así que muchos errores son de **configuración** más que de código puro.

### 1) Runs que no aparecen en la UI (tracking_uri/experimento incorrectos)

**Síntomas típicos**

- Ejecutas training o `run_mlflow.py` y no ves nada nuevo en `http://localhost:5000`.

**Cómo identificarlo**

- Imprime `mlflow.get_tracking_uri()` y el experimento actual (`mlflow.get_experiment_by_name(...)`).
- Verifica si estás usando `file:./mlruns` mientras tienes un servidor en Docker (`http://localhost:5000`).

**Cómo corregirlo**

- Define claramente en config:
  - Desarrollo local → `tracking_uri: "file:./mlruns"`.
  - Demo/stack Docker → `tracking_uri: "http://mlflow:5000"` o `http://localhost:5000`.
- Asegúrate de que tanto `ChurnTrainer` como `scripts/run_mlflow.py` lean del mismo origen (YAML/env vars).

---

### 2) Errores al registrar modelos (`MlflowException`, permisos, backend)

**Síntomas típicos**

- Al llamar `mlflow.sklearn.log_model(..., registered_model_name=...)` obtienes errores sobre base de datos o registry no configurado.

**Cómo identificarlo**

- Si usas solo `file:./mlruns` sin servidor, el **registry completo** no está disponible.

**Cómo corregirlo**

- Para desarrollo ligero, limita el uso de registry (puedes usar solo tracking + artifacts).
- Para un registry completo, usa el `docker-compose.mlflow.yml` del portafolio con backend SQLite/postgres y apunta `MLFLOW_TRACKING_URI` al servidor.

---

### 3) Artifacts que no se encuentran o no se suben

**Síntomas típicos**

- Errores tipo `FileNotFoundError` al hacer `mlflow.log_artifact`.
- No ves `training_results.json` ni `config.yaml` en la pestaña de artifacts.

**Cómo identificarlo**

- Revisa rutas relativas en `run_mlflow.py` y asegúrate de que ejecutas el script desde la raíz del proyecto.

**Cómo corregirlo**

- Usa rutas consistentes (por ejemplo `artifacts/training_results.json`) y verifica que el archivo exista antes de loguearlo.
- Si corres dentro de Docker, revisa que el volumen monte correctamente `artifacts/` y `configs/`.

---

### 4) Problemas con MLflow en Docker (puertos, hostnames, permisos)

**Síntomas típicos**

- `ConnectionError` al intentar conectar a `http://localhost:5000` desde un contenedor.
- Logs que muestran errores de permisos en `/mlflow`.

**Cómo identificarlo**

- Examina `docker-compose.mlflow.yml` y las variables de entorno de tus servicios.

**Cómo corregirlo**

- Dentro de un contenedor, usa el hostname del servicio (`http://mlflow:5000`) en lugar de `localhost`.
- Asegúrate de que el volumen `mlflow-artifacts` tenga permisos de escritura correctos (usuario del contenedor).

---

### Patrón general de debugging en MLflow

1. **Comprueba tracking_uri y experimento** antes de iniciar el run.
2. **Valida artifacts y modelos**: que los paths existen y se cargan correctamente.
3. **Reproduce localmente con file store** (`file:./mlruns`) antes de ir a servidor Docker.
4. **Verifica desde la UI** que params, metrics y artifacts coincidan con lo que esperas de tu código.

Con este patrón, MLflow pasa de ser “caja negra” a una herramienta confiable para explicar, comparar y promover modelos.

---

## ✅ Ejercicio: Integrar MLflow en TelecomAI

1. Crea `scripts/run_mlflow.py` para TelecomAI
2. Log las métricas: accuracy, f1, precision, recall, roc_auc
3. Calcula métricas de negocio (customers retained, revenue saved)
4. Registra el modelo como "TelecomPlanClassifier"

---

## 📦 Cómo se Usó en el Portafolio

MLflow está integrado en los 3 proyectos del portafolio:

### Configuración MLflow en BankChurn

```python
# BankChurn-Predictor/src/bankchurn/config.py
class MLflowConfig(BaseModel):
    """MLflow tracking configuration."""
    tracking_uri: str = "file:./mlruns"  # Local por defecto
    experiment_name: str = "bankchurn"
    enabled: bool = True
```

### Integración en Trainer

```python
# BankChurn-Predictor/src/bankchurn/trainer.py (extracto)
def _log_to_mlflow(self):
    """Log experimento a MLflow."""
    if not self.config.mlflow.enabled:
        return
    
    mlflow.set_tracking_uri(self.config.mlflow.tracking_uri)
    mlflow.set_experiment(self.config.mlflow.experiment_name)
    
    with mlflow.start_run():
        # Parámetros
        mlflow.log_params({
            "model_type": self.config.model.type,
            "test_size": self.config.model.test_size,
            "cv_folds": self.config.model.cv_folds,
        })
        
        # Métricas
        mlflow.log_metrics(self.metrics_)
        
        # Modelo
        mlflow.sklearn.log_model(self.model_, "model")
```

### Estructura de mlruns/

```
BankChurn-Predictor/
└── mlruns/
    ├── 0/                    # Default experiment
    └── 123456789/            # bankchurn experiment
        └── abc123def456/     # Run ID
            ├── artifacts/
            │   └── model/
            ├── metrics/
            │   ├── accuracy
            │   ├── f1_score
            │   └── roc_auc
            ├── params/
            │   ├── model_type
            │   └── cv_folds
            └── meta.yaml
```

### MLflow por Proyecto

| Proyecto | Tracking URI | Experiment | Métricas Principales |
|----------|--------------|------------|---------------------|
| BankChurn | `file:./mlruns` | `bankchurn` | accuracy, f1, roc_auc |
| CarVision | `file:./mlruns` | `carvision` | mae, rmse, r2 |
| TelecomAI | `file:./mlruns` | `telecomai` | accuracy, f1_weighted |

### 🔧 Ejercicio: Explora MLflow Real

```bash
# 1. Ve a BankChurn
cd BankChurn-Predictor

# 2. Entrena con MLflow habilitado
python main.py --config configs/config.yaml

# 3. Inicia la UI de MLflow
mlflow ui --backend-store-uri file:./mlruns

# 4. Abre en navegador
# http://localhost:5000

# 5. Explora:
# - Compara runs
# - Ve artifacts
# - Registra modelo en Model Registry
```

---

## 💼 Consejos Profesionales

> **Recomendaciones para destacar en entrevistas y proyectos reales**

### Para Entrevistas

1. **MLflow vs W&B vs Neptune**: Conoce trade-offs (MLflow open-source, W&B mejor UI, Neptune escalabilidad).

2. **Model Registry**: Explica stages (Staging → Production → Archived).

3. **Reproducibilidad**: Cómo reconstruir cualquier experimento desde el tracking.

### Para Proyectos Reales

| Situación | Consejo |
|-----------|---------|
| Equipo distribuido | Usa servidor MLflow centralizado |
| Muchos experimentos | Organiza con tags y naming conventions |
| Modelos grandes | Usa artifact storage externo (S3, GCS) |
| Comparación | Siempre registra baseline para comparar |

### Qué Trackear Siempre

- **Params**: Hiperparámetros, versiones de datos
- **Metrics**: Train/val/test, métricas de negocio
- **Artifacts**: Modelo, configs, plots, requirements.txt
- **Tags**: Git commit, autor, dataset version


---

## 📺 Recursos Externos Recomendados

> Ver [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) para la lista completa.

| 🏷️ | Recurso | Tipo |
|:--:|:--------|:-----|
| 🔴 | [MLflow Tutorial - Krish Naik](https://www.youtube.com/watch?v=qdcHHrsXA48) | Video |
| 🟡 | [MLflow Complete Course](https://www.youtube.com/watch?v=MHcqGxA6JPs) | Video |

**Documentación oficial:**
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)

---

## 🔗 Referencias del Glosario

Ver [21_GLOSARIO.md](21_GLOSARIO.md) para definiciones de:
- **MLflow**: Plataforma de experiment tracking
- **Model Registry**: Registro de versiones de modelos
- **Artifact**: Archivo asociado a un experimento

---

## ✅ Ejercicios

Ver [EJERCICIOS.md](EJERCICIOS.md) - Módulo 10:
- **10.1**: MLflow básico (params, metrics, model)
- **10.2**: Comparar múltiples experimentos

---

<div align="center">

[← Training Profesional](09_TRAINING_PROFESIONAL.md) | [Siguiente: Testing ML →](11_TESTING_ML.md)

</div>
