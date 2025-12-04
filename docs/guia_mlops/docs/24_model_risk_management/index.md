---
title: "Model Risk Management"
module: "24"
order: 1
tags:
  - "risk"
  - "fairness"
  - "governance"
  - "staff-level"
status: "ready"
---

# 24 — Model Risk Management

> **Tiempo estimado**: 8 horas | **Nivel**: Staff/Principal
> 
> **Prerrequisitos**: Módulos 22-23 completados

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Realizar **análisis de riesgo** de modelos ML
2. ✅ Evaluar **fairness** y detectar sesgos
3. ✅ Establecer **políticas de retención** de modelos
4. ✅ Implementar **governance** de modelos en producción

---

## 📖 Contenido Teórico

### 1. Framework de Riesgo ML

```
┌─────────────────────────────────────────────────────────────┐
│                   RISK ASSESSMENT MATRIX                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   IMPACTO                                                   │
│      ▲                                                      │
│  Alto│  MEDIUM    HIGH      CRITICAL                        │
│      │  (Monitor) (Mitigate) (Block)                        │
│ Medio│  LOW       MEDIUM     HIGH                           │
│      │  (Accept)  (Monitor)  (Mitigate)                     │
│  Bajo│  TRIVIAL   LOW        MEDIUM                         │
│      │  (Accept)  (Accept)   (Monitor)                      │
│      └──────────────────────────────────────▶               │
│           Baja      Media      Alta                         │
│                  PROBABILIDAD                               │
└─────────────────────────────────────────────────────────────┘
```

```python
"""risk_assessment.py — Framework de evaluación de riesgo."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
from datetime import datetime


class RiskLevel(Enum):
    """Niveles de riesgo."""
    TRIVIAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class RiskCategory(Enum):
    """Categorías de riesgo ML."""
    ACCURACY = "accuracy"           # Degradación de performance
    FAIRNESS = "fairness"           # Sesgos en predicciones
    PRIVACY = "privacy"             # Exposición de datos
    SECURITY = "security"           # Vulnerabilidades
    OPERATIONAL = "operational"     # Fallos en producción
    REGULATORY = "regulatory"       # Incumplimiento normativo


@dataclass
class RiskItem:
    """Item de riesgo identificado."""
    
    id: str
    category: RiskCategory
    description: str
    probability: int  # 1-5
    impact: int       # 1-5
    mitigation: str
    owner: str
    status: str = "open"  # open, mitigating, resolved
    
    @property
    def risk_score(self) -> int:
        """Calcula score de riesgo (1-25)."""
        return self.probability * self.impact
    
    @property
    def risk_level(self) -> RiskLevel:
        """Determina nivel de riesgo."""
        score = self.risk_score
        if score <= 4:
            return RiskLevel.TRIVIAL
        elif score <= 8:
            return RiskLevel.LOW
        elif score <= 12:
            return RiskLevel.MEDIUM
        elif score <= 16:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL


class ModelRiskAssessment:
    """Evaluación de riesgo para un modelo ML."""
    
    def __init__(self, model_name: str, model_version: str):
        self.model_name = model_name
        self.model_version = model_version
        self.risks: List[RiskItem] = []
        self.assessment_date = datetime.now()
    
    def add_risk(self, risk: RiskItem) -> None:
        """Agrega un riesgo identificado."""
        self.risks.append(risk)
    
    def get_critical_risks(self) -> List[RiskItem]:
        """Retorna riesgos críticos y altos."""
        return [r for r in self.risks 
                if r.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
    
    def get_summary(self) -> dict:
        """Genera resumen del assessment."""
        by_level = {}
        for level in RiskLevel:
            by_level[level.name] = len([r for r in self.risks if r.risk_level == level])
        
        return {
            "model": self.model_name,
            "version": self.model_version,
            "date": self.assessment_date.isoformat(),
            "total_risks": len(self.risks),
            "by_level": by_level,
            "requires_action": len(self.get_critical_risks()) > 0,
        }
    
    def can_deploy(self) -> tuple[bool, str]:
        """Verifica si el modelo puede desplegarse."""
        critical = [r for r in self.risks if r.risk_level == RiskLevel.CRITICAL]
        
        if critical:
            return False, f"Bloqueado por {len(critical)} riesgo(s) crítico(s)"
        
        high = [r for r in self.risks if r.risk_level == RiskLevel.HIGH]
        if len(high) > 2:
            return False, f"Demasiados riesgos altos ({len(high)})"
        
        return True, "Aprobado para despliegue con monitoreo"


# Ejemplo de uso
assessment = ModelRiskAssessment("churn_predictor", "1.0.0")

assessment.add_risk(RiskItem(
    id="R001",
    category=RiskCategory.FAIRNESS,
    description="Menor recall en clientes < 25 años",
    probability=4,
    impact=3,
    mitigation="Agregar balanceo por edad en entrenamiento",
    owner="ml-team",
))

assessment.add_risk(RiskItem(
    id="R002",
    category=RiskCategory.ACCURACY,
    description="Posible degradación por drift estacional",
    probability=3,
    impact=4,
    mitigation="Implementar monitoreo de drift semanal",
    owner="ml-ops",
))
```

