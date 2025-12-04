# 11 — Mantenimiento & Auditoría

> **Tiempo estimado**: 2 días (16 horas)
> 
> **Prerrequisitos**: Módulos 01-10 completados

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Crear **playbooks de mantenimiento**
2. ✅ Implementar **tests de regresión**
3. ✅ Gestionar **actualización de dependencias**
4. ✅ Establecer **calendario de revisiones**

---

## 📖 Contenido Teórico

### 1. Playbook de Mantenimiento

```markdown
# Playbook de Mantenimiento — ML System

## Tareas Rutinarias

### Diarias
- [ ] Revisar logs de errores
- [ ] Verificar métricas de latencia
- [ ] Confirmar que health checks pasan

### Semanales
- [ ] Revisar drift reports
- [ ] Analizar distribución de predicciones
- [ ] Backup de MLflow artifacts

### Mensuales
- [ ] Evaluar modelo contra datos recientes
- [ ] Revisar y actualizar dependencias
- [ ] Regenerar lockfiles

### Trimestrales
- [ ] Reentrenar modelo si degradación > 5%
- [ ] Auditoría de sesgos
- [ ] Actualizar Model Card

---

## Runbooks

### Runbook: Degradación de Métricas

**Síntoma**: AUC/F1 cae más de 5% respecto a baseline

**Pasos**:
1. Verificar datos de entrada (drift detection)
2. Comparar distribución de features vs training
3. Si hay drift significativo → reentrenar
4. Si no hay drift → investigar cambios en upstream

### Runbook: Alta Latencia

**Síntoma**: p95 latency > 500ms

**Pasos**:
1. Verificar CPU/Memory del pod
2. Revisar tamaño de batch de requests
3. Verificar si hay queries lentas al modelo
4. Escalar horizontalmente si necesario

### Runbook: Rollback de Modelo

**Síntoma**: Nuevo modelo con problemas en producción

**Pasos**:
1. Identificar versión anterior estable
2. `mlflow models update-stage --model-name X --version Y --stage Production`
3. Restart de pods de inferencia
4. Verificar métricas post-rollback
5. Documentar incidente
```

---

### 2. Tests de Regresión

```python
"""tests/regression/test_model_regression.py — Tests de regresión."""
import pytest
import json
import numpy as np
import pandas as pd
from pathlib import Path


class TestModelRegression:
    """Tests de regresión del modelo."""
    
    @pytest.fixture
    def baseline_metrics(self) -> dict:
        """Métricas baseline guardadas."""
        baseline_path = Path("tests/regression/baseline_metrics.json")
        with open(baseline_path) as f:
            return json.load(f)
    
    @pytest.fixture
    def current_metrics(self, trained_pipeline, test_data) -> dict:
        """Métricas actuales."""
        from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
        
        X_test = test_data.drop("churn", axis=1)
        y_test = test_data["churn"]
        
        y_pred = trained_pipeline.predict(X_test)
        y_proba = trained_pipeline.predict_proba(X_test)[:, 1]
        
        return {
            "accuracy": accuracy_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_proba),
            "f1": f1_score(y_test, y_pred),
        }
    
    def test_accuracy_not_degraded(self, baseline_metrics, current_metrics):
        """Accuracy no debe degradarse más de 5%."""
        degradation = baseline_metrics["accuracy"] - current_metrics["accuracy"]
        assert degradation < 0.05, f"Degradación de accuracy: {degradation:.2%}"
    
    def test_auc_not_degraded(self, baseline_metrics, current_metrics):
        """AUC no debe degradarse más de 5%."""
        degradation = baseline_metrics["roc_auc"] - current_metrics["roc_auc"]
        assert degradation < 0.05, f"Degradación de AUC: {degradation:.2%}"
    
    def test_f1_not_degraded(self, baseline_metrics, current_metrics):
        """F1 no debe degradarse más de 5%."""
        degradation = baseline_metrics["f1"] - current_metrics["f1"]
        assert degradation < 0.05, f"Degradación de F1: {degradation:.2%}"
    
    def test_prediction_distribution(self, trained_pipeline, test_data):
        """Distribución de predicciones debe ser razonable."""
        X_test = test_data.drop("churn", axis=1)
        y_proba = trained_pipeline.predict_proba(X_test)[:, 1]
        
        # No debe predecir todo 0 o todo 1
        assert 0.05 < np.mean(y_proba > 0.5) < 0.95
```

