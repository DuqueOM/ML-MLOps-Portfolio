# 10 — Observabilidad & Monitoring

> **Tiempo estimado**: 2 días (16 horas)
> 
> **Prerrequisitos**: Módulos 01-09 completados

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Implementar **logging estructurado**
2. ✅ Medir **métricas de inferencia** (latencia, error rate)
3. ✅ Detectar **data/model drift**
4. ✅ Configurar **alertas básicas**

---

## 📖 Contenido Teórico

### 1. Logging Estructurado

```python
"""logging_config.py — Configuración de logging."""
import logging
import json
from datetime import datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formatter que produce logs en JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Agregar campos extra
        if hasattr(record, "extra"):
            log_obj.update(record.extra)
        
        return json.dumps(log_obj)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configura logging estructurado."""
    logger = logging.getLogger("ml_api")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler con JSON
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    return logger


# Uso
logger = setup_logging()
logger.info("Modelo cargado", extra={"model_version": "1.0.0"})
logger.info("Predicción realizada", extra={"latency_ms": 45, "customer_id": "C001"})
```

---

### 2. Métricas de Inferencia

```python
"""metrics.py — Métricas de la API."""
import time
from functools import wraps
from collections import defaultdict
from typing import Callable
import threading


class MetricsCollector:
    """Colector de métricas en memoria."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._request_count = 0
        self._error_count = 0
        self._latencies: list[float] = []
        self._predictions: dict[str, int] = defaultdict(int)
    
    def record_request(self, latency_ms: float, success: bool, prediction: str = None):
        """Registra una request."""
        with self._lock:
            self._request_count += 1
            self._latencies.append(latency_ms)
            
            if not success:
                self._error_count += 1
            
            if prediction:
                self._predictions[prediction] += 1
    
    def get_stats(self) -> dict:
        """Retorna estadísticas actuales."""
        with self._lock:
            if not self._latencies:
                return {"error": "No data"}
            
            latencies = sorted(self._latencies)
            return {
                "request_count": self._request_count,
                "error_count": self._error_count,
                "error_rate": self._error_count / self._request_count if self._request_count else 0,
                "latency_p50_ms": latencies[len(latencies) // 2],
                "latency_p95_ms": latencies[int(len(latencies) * 0.95)],
                "latency_p99_ms": latencies[int(len(latencies) * 0.99)],
                "predictions": dict(self._predictions),
            }
    
    def reset(self):
        """Resetea métricas."""
        with self._lock:
            self._request_count = 0
            self._error_count = 0
            self._latencies = []
            self._predictions = defaultdict(int)


# Singleton global
metrics = MetricsCollector()


def track_latency(func: Callable) -> Callable:
    """Decorador para medir latencia."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            latency = (time.perf_counter() - start) * 1000
            metrics.record_request(latency, success=True)
            return result
        except Exception as e:
            latency = (time.perf_counter() - start) * 1000
            metrics.record_request(latency, success=False)
            raise
    return wrapper
```

---

### 3. Drift Detection

