---
title: "Seguridad y Testing Adversarial para ML"
module: "21"
order: 1
tags:
  - "security"
  - "adversarial"
  - "testing"
  - "staff-level"
status: "ready"
---

# 21 — Seguridad y Testing Adversarial para ML

> **Tiempo estimado**: 8 horas | **Nivel**: Staff/Principal
> 
> **Prerrequisitos**: Módulos 19-20 completados

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Identificar **vectores de ataque** en sistemas ML
2. ✅ Implementar **tests adversariales** básicos
3. ✅ Detectar **data poisoning** en entrenamiento
4. ✅ Proteger **APIs de inferencia** contra ataques

---

## 📖 Contenido Teórico

### 1. Amenazas en ML Systems

```
┌─────────────────────────────────────────────────────────────┐
│                    SUPERFICIE DE ATAQUE ML                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TRAINING TIME                      INFERENCE TIME          │
│  ─────────────                      ──────────────          │
│  • Data Poisoning                   • Adversarial Examples  │
│  • Label Flipping                   • Model Extraction      │
│  • Backdoor Attacks                 • Membership Inference  │
│  • Model Manipulation               • Input Manipulation    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. Testing Adversarial para Clasificadores

```python
"""adversarial.py — Tests adversariales básicos."""
import numpy as np
import pandas as pd
from typing import Callable, Any
from dataclasses import dataclass


@dataclass
class AdversarialResult:
    """Resultado de un test adversarial."""
    test_name: str
    passed: bool
    original_prediction: Any
    adversarial_prediction: Any
    perturbation_magnitude: float
    details: str