---

### 3. Gestión de Dependencias

```bash
# Verificar dependencias desactualizadas
pip list --outdated

# Actualizar de forma segura
pip install --upgrade package==X.Y.Z

# Regenerar lockfile
pip freeze > requirements.lock

# Auditar vulnerabilidades
pip-audit
safety check
```

#### Script de Actualización

```python
"""scripts/update_deps.py — Actualización de dependencias."""
import subprocess
import json
from datetime import datetime


def check_outdated() -> list[dict]:
    """Lista dependencias desactualizadas."""
    result = subprocess.run(
        ["pip", "list", "--outdated", "--format=json"],
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def update_package(name: str, version: str) -> bool:
    """Actualiza un paquete específico."""
    result = subprocess.run(
        ["pip", "install", f"{name}=={version}"],
        capture_output=True,
    )
    return result.returncode == 0


def run_tests() -> bool:
    """Ejecuta tests."""
    result = subprocess.run(
        ["pytest", "tests/", "-q"],
        capture_output=True,
    )
    return result.returncode == 0


def main():
    outdated = check_outdated()
    print(f"Encontradas {len(outdated)} dependencias desactualizadas")
    
    for pkg in outdated:
        name = pkg["name"]
        current = pkg["version"]
        latest = pkg["latest_version"]
        
        print(f"\n{name}: {current} → {latest}")
        
        # Actualizar
        if update_package(name, latest):
            # Verificar que tests pasan
            if run_tests():
                print(f"  ✅ Actualizado exitosamente")
            else:
                print(f"  ❌ Tests fallaron, revertiendo...")
                update_package(name, current)
        else:
            print(f"  ❌ Error al actualizar")


if __name__ == "__main__":
    main()
```

---

### 4. Calendario de Revisiones

```markdown
# Calendario de Mantenimiento ML

## Revisiones Automáticas (CI/CD)
- Tests unitarios: En cada PR
- Coverage check: En cada PR
- Security scan: Diario
- Dependency audit: Semanal

## Revisiones Manuales

### Mensual (1er lunes del mes)
- [ ] Revisar métricas de modelo vs baseline
- [ ] Analizar drift reports
- [ ] Actualizar dependencias menores
- [ ] Revisar y cerrar issues antiguos

### Trimestral (1er semana del trimestre)
- [ ] Reentrenar modelo con datos recientes
- [ ] Auditoría de sesgos
- [ ] Actualizar Model Card
- [ ] Revisar y actualizar documentación
- [ ] Actualizar dependencias mayores

### Semestral
- [ ] Revisión de arquitectura
- [ ] Evaluación de nuevos algoritmos
- [ ] Benchmark contra soluciones alternativas
- [ ] Actualización de infraestructura
```

---

## 🔧 Mini-Proyecto: Sistema de Mantenimiento

### Objetivo

1. Crear MAINTENANCE_GUIDE.md
2. Implementar tests de regresión
3. Crear script de validación
4. Definir calendario de revisiones

### Estructura

```
work/11_mantenimiento_auditoria/
├── docs/
│   ├── MAINTENANCE_GUIDE.md
│   └── RUNBOOKS.md
├── tests/
│   └── regression/
│       ├── test_model_regression.py
│       └── baseline_metrics.json
├── scripts/
│   ├── validate_guide.sh
│   └── update_deps.py
└── CALENDAR.md
```

### Criterios de Éxito

- [ ] MAINTENANCE_GUIDE.md completo
- [ ] Tests de regresión implementados
- [ ] Script de validación funcional
- [ ] Calendario definido

---

## ✅ Validación

```bash
make check-11
```

---

## 🎉 ¡Felicitaciones!

Has completado todos los módulos de la Guía MLOps v2. Ahora tienes las habilidades para:

- ✅ Construir pipelines ML profesionales
- ✅ Implementar CI/CD con testing
- ✅ Desplegar APIs y dashboards
- ✅ Monitorear y mantener sistemas ML

**Siguiente paso**: Aplica todo lo aprendido reproduciendo los proyectos del portafolio.

---

*Última actualización: 2024-12*