---

### 2. Evaluación de Fairness

```python
"""fairness.py — Métricas de fairness para ML."""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class FairnessMetrics:
    """Métricas de fairness por grupo."""
    
    group_name: str
    total_samples: int
    positive_rate: float        # P(y_pred=1)
    true_positive_rate: float   # Recall
    false_positive_rate: float
    precision: float
    
    def to_dict(self) -> dict:
        return {
            "group": self.group_name,
            "samples": self.total_samples,
            "positive_rate": round(self.positive_rate, 4),
            "tpr": round(self.true_positive_rate, 4),
            "fpr": round(self.false_positive_rate, 4),
            "precision": round(self.precision, 4),
        }


class FairnessEvaluator:
    """Evaluador de fairness para modelos de clasificación."""
    
    def __init__(self, y_true: np.ndarray, y_pred: np.ndarray, y_proba: np.ndarray = None):
        self.y_true = y_true
        self.y_pred = y_pred
        self.y_proba = y_proba
    
    def compute_group_metrics(
        self,
        sensitive_attr: np.ndarray,
    ) -> Dict[str, FairnessMetrics]:
        """Calcula métricas por grupo sensible."""
        groups = np.unique(sensitive_attr)
        metrics = {}
        
        for group in groups:
            mask = sensitive_attr == group
            y_true_g = self.y_true[mask]
            y_pred_g = self.y_pred[mask]
            
            # Métricas básicas
            tp = ((y_true_g == 1) & (y_pred_g == 1)).sum()
            fp = ((y_true_g == 0) & (y_pred_g == 1)).sum()
            tn = ((y_true_g == 0) & (y_pred_g == 0)).sum()
            fn = ((y_true_g == 1) & (y_pred_g == 0)).sum()
            
            metrics[str(group)] = FairnessMetrics(
                group_name=str(group),
                total_samples=len(y_true_g),
                positive_rate=y_pred_g.mean(),
                true_positive_rate=tp / (tp + fn) if (tp + fn) > 0 else 0,
                false_positive_rate=fp / (fp + tn) if (fp + tn) > 0 else 0,
                precision=tp / (tp + fp) if (tp + fp) > 0 else 0,
            )
        
        return metrics
    
    def demographic_parity(
        self,
        sensitive_attr: np.ndarray,
    ) -> Tuple[float, bool]:
        """Calcula paridad demográfica.
        
        Mide si la tasa de predicciones positivas es igual entre grupos.
        Ratio aceptable: 0.8 - 1.25 (regla del 80%)
        """
        metrics = self.compute_group_metrics(sensitive_attr)
        
        rates = [m.positive_rate for m in metrics.values()]
        min_rate = min(rates)
        max_rate = max(rates)
        
        ratio = min_rate / max_rate if max_rate > 0 else 0
        passes = 0.8 <= ratio <= 1.25
        
        return ratio, passes
    
    def equalized_odds(
        self,
        sensitive_attr: np.ndarray,
    ) -> Dict[str, Tuple[float, bool]]:
        """Calcula igualdad de oportunidades.
        
        Mide si TPR y FPR son iguales entre grupos.
        """
        metrics = self.compute_group_metrics(sensitive_attr)
        
        tprs = [m.true_positive_rate for m in metrics.values()]
        fprs = [m.false_positive_rate for m in metrics.values()]
        
        tpr_ratio = min(tprs) / max(tprs) if max(tprs) > 0 else 0
        fpr_ratio = min(fprs) / max(fprs) if max(fprs) > 0 else 0
        
        return {
            "tpr_ratio": (tpr_ratio, 0.8 <= tpr_ratio <= 1.25),
            "fpr_ratio": (fpr_ratio, 0.8 <= fpr_ratio <= 1.25),
        }
    
    def generate_report(
        self,
        sensitive_attrs: Dict[str, np.ndarray],
    ) -> dict:
        """Genera reporte completo de fairness."""
        report = {
            "summary": {},
            "by_attribute": {},
        }
        
        all_pass = True
        
        for attr_name, attr_values in sensitive_attrs.items():
            metrics = self.compute_group_metrics(attr_values)
            dp_ratio, dp_pass = self.demographic_parity(attr_values)
            eq_odds = self.equalized_odds(attr_values)
            
            attr_pass = dp_pass and eq_odds["tpr_ratio"][1]
            all_pass = all_pass and attr_pass
            
            report["by_attribute"][attr_name] = {
                "group_metrics": {k: v.to_dict() for k, v in metrics.items()},
                "demographic_parity": {"ratio": dp_ratio, "pass": dp_pass},
                "equalized_odds": eq_odds,
                "overall_pass": attr_pass,
            }
        
        report["summary"]["all_pass"] = all_pass
        report["summary"]["recommendation"] = (
            "Modelo cumple criterios de fairness" if all_pass
            else "Revisar sesgos antes de producción"
        )
        
        return report
```

