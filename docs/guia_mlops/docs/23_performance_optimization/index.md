---
title: "Performance y Optimización de Costos"
module: "23"
order: 1
tags:
  - "performance"
  - "optimization"
  - "cost"
  - "staff-level"
status: "ready"
---

# 23 — Performance y Optimización de Costos

> **Tiempo estimado**: 8 horas | **Nivel**: Staff/Principal
> 
> **Prerrequisitos**: Módulos 15-16 completados

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Realizar **benchmarking** de modelos e inferencia
2. ✅ Aplicar **cuantización** y optimizaciones
3. ✅ Configurar **batch inference** eficiente
4. ✅ Optimizar **costos de infraestructura** ML

---

## 📖 Contenido Teórico

### 1. Benchmarking de Inferencia

```python
"""benchmark.py — Benchmarking de modelos ML."""
import time
import numpy as np
import statistics
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class BenchmarkResult:
    """Resultado de benchmark."""
    
    model_name: str
    batch_size: int
    n_iterations: int
    
    # Latencias (ms)
    latency_mean: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    latency_std: float
    
    # Throughput
    throughput_rps: float  # requests per second
    
    # Memoria
    memory_mb: float
    
    def __str__(self):
        return f"""
Benchmark: {self.model_name}
  Batch size: {self.batch_size}
  Iterations: {self.n_iterations}
  
  Latency (ms):
    Mean: {self.latency_mean:.2f}
    P50:  {self.latency_p50:.2f}
    P95:  {self.latency_p95:.2f}
    P99:  {self.latency_p99:.2f}
    Std:  {self.latency_std:.2f}
  
  Throughput: {self.throughput_rps:.1f} req/s
  Memory: {self.memory_mb:.1f} MB
"""


class ModelBenchmarker:
    """Benchmarker para modelos ML."""
    
    def __init__(self, warmup_iterations: int = 10):
        self.warmup_iterations = warmup_iterations
    
    def benchmark(
        self,
        model: Any,
        X: np.ndarray,
        n_iterations: int = 100,
        batch_size: int = 1,
    ) -> BenchmarkResult:
        """Ejecuta benchmark de inferencia."""
        import tracemalloc
        
        # Preparar batches
        n_samples = len(X)
        batches = [
            X[i:i+batch_size] 
            for i in range(0, n_samples, batch_size)
        ]
        
        # Warmup
        for _ in range(self.warmup_iterations):
            model.predict(X[:batch_size])
        
        # Benchmark
        latencies = []
        tracemalloc.start()
        
        for _ in range(n_iterations):
            for batch in batches:
                start = time.perf_counter()
                model.predict(batch)
                end = time.perf_counter()
                latencies.append((end - start) * 1000)  # ms
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Calcular estadísticas
        latencies_sorted = sorted(latencies)
        n = len(latencies)
        
        return BenchmarkResult(
            model_name=type(model).__name__,
            batch_size=batch_size,
            n_iterations=n_iterations,
            latency_mean=statistics.mean(latencies),
            latency_p50=latencies_sorted[int(n * 0.50)],
            latency_p95=latencies_sorted[int(n * 0.95)],
            latency_p99=latencies_sorted[int(n * 0.99)],
            latency_std=statistics.stdev(latencies),
            throughput_rps=1000 / statistics.mean(latencies) * batch_size,
            memory_mb=peak / 1024 / 1024,
        )
    
    def compare_models(
        self,
        models: dict[str, Any],
        X: np.ndarray,
        batch_sizes: list[int] = [1, 8, 32, 64],
    ) -> dict:
        """Compara múltiples modelos."""
        results = {}
        
        for name, model in models.items():
            results[name] = {}
            for bs in batch_sizes:
                result = self.benchmark(model, X, batch_size=bs)
                results[name][f"batch_{bs}"] = result
        
        return results
```

---

### 2. Optimización de Modelos