```python
"""drift.py — Detección de drift."""
import numpy as np
import pandas as pd
from scipy import stats
from typing import Optional


class DriftDetector:
    """Detector de drift en features y predicciones."""
    
    def __init__(self, reference_data: pd.DataFrame, threshold: float = 0.05):
        self.reference = reference_data
        self.threshold = threshold
        self._reference_stats = self._compute_stats(reference_data)
    
    def _compute_stats(self, df: pd.DataFrame) -> dict:
        """Calcula estadísticas de referencia."""
        stats_dict = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            stats_dict[col] = {
                "mean": df[col].mean(),
                "std": df[col].std(),
                "quantiles": df[col].quantile([0.25, 0.5, 0.75]).to_dict(),
            }
        return stats_dict
    
    def check_drift(self, current_data: pd.DataFrame) -> dict:
        """Verifica drift en datos actuales.
        
        Returns:
            Dict con resultados por feature
        """
        results = {}
        
        for col in self._reference_stats.keys():
            if col not in current_data.columns:
                continue
            
            ref = self.reference[col].dropna()
            cur = current_data[col].dropna()
            
            # Kolmogorov-Smirnov test
            ks_stat, p_value = stats.ks_2samp(ref, cur)
            
            # Detectar drift si p-value < threshold
            drift_detected = p_value < self.threshold
            
            results[col] = {
                "drift_detected": drift_detected,
                "ks_statistic": float(ks_stat),
                "p_value": float(p_value),
                "ref_mean": float(ref.mean()),
                "cur_mean": float(cur.mean()),
                "mean_shift": float(cur.mean() - ref.mean()),
            }
        
        return results
    
    def check_prediction_drift(
        self,
        reference_preds: np.ndarray,
        current_preds: np.ndarray,
    ) -> dict:
        """Verifica drift en predicciones."""
        ks_stat, p_value = stats.ks_2samp(reference_preds, current_preds)
        
        return {
            "drift_detected": p_value < self.threshold,
            "ks_statistic": float(ks_stat),
            "p_value": float(p_value),
            "ref_mean": float(np.mean(reference_preds)),
            "cur_mean": float(np.mean(current_preds)),
        }
```

---

### 4. Alertas Básicas

```python
"""alerts.py — Sistema de alertas."""
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Representa una alerta."""
    name: str
    level: AlertLevel
    message: str
    metric_value: float
    threshold: float


class AlertManager:
    """Gestor de alertas."""
    
    def __init__(self):
        self._rules: list[dict] = []
        self._handlers: list[Callable[[Alert], None]] = []
    
    def add_rule(
        self,
        name: str,
        metric_name: str,
        threshold: float,
        operator: str = "gt",  # gt, lt, eq
        level: AlertLevel = AlertLevel.WARNING,
    ):
        """Agrega una regla de alerta."""
        self._rules.append({
            "name": name,
            "metric_name": metric_name,
            "threshold": threshold,
            "operator": operator,
            "level": level,
        })
    
    def add_handler(self, handler: Callable[[Alert], None]):
        """Agrega un handler de alertas."""
        self._handlers.append(handler)
    
    def check(self, metrics: dict) -> list[Alert]:
        """Evalúa reglas contra métricas actuales."""
        alerts = []
        
        for rule in self._rules:
            metric_name = rule["metric_name"]
            if metric_name not in metrics:
                continue
            
            value = metrics[metric_name]
            threshold = rule["threshold"]
            operator = rule["operator"]
            
            triggered = False
            if operator == "gt" and value > threshold:
                triggered = True
            elif operator == "lt" and value < threshold:
                triggered = True
            elif operator == "eq" and value == threshold:
                triggered = True
            
            if triggered:
                alert = Alert(
                    name=rule["name"],
                    level=rule["level"],
                    message=f"{metric_name} = {value} (threshold: {operator} {threshold})",
                    metric_value=value,
                    threshold=threshold,
                )
                alerts.append(alert)
                
                # Notificar handlers
                for handler in self._handlers:
                    handler(alert)
        
        return alerts


# Configurar alertas
alert_manager = AlertManager()
alert_manager.add_rule("high_error_rate", "error_rate", 0.05, "gt", AlertLevel.CRITICAL)
alert_manager.add_rule("high_latency", "latency_p95_ms", 500, "gt", AlertLevel.WARNING)
alert_manager.add_handler(lambda a: logger.warning(f"ALERT: {a.name} - {a.message}"))
```

---

## 🔧 Mini-Proyecto: Observabilidad Básica

### Objetivo

1. Agregar logging estructurado a la API
2. Implementar métricas de latencia
3. Crear detector de drift
4. Configurar alertas básicas

### Criterios de Éxito

- [ ] Logs en formato JSON
- [ ] Endpoint `/metrics` funcionando
- [ ] Drift detection implementado
- [ ] Alertas configuradas

---

## ✅ Validación

```bash
make check-10
```

---

## ➡️ Siguiente Módulo

**[11 — Mantenimiento & Auditoría](../11_mantenimiento_auditoria/index.md)**

---

*Última actualización: 2024-12*