---

### 3. Políticas de Retención

```python
"""retention.py — Políticas de retención de modelos."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum


class RetentionAction(Enum):
    """Acciones de retención."""
    KEEP = "keep"
    ARCHIVE = "archive"
    DELETE = "delete"


@dataclass
class ModelVersion:
    """Versión de modelo con metadata."""
    
    name: str
    version: str
    stage: str  # staging, production, archived
    created_at: datetime
    last_used: Optional[datetime]
    metrics: dict
    risk_assessment: Optional[dict]
    
    def days_since_created(self) -> int:
        return (datetime.now() - self.created_at).days
    
    def days_since_used(self) -> int:
        if not self.last_used:
            return self.days_since_created()
        return (datetime.now() - self.last_used).days


class RetentionPolicy:
    """Política de retención de modelos."""
    
    def __init__(
        self,
        max_versions_in_production: int = 2,
        max_versions_in_staging: int = 5,
        archive_after_days_unused: int = 90,
        delete_archived_after_days: int = 365,
        keep_minimum_versions: int = 3,
    ):
        self.max_prod = max_versions_in_production
        self.max_staging = max_versions_in_staging
        self.archive_days = archive_after_days_unused
        self.delete_days = delete_archived_after_days
        self.min_versions = keep_minimum_versions
    
    def evaluate(self, versions: List[ModelVersion]) -> List[tuple]:
        """Evalúa qué acción tomar para cada versión.
        
        Returns:
            Lista de (ModelVersion, RetentionAction, razón)
        """
        actions = []
        
        # Separar por stage
        prod = [v for v in versions if v.stage == "production"]
        staging = [v for v in versions if v.stage == "staging"]
        archived = [v for v in versions if v.stage == "archived"]
        
        # Regla 1: Mantener versiones en producción (máximo N)
        prod_sorted = sorted(prod, key=lambda v: v.created_at, reverse=True)
        for i, v in enumerate(prod_sorted):
            if i < self.max_prod:
                actions.append((v, RetentionAction.KEEP, "En producción activa"))
            else:
                actions.append((v, RetentionAction.ARCHIVE, "Excede máximo en producción"))
        
        # Regla 2: Archivar staging no usado
        for v in staging:
            if v.days_since_used() > self.archive_days:
                actions.append((v, RetentionAction.ARCHIVE, f"Sin uso por {v.days_since_used()} días"))
            elif len(staging) > self.max_staging:
                oldest = sorted(staging, key=lambda x: x.created_at)
                if v == oldest[0]:
                    actions.append((v, RetentionAction.ARCHIVE, "Excede máximo en staging"))
                else:
                    actions.append((v, RetentionAction.KEEP, "En staging"))
            else:
                actions.append((v, RetentionAction.KEEP, "En staging"))
        
        # Regla 3: Eliminar archivados antiguos
        for v in archived:
            if v.days_since_created() > self.delete_days:
                actions.append((v, RetentionAction.DELETE, f"Archivado por {v.days_since_created()} días"))
            else:
                actions.append((v, RetentionAction.KEEP, "Archivado reciente"))
        
        # Regla 4: Siempre mantener mínimo de versiones
        keeps = [a for a in actions if a[1] == RetentionAction.KEEP]
        if len(keeps) < self.min_versions:
            # Convertir DELETE a ARCHIVE hasta tener mínimo
            for i, (v, action, reason) in enumerate(actions):
                if action == RetentionAction.DELETE and len(keeps) < self.min_versions:
                    actions[i] = (v, RetentionAction.ARCHIVE, "Mantener versión mínima")
                    keeps.append(actions[i])
        
        return actions
```

---

## 🔧 Mini-Proyecto: Risk Assessment

### Objetivo

1. Evaluar riesgo de tu modelo
2. Calcular métricas de fairness
3. Definir políticas de retención
4. Documentar en Model Card

### Criterios de Éxito

- [ ] Risk Assessment completado
- [ ] Fairness report generado
- [ ] Política de retención definida
- [ ] Model Card actualizado con riesgos

---

## ✅ Validación

```bash
make check-24
```

---

## ➡️ Siguiente Módulo

**[25 — Mantenimiento y Runbooks](../25_mantenimiento_runbooks/index.md)**

---

*Última actualización: 2024-12*