```python
"""optimization.py — Técnicas de optimización."""
import numpy as np
from sklearn.base import BaseEstimator
import joblib


class ModelOptimizer:
    """Optimizador de modelos para producción."""
    
    @staticmethod
    def reduce_tree_depth(model, max_depth: int = 10):
        """Reduce profundidad de árboles (para RF/XGBoost)."""
        if hasattr(model, 'estimators_'):
            # Random Forest
            for tree in model.estimators_:
                # Truncar árbol (simplificado)
                pass
        return model
    
    @staticmethod
    def prune_features(model, X, importance_threshold: float = 0.01):
        """Elimina features de baja importancia."""
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            mask = importances >= importance_threshold
            
            # Retornar índices de features importantes
            return np.where(mask)[0]
        
        return np.arange(X.shape[1])
    
    @staticmethod
    def quantize_weights(model, bits: int = 8):
        """Cuantización básica de pesos (para modelos custom)."""
        # Para sklearn, cuantización limitada
        # Esto es más relevante para modelos deep learning
        
        if hasattr(model, 'coef_'):
            coef = model.coef_
            
            # Cuantizar a int8
            min_val = coef.min()
            max_val = coef.max()
            scale = (max_val - min_val) / (2**bits - 1)
            
            quantized = np.round((coef - min_val) / scale).astype(np.int8)
            
            return {
                'quantized_weights': quantized,
                'scale': scale,
                'min_val': min_val,
            }
        
        return None


class BatchInferenceOptimizer:
    """Optimizador de inferencia en batch."""
    
    def __init__(self, model, optimal_batch_size: int = 32):
        self.model = model
        self.optimal_batch_size = optimal_batch_size
        self._buffer = []
    
    def add_request(self, x: np.ndarray) -> None:
        """Agrega request al buffer."""
        self._buffer.append(x)
    
    def flush(self) -> np.ndarray:
        """Procesa todo el buffer."""
        if not self._buffer:
            return np.array([])
        
        X = np.vstack(self._buffer)
        predictions = self.model.predict(X)
        self._buffer = []
        return predictions
    
    def predict_batched(self, X: np.ndarray) -> np.ndarray:
        """Predicción con batching óptimo."""
        n_samples = len(X)
        predictions = []
        
        for i in range(0, n_samples, self.optimal_batch_size):
            batch = X[i:i+self.optimal_batch_size]
            preds = self.model.predict(batch)
            predictions.extend(preds)
        
        return np.array(predictions)
```

---

### 3. Optimización de Costos