class AdversarialTester:
    """Tester de robustez adversarial para modelos ML."""
    
    def __init__(self, model, feature_names: list[str]):
        self.model = model
        self.feature_names = feature_names
    
    def fgsm_attack(
        self,
        X: np.ndarray,
        y_true: np.ndarray,
        epsilon: float = 0.1,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Fast Gradient Sign Method (aproximado para modelos no diferenciables).
        
        Para sklearn, usamos perturbación basada en gradiente numérico.
        """
        X_adv = X.copy()
        
        # Calcular "gradiente" numérico aproximado
        for i in range(X.shape[1]):
            delta = np.zeros_like(X)
            delta[:, i] = epsilon
            
            pred_plus = self.model.predict_proba(X + delta)[:, 1]
            pred_minus = self.model.predict_proba(X - delta)[:, 1]
            
            # Dirección que maximiza la pérdida (flip prediction)
            gradient = pred_plus - pred_minus
            
            # Aplicar perturbación en dirección del gradiente
            X_adv[:, i] += epsilon * np.sign(gradient)
        
        y_adv = self.model.predict(X_adv)
        return X_adv, y_adv
    
    def test_feature_perturbation(
        self,
        X: np.ndarray,
        feature_idx: int,
        perturbation_range: tuple[float, float] = (-0.5, 0.5),
        n_steps: int = 10,
    ) -> list[AdversarialResult]:
        """Testa sensibilidad a perturbaciones en una feature."""
        results = []
        original_pred = self.model.predict(X)
        original_proba = self.model.predict_proba(X)[:, 1]
        
        for step in np.linspace(perturbation_range[0], perturbation_range[1], n_steps):
            X_perturbed = X.copy()
            X_perturbed[:, feature_idx] += step
            
            new_pred = self.model.predict(X_perturbed)
            new_proba = self.model.predict_proba(X_perturbed)[:, 1]
            
            # Detectar cambios de predicción
            flipped = (original_pred != new_pred).sum()
            
            results.append(AdversarialResult(
                test_name=f"perturbation_{self.feature_names[feature_idx]}",
                passed=flipped == 0,
                original_prediction=original_proba.mean(),
                adversarial_prediction=new_proba.mean(),
                perturbation_magnitude=abs(step),
                details=f"{flipped}/{len(X)} predictions flipped",
            ))
        
        return results
    
    def test_boundary_inputs(
        self,
        X: np.ndarray,
        bounds: dict[str, tuple[float, float]],
    ) -> list[AdversarialResult]:
        """Testa inputs en los límites del dominio."""
        results = []
        
        for feature, (min_val, max_val) in bounds.items():
            if feature not in self.feature_names:
                continue
            
            idx = self.feature_names.index(feature)
            
            # Test con valor mínimo extremo
            X_min = X.copy()
            X_min[:, idx] = min_val
            
            try:
                pred_min = self.model.predict(X_min)
                results.append(AdversarialResult(
                    test_name=f"boundary_min_{feature}",
                    passed=True,
                    original_prediction=None,
                    adversarial_prediction=pred_min.mean(),
                    perturbation_magnitude=0,
                    details=f"Model handled min value {min_val}",
                ))
            except Exception as e:
                results.append(AdversarialResult(
                    test_name=f"boundary_min_{feature}",
                    passed=False,
                    original_prediction=None,
                    adversarial_prediction=None,
                    perturbation_magnitude=0,
                    details=f"Error: {e}",
                ))
            
            # Test con valor máximo extremo
            X_max = X.copy()
            X_max[:, idx] = max_val
            
            try:
                pred_max = self.model.predict(X_max)
                results.append(AdversarialResult(
                    test_name=f"boundary_max_{feature}",
                    passed=True,
                    original_prediction=None,
                    adversarial_prediction=pred_max.mean(),
                    perturbation_magnitude=0,
                    details=f"Model handled max value {max_val}",
                ))
            except Exception as e:
                results.append(AdversarialResult(
                    test_name=f"boundary_max_{feature}",
                    passed=False,
                    original_prediction=None,
                    adversarial_prediction=None,
                    perturbation_magnitude=0,
                    details=f"Error: {e}",
                ))
        
        return results
```

---

### 3. Detección de Data Poisoning

```python
"""poisoning.py — Detección de data poisoning."""
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from typing import Tuple


class PoisoningDetector:
    """Detector de data poisoning en datasets de entrenamiento."""
    
    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
        )
        self.lof = LocalOutlierFactor(
            n_neighbors=20,
            contamination=contamination,
        )
    
    def detect_outliers(
        self,
        X: np.ndarray,
        method: str = "isolation_forest",
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Detecta outliers que podrían ser datos envenenados.
        
        Returns:
            - mask: booleano, True = sospechoso
            - scores: puntuación de anomalía
        """
        if method == "isolation_forest":
            predictions = self.isolation_forest.fit_predict(X)
            scores = self.isolation_forest.score_samples(X)
        elif method == "lof":
            predictions = self.lof.fit_predict(X)
            scores = self.lof.negative_outlier_factor_
        else:
            raise ValueError(f"Método no soportado: {method}")
        
        # -1 = anomalía, 1 = normal
        mask = predictions == -1
        return mask, scores
    
    def detect_label_flipping(
        self,
        X: np.ndarray,
        y: np.ndarray,
        threshold: float = 0.1,
    ) -> np.ndarray:
        """Detecta posibles labels flippeados.
        
        Busca samples donde el label es inconsistente con vecinos cercanos.
        """
        from sklearn.neighbors import NearestNeighbors
        
        nn = NearestNeighbors(n_neighbors=10)
        nn.fit(X)
        
        suspicious = []
        
        for i in range(len(X)):
            # Encontrar vecinos
            distances, indices = nn.kneighbors([X[i]])
            neighbor_labels = y[indices[0][1:]]  # Excluir el propio sample
            
            # Calcular consenso de vecinos
            neighbor_consensus = neighbor_labels.mean()
            
            # Si el label es muy diferente al consenso, es sospechoso
            if abs(y[i] - neighbor_consensus) > threshold:
                suspicious.append(i)
        
        return np.array(suspicious)
    
    def statistical_tests(
        self,
        X_train: np.ndarray,
        X_reference: np.ndarray,
    ) -> dict:
        """Tests estadísticos para detectar distribución envenenada."""
        from scipy import stats
        
        results = {}
        
        for col in range(X_train.shape[1]):
            # Test Kolmogorov-Smirnov
            ks_stat, p_value = stats.ks_2samp(
                X_train[:, col],
                X_reference[:, col]
            )
            
            results[f"feature_{col}"] = {
                "ks_statistic": float(ks_stat),
                "p_value": float(p_value),
                "suspicious": p_value < 0.01,
            }
        
        return results
```

---

### 4. Seguridad de API de Inferencia

```python
"""api_security.py — Seguridad para APIs de inferencia."""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, field_validator
import hashlib
import time
from collections import defaultdict
from typing import Optional


# Rate limiting simple
request_counts = defaultdict(list)
RATE_LIMIT = 100  # requests por minuto


def rate_limiter(request: Request):
    """Rate limiting básico."""
    client_ip = request.client.host
    current_time = time.time()
    
    # Limpiar requests antiguos (> 1 minuto)
    request_counts[client_ip] = [
        t for t in request_counts[client_ip]
        if current_time - t < 60
    ]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(429, "Rate limit exceeded")
    
    request_counts[client_ip].append(current_time)


class SecureInput(BaseModel):
    """Input con validaciones de seguridad."""
    
    age: int = Field(..., ge=0, le=150)
    balance: float = Field(..., ge=-1e6, le=1e9)
    tenure: int = Field(..., ge=0, le=100)
    
    @field_validator("balance")
    @classmethod
    def check_balance(cls, v):
        # Detectar valores sospechosos
        if v == float('inf') or v == float('-inf'):
            raise ValueError("Valores infinitos no permitidos")
        return v
    
    def is_suspicious(self) -> bool:
        """Detecta inputs potencialmente maliciosos."""
        # Combinaciones inusuales
        if self.age < 18 and self.balance > 100000:
            return True
        if self.tenure > self.age:
            return True
        return False


class InputSanitizer:
    """Sanitiza inputs para prevenir ataques."""
    
    @staticmethod
    def clip_to_bounds(value: float, min_val: float, max_val: float) -> float:
        """Clip valores a límites razonables."""
        return max(min_val, min(max_val, value))
    
    @staticmethod
    def detect_injection(text: str) -> bool:
        """Detecta posibles inyecciones en strings."""
        suspicious_patterns = [
            "SELECT", "DROP", "INSERT", "DELETE",
            "<script>", "javascript:",
            "../", "..\\",
        ]
        text_upper = text.upper()
        return any(p.upper() in text_upper for p in suspicious_patterns)
    
    @staticmethod
    def hash_sensitive(value: str) -> str:
        """Hashea datos sensibles para logging."""
        return hashlib.sha256(value.encode()).hexdigest()[:16]


# Uso en API
app = FastAPI()

@app.post("/predict", dependencies=[Depends(rate_limiter)])
async def predict(input_data: SecureInput):
    """Endpoint de predicción con seguridad."""
    
    # Verificar inputs sospechosos
    if input_data.is_suspicious():
        # Log para análisis pero no rechazar
        print(f"SUSPICIOUS INPUT: {input_data}")
    
    # Procesar predicción...
    return {"prediction": 0.5}
```

---

## 🔧 Mini-Proyecto: Security Testing Suite

### Objetivo

1. Implementar tests adversariales para tu modelo
2. Crear detector de data poisoning
3. Agregar seguridad a la API
4. Documentar vulnerabilidades encontradas

### Criterios de Éxito

- [ ] Tests adversariales ejecutándose
- [ ] API con rate limiting y validación
- [ ] Reporte de vulnerabilidades
- [ ] Mitigaciones implementadas

---

## ✅ Validación

```bash
make check-21
```

---

## ➡️ Siguiente Módulo

**[22 — Observabilidad y Monitoring](../22_observabilidad/index.md)**

---

*Última actualización: 2024-12*
