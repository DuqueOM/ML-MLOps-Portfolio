# 17. Observabilidad para ML

## 🎯 Objetivo del Módulo

Implementar monitoreo completo: logs, métricas, y drift detection como en el portafolio.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  "Si no puedo verlo en un dashboard, no sé si está funcionando."             ║
║                                        — Mentalidad Senior                   ║
║                                                                              ║
║  OBSERVABILIDAD = LOGS + METRICS + TRACES + ML MONITORING                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 📋 Contenido

1. [Las 4 Señales de Oro](#171-las-4-señales-de-oro)
2. [Prometheus + Grafana](#172-prometheus--grafana)
3. [Logging Estructurado](#173-logging-estructurado)
4. [Model Monitoring](#174-model-monitoring)

---

## 17.1 Las 4 Señales de Oro

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     📊 LAS 4 SEÑALES DE ORO (+ ML)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. LATENCIA          ¿Cuánto tarda una predicción?                         │
│     ───────────       Target: P99 < 100ms                                   │
│                       Alerta: P99 > 200ms                                   │
│                                                                             │
│  2. TRÁFICO           ¿Cuántas requests por segundo?                        │
│     ────────          Monitorear: picos, tendencias, anomalías              │
│                                                                             │
│  3. ERRORES           ¿Qué porcentaje de requests falla?                    │
│     ───────           Target: Error rate < 0.1%                             │
│                       Alerta: Error rate > 1%                               │
│                                                                             │
│  4. SATURACIÓN        ¿Cuánto recurso queda?                                │
│     ──────────        Alerta: CPU > 80%, Memory > 85%                       │
│                                                                             │
│  + ML-ESPECÍFICO:                                                           │
│  ────────────────                                                           │
│  5. DATA DRIFT        ¿Los datos de entrada cambiaron?                      │
│  6. PREDICTION DRIFT  ¿Las predicciones cambiaron distribución?             │
│  7. MODEL DECAY       ¿El accuracy está degradando?                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 17.2 Prometheus + Grafana

### Configuración del Portafolio

```yaml
# infra/prometheus-config.yaml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'bankchurn-api'
    static_configs:
      - targets: ['bankchurn:8000']
    metrics_path: /metrics
  
  - job_name: 'carvision-api'
    static_configs:
      - targets: ['carvision:8000']
    metrics_path: /metrics
  
  - job_name: 'telecom-api'
    static_configs:
      - targets: ['telecom:8000']
    metrics_path: /metrics
```

### Métricas en FastAPI

```python
# app/metrics.py

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

# Métricas
PREDICTIONS_TOTAL = Counter(
    'predictions_total',
    'Total de predicciones realizadas',
    ['model', 'result']
)

PREDICTION_LATENCY = Histogram(
    'prediction_latency_seconds',
    'Latencia de predicciones',
    ['model'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

MODEL_LOADED = Gauge(
    'model_loaded',
    'Indica si el modelo está cargado',
    ['model']
)

PREDICTION_PROBABILITY = Histogram(
    'prediction_probability',
    'Distribución de probabilidades predichas',
    ['model'],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)


# Endpoint de métricas
@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )


# Uso en predicción
import time

@app.post("/predict")
async def predict(request: PredictionRequest):
    start = time.time()
    
    # ... predicción ...
    proba = model.predict_proba(df)[0, 1]
    prediction = int(proba >= 0.5)
    
    # Registrar métricas
    latency = time.time() - start
    PREDICTION_LATENCY.labels(model="bankchurn").observe(latency)
    PREDICTIONS_TOTAL.labels(model="bankchurn", result=str(prediction)).inc()
    PREDICTION_PROBABILITY.labels(model="bankchurn").observe(proba)
    
    return {"prediction": prediction, "probability": proba}
```

---

## 17.3 Logging Estructurado

### Configuración Profesional

```python
# src/logging_config.py

import logging
import json
import sys
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Formatter que produce logs en JSON para fácil parsing."""
    
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Añadir extras si existen
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_obj["user_id"] = record.user_id
        if hasattr(record, "prediction"):
            log_obj["prediction"] = record.prediction
        
        # Añadir exception si existe
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_obj)


def setup_logging(level: str = "INFO", json_format: bool = True):
    """Configura logging para producción."""
    
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper()))
    
    handler = logging.StreamHandler(sys.stdout)
    
    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        ))
    
    root.addHandler(handler)
    
    # Silenciar loggers ruidosos
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
```

### Logs con Contexto

```python
import logging
import uuid

logger = logging.getLogger(__name__)

@app.post("/predict")
async def predict(request: PredictionRequest):
    request_id = str(uuid.uuid4())[:8]
    
    # Log con contexto
    logger.info(
        "Prediction request received",
        extra={
            "request_id": request_id,
            "credit_score": request.CreditScore,
            "geography": request.Geography,
        }
    )
    
    try:
        prediction = model.predict(...)
        
        logger.info(
            "Prediction completed",
            extra={
                "request_id": request_id,
                "prediction": prediction,
                "latency_ms": latency * 1000,
            }
        )
        
        return {"prediction": prediction}
    
    except Exception as e:
        logger.error(
            f"Prediction failed: {str(e)}",
            extra={"request_id": request_id},
            exc_info=True
        )
        raise
```

---

## 17.4 Model Monitoring (Drift Detection)

### Script de Drift Detection

```python
# monitoring/check_drift.py - Código REAL del portafolio

"""
Detecta drift en datos usando Evidently AI.

Compara datos de referencia (training) con datos actuales (producción).
Genera reporte HTML y métricas JSON.

Uso:
    python monitoring/check_drift.py --reference data/train.csv --current data/recent.csv
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

import pandas as pd

try:
    from evidently import ColumnMapping
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset, DataQualityPreset
    EVIDENTLY_AVAILABLE = True
except ImportError:
    EVIDENTLY_AVAILABLE = False


def check_drift(
    reference_data: pd.DataFrame,
    current_data: pd.DataFrame,
    output_dir: Path,
    numerical_features: list = None,
    categorical_features: list = None,
) -> dict:
    """
    Ejecuta análisis de drift entre datos de referencia y actuales.
    
    Returns
    -------
    dict
        Métricas de drift incluyendo:
        - dataset_drift: bool (True si hay drift significativo)
        - drift_share: float (% de features con drift)
        - drifted_features: list (features con drift detectado)
    """
    
    if not EVIDENTLY_AVAILABLE:
        return {"error": "Evidently no instalado", "dataset_drift": None}
    
    # Column mapping
    column_mapping = ColumnMapping()
    if numerical_features:
        column_mapping.numerical_features = numerical_features
    if categorical_features:
        column_mapping.categorical_features = categorical_features
    
    # Crear reporte
    report = Report(metrics=[
        DataDriftPreset(),
        DataQualityPreset(),
    ])
    
    report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping
    )
    
    # Guardar HTML
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    html_path = output_dir / f"drift_report_{timestamp}.html"
    report.save_html(str(html_path))
    
    # Extraer métricas
    results = report.as_dict()
    
    drift_metrics = {
        "timestamp": timestamp,
        "reference_rows": len(reference_data),
        "current_rows": len(current_data),
        "dataset_drift": False,
        "drift_share": 0.0,
        "drifted_features": [],
        "report_path": str(html_path),
    }
    
    # Parsear resultados de Evidently
    for metric in results.get("metrics", []):
        if "DataDriftTable" in str(metric.get("metric", "")):
            result = metric.get("result", {})
            drift_metrics["dataset_drift"] = result.get("dataset_drift", False)
            drift_metrics["drift_share"] = result.get("drift_share", 0.0)
            
            # Features con drift
            drift_by_columns = result.get("drift_by_columns", {})
            for col, col_data in drift_by_columns.items():
                if col_data.get("drift_detected", False):
                    drift_metrics["drifted_features"].append(col)
    
    # Guardar métricas JSON
    json_path = output_dir / f"drift_metrics_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(drift_metrics, f, indent=2)
    
    return drift_metrics


def main():
    parser = argparse.ArgumentParser(description="Check data drift")
    parser.add_argument("--reference", required=True, help="Path to reference data CSV")
    parser.add_argument("--current", required=True, help="Path to current data CSV")
    parser.add_argument("--output", default="artifacts", help="Output directory")
    args = parser.parse_args()
    
    reference = pd.read_csv(args.reference)
    current = pd.read_csv(args.current)
    
    metrics = check_drift(reference, current, Path(args.output))
    
    print(json.dumps(metrics, indent=2))
    
    # Exit code basado en drift
    if metrics.get("dataset_drift"):
        print("⚠️ DRIFT DETECTADO")
        exit(1)
    else:
        print("✅ No hay drift significativo")
        exit(0)


if __name__ == "__main__":
    main()
```

### GitHub Action para Drift Scheduled

```yaml
# .github/workflows/drift-detection.yml

name: Drift Detection

on:
  schedule:
    - cron: '0 2 * * *'  # Diario a las 2am UTC
  workflow_dispatch:

jobs:
  check-drift:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pandas evidently
      
      - name: Run drift check
        run: |
          python monitoring/check_drift.py \
            --reference data/reference/train.csv \
            --current data/recent/latest.csv \
            --output artifacts/drift
      
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: drift-report
          path: artifacts/drift/
      
      - name: Create issue if drift detected
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '⚠️ Data Drift Detected',
              body: 'Drift detection workflow failed. Check the artifacts.',
              labels: ['drift', 'monitoring']
            })
```

---

## 🧨 Errores habituales y cómo depurarlos en Observabilidad ML

En observabilidad ML es habitual tener dashboards bonitos pero poca señal útil, o scripts de drift que fallan en silencio.

### 1) Métricas que no aparecen en Prometheus/Grafana

**Síntomas típicos**

- En Grafana, los paneles muestran `No data`.
- En Prometheus, la métrica `predictions_total` no existe o tiene solo ceros.

**Cómo identificarlo**

- Verifica que el endpoint `/metrics` responde localmente (`curl http://localhost:8000/metrics`).
- Revisa `prometheus-config.yaml`:
  - ¿El `job_name` y `targets` apuntan al host/puerto correctos?
  - ¿`metrics_path` es `/metrics`?

**Cómo corregirlo**

- Asegura que el API exponga `/metrics` y que el contenedor esté accesible desde Prometheus (mismo docker network).
- Usa nombres de servicio (`bankchurn:8000`) coherentes con `docker-compose`.

---

### 2) Alertas demasiado ruidosas (alert fatigue)

**Síntomas típicos**

- Canal de Slack/Email lleno de alertas constantes que el equipo ignora.

**Cómo identificarlo**

- Revisa las reglas de alerta: thresholds demasiado agresivos (por ejemplo, alertar por cualquier spike puntual).

**Cómo corregirlo**

- Usa ventanas de tiempo y reglas de severidad (warning vs critical).
- Define claramente métricas **críticas** (latencia P99, error rate, dataset_drift) y otras solo informativas.

---

### 3) Logs JSON imposibles de parsear

**Síntomas típicos**

- La herramienta de logs (ELK, Loki, etc.) no reconoce campos como `request_id` o `prediction`.
- Aparecen líneas mezcladas de formatos distintos.

**Cómo identificarlo**

- Revisa `setup_logging`: ¿todos los handlers usan `JSONFormatter` en producción?
- Busca logs que usen `print` en vez de `logger.info`.

**Cómo corregirlo**

- Centraliza la configuración de logging y evita crear loggers adicionales con otros formatos.
- Usa siempre `extra={...}` en los logs de negocio en vez de concatenar strings.

---

### 4) Script de drift que falla en CI o nunca encuentra drift

**Síntomas típicos**

- El workflow `drift-detection.yml` falla por `ImportError: evidently` o rutas incorrectas.
- El script siempre devuelve "✅ No hay drift" aunque sabes que los datos cambiaron.

**Cómo identificarlo**

- Revisa los paths `--reference` y `--current` usados en el workflow.
- Comprueba que `EVIDENTLY_AVAILABLE` es `True` y que las columnas de referencia/actual coinciden.

**Cómo corregirlo**

- Alinea las rutas de datos de referencia y actuales con la estructura de tu repo.
- Asegúrate de instalar `evidently` en el job de CI (`pip install evidently`).
- Revisa el JSON de métricas generado para validar que `drift_share` y `drifted_features` tienen sentido.

---

### 5) Patrón general de debugging en observabilidad ML

1. Empieza por el **flujo de datos**: API → `/metrics` → Prometheus → Grafana.
2. Verifica que logs y métricas contengan campos de negocio (no solo técnica básica).
3. Revisa periódicamente los umbrales de alerta según el comportamiento real del sistema.
4. Usa los reports de drift como insumo para decisiones, no como verdad absoluta: combínalos con métricas de negocio.

Con esta mentalidad, la observabilidad deja de ser un "extra" y se convierte en tu principal herramienta para operar modelos en producción.

---

## 💼 Consejos Profesionales

> **Recomendaciones para destacar en entrevistas y proyectos reales**

### Para Entrevistas

1. **Observability vs Monitoring**: Monitoring = métricas predefinidas, Observability = entender comportamiento inesperado.

2. **Three Pillars**: Logs, Metrics, Traces. Explica cada uno.

3. **ML Monitoring**: Model drift, data drift, concept drift.

### Para Proyectos Reales

| Situación | Consejo |
|-----------|---------|
| Alertas | Evita alert fatigue: alerta solo lo accionable |
| Dashboards | Un dashboard por audiencia (ops, ML, negocio) |
| On-call | Documenta runbooks para cada alerta |
| Drift detection | Monitorea distribuciones de features y predictions |

### Métricas Clave para ML

- **Serving**: Latency p50/p95/p99, error rate, throughput
- **Model**: Prediction distribution, confidence scores
- **Data**: Missing values, schema changes, drift
- **Business**: Conversion, revenue impact


---

## 📺 Recursos Externos Recomendados

> Ver [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) para la lista completa.

| 🏷️ | Recurso | Tipo |
|:--:|:--------|:-----|
| 🔴 | [Prometheus + Grafana - TechWorld Nana](https://www.youtube.com/watch?v=7gW5pSM6dlU) | Video |
| 🟡 | [ML Monitoring with Evidently](https://www.youtube.com/watch?v=nGFnk7e3R-g) | Video |

**Documentación oficial:**
- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/)
- [Evidently AI](https://docs.evidentlyai.com/)

---

## 🔗 Referencias del Glosario

Ver [21_GLOSARIO.md](21_GLOSARIO.md) para definiciones de:
- **Data Drift**: Cambio en distribución de features
- **Prometheus**: Sistema de monitoreo y alertas
- **PSI**: Population Stability Index

---

## ✅ Ejercicios

Ver [EJERCICIOS.md](EJERCICIOS.md) - Módulo 16:
- **16.1**: Logging estructurado JSON

**Checkpoint:**
- [ ] Tienes endpoint `/metrics` en tu API
- [ ] Logs en formato JSON estructurado
- [ ] Script de drift detection funcional
- [ ] Alertas configuradas para métricas críticas

---

<div align="center">

[← Streamlit Dashboards](15_STREAMLIT.md) | [Siguiente: Despliegue →](17_DESPLIEGUE.md)

</div>