```python
"""cost_optimization.py — Estrategias de reducción de costos."""
from dataclasses import dataclass
from enum import Enum


class InfrastructureTier(Enum):
    """Niveles de infraestructura."""
    SERVERLESS = "serverless"      # Lambda, Cloud Functions
    CONTAINER = "container"        # ECS, Cloud Run
    KUBERNETES = "kubernetes"      # EKS, GKE
    DEDICATED = "dedicated"        # EC2, Compute Engine


@dataclass
class CostEstimate:
    """Estimación de costos."""
    
    tier: InfrastructureTier
    monthly_requests: int
    avg_latency_ms: float
    
    # Costos
    compute_cost: float
    storage_cost: float
    network_cost: float
    
    @property
    def total_cost(self) -> float:
        return self.compute_cost + self.storage_cost + self.network_cost
    
    @property
    def cost_per_1k_requests(self) -> float:
        if self.monthly_requests == 0:
            return 0
        return (self.total_cost / self.monthly_requests) * 1000


class CostOptimizer:
    """Optimizador de costos de infraestructura ML."""
    
    # Precios aproximados (USD)
    PRICING = {
        InfrastructureTier.SERVERLESS: {
            "per_request": 0.0000002,  # $0.20 por millón
            "per_gb_second": 0.0000166667,
            "storage_gb": 0.023,
        },
        InfrastructureTier.CONTAINER: {
            "per_vcpu_hour": 0.04,
            "per_gb_hour": 0.004,
            "storage_gb": 0.10,
        },
        InfrastructureTier.KUBERNETES: {
            "per_vcpu_hour": 0.05,
            "per_gb_hour": 0.005,
            "management_fee": 72,  # por cluster/mes
            "storage_gb": 0.10,
        },
    }
    
    def estimate_serverless(
        self,
        monthly_requests: int,
        avg_duration_ms: int,
        memory_mb: int = 256,
    ) -> CostEstimate:
        """Estima costos de serverless (Lambda/Cloud Functions)."""
        pricing = self.PRICING[InfrastructureTier.SERVERLESS]
        
        # Compute: requests + duration
        request_cost = monthly_requests * pricing["per_request"]
        gb_seconds = (monthly_requests * (avg_duration_ms / 1000) * 
                     (memory_mb / 1024))
        compute_cost = request_cost + (gb_seconds * pricing["per_gb_second"])
        
        return CostEstimate(
            tier=InfrastructureTier.SERVERLESS,
            monthly_requests=monthly_requests,
            avg_latency_ms=avg_duration_ms,
            compute_cost=compute_cost,
            storage_cost=0,
            network_cost=monthly_requests * 0.000001,  # ~$1 per million
        )
    
    def estimate_container(
        self,
        monthly_requests: int,
        avg_duration_ms: int,
        instances: int = 2,
        vcpus: int = 1,
        memory_gb: int = 2,
    ) -> CostEstimate:
        """Estima costos de containers (ECS/Cloud Run)."""
        pricing = self.PRICING[InfrastructureTier.CONTAINER]
        
        hours_per_month = 730
        compute_cost = (
            instances * vcpus * hours_per_month * pricing["per_vcpu_hour"] +
            instances * memory_gb * hours_per_month * pricing["per_gb_hour"]
        )
        
        return CostEstimate(
            tier=InfrastructureTier.CONTAINER,
            monthly_requests=monthly_requests,
            avg_latency_ms=avg_duration_ms,
            compute_cost=compute_cost,
            storage_cost=20 * pricing["storage_gb"],
            network_cost=monthly_requests * 0.000001,
        )
    
    def recommend_tier(
        self,
        monthly_requests: int,
        latency_requirement_ms: int,
        budget_max: float,
    ) -> InfrastructureTier:
        """Recomienda tier basado en requisitos."""
        
        # Serverless: mejor para tráfico bajo/variable, latencia flexible
        if monthly_requests < 1_000_000 and latency_requirement_ms > 100:
            return InfrastructureTier.SERVERLESS
        
        # Containers: balance entre costo y latencia
        if monthly_requests < 10_000_000:
            return InfrastructureTier.CONTAINER
        
        # Kubernetes: alto tráfico, requisitos estrictos
        return InfrastructureTier.KUBERNETES
```

---

### 4. Checklist de Optimización

```markdown
## Checklist de Performance

### Pre-producción
- [ ] Benchmark latencia P50, P95, P99
- [ ] Verificar uso de memoria
- [ ] Probar diferentes batch sizes
- [ ] Eliminar features no importantes (<1%)

### Modelo
- [ ] Reducir complejidad si latencia > requisito
- [ ] Considerar modelo más simple (Logistic vs RF)
- [ ] Feature selection basada en importancia
- [ ] Evaluar trade-off accuracy vs latency

### Infraestructura
- [ ] Elegir tier apropiado al volumen
- [ ] Configurar autoscaling
- [ ] Implementar caching donde aplique
- [ ] Monitorear costos semanalmente

### Inferencia
- [ ] Usar batch inference cuando sea posible
- [ ] Implementar timeout apropiado
- [ ] Cachear predicciones repetidas
- [ ] Async para requests no críticos
```

---

## 🔧 Mini-Proyecto: Optimization Suite

### Objetivo

1. Benchmark de tu modelo con diferentes batch sizes
2. Identificar oportunidades de optimización
3. Estimar costos de diferentes infraestructuras
4. Documentar recomendaciones

### Criterios de Éxito

- [ ] Reporte de benchmark generado
- [ ] Latencia P95 < 100ms para batch=1
- [ ] Estimación de costos para 3 tiers
- [ ] Recomendación documentada

---

## ✅ Validación

```bash
make check-23
```

---

## ➡️ Siguiente Módulo

**[24 — Model Risk Management](../24_model_risk_management/index.md)**

---

*Última actualización: 2024-12*
