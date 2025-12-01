# Reporte Global de Calidad de Código — Portafolio ML-MLOps

**Fecha**: 2025-11-25  
**Alcance**: BankChurn-Predictor, CarVision-Market-Intelligence, TelecomAI-Customer-Intelligence  
**Herramientas**: Black, Flake8, mypy, Radon

---

## 1) Resumen Ejecutivo

Este reporte consolida los resultados de análisis de calidad de código para los tres proyectos principales del portafolio ML-MLOps. Los hallazgos demuestran un nivel de calidad profesional con oportunidades específicas de mejora.

### Dashboard de Calidad

| Proyecto | Black | Flake8 | mypy Errors | Complejidad | Cobertura |
|----------|-------|--------|-------------|-------------|-----------|
| BankChurn-Predictor | ✅ Pass | ✅ Pass | 4 | A (3.76) | 78% |
| CarVision-Market-Intelligence | ⚠️ 3 files | ✅ Pass | 1 | A (4.19) | 86% |
| TelecomAI-Customer-Intelligence | ✅ Pass | ✅ Pass | 0 | A (2.73) | 91% |

**Conclusión general**: El portafolio presenta buena calidad de código con complejidad mantenible. Los issues identificados son menores y fácilmente corregibles.

---

## 2) Análisis de Formateo (Black)

### ¿Qué es Black?
Black es un formateador de código Python "sin configuración" que aplica un estilo consistente automáticamente. Un código bien formateado es más fácil de leer y revisar.

### Resultados por Proyecto

#### BankChurn-Predictor ✅
```bash
black --check BankChurn-Predictor/src BankChurn-Predictor/app BankChurn-Predictor/tests
```
```
All done! ✨ 🍰 ✨
20 files would be left unchanged.
```

#### CarVision-Market-Intelligence ⚠️
```bash
black --check CarVision-Market-Intelligence/src CarVision-Market-Intelligence/app
```
```
would reformat src/carvision/data.py
would reformat src/carvision/visualization.py
would reformat app/streamlit_app.py

3 files would be reformatted, 19 files would be left unchanged.
```

**Archivos a formatear:**
- `src/carvision/data.py`
- `src/carvision/visualization.py`
- `app/streamlit_app.py`

**Comando de corrección:**
```bash
cd CarVision-Market-Intelligence
black src/carvision/data.py src/carvision/visualization.py app/streamlit_app.py
```

#### TelecomAI-Customer-Intelligence ✅
```bash
black --check TelecomAI-Customer-Intelligence/src TelecomAI-Customer-Intelligence/app
```
```
All done! ✨ 🍰 ✨
14 files would be left unchanged.
```

---

## 3) Análisis de Estilo (Flake8)

### ¿Qué es Flake8?
Flake8 verifica el código contra las convenciones de estilo PEP 8 y detecta errores comunes de programación.

### Configuración Utilizada
```
--max-line-length=120
--statistics
```

### Resultados

| Proyecto | Errores | Warnings | Estado |
|----------|---------|----------|--------|
| BankChurn-Predictor | 0 | 0 | ✅ |
| CarVision-Market-Intelligence | 0 | 0 | ✅ |
| TelecomAI-Customer-Intelligence | 0 | 0 | ✅ |

✅ **Todos los proyectos pasan Flake8 sin issues.**

---

## 4) Análisis de Tipado Estático (mypy)

### ¿Qué es mypy?
mypy es un verificador de tipos estáticos para Python que detecta errores de tipo antes de ejecutar el código.

### Configuración Utilizada
```
--ignore-missing-imports
--no-error-summary
```

### Resultados Detallados

#### BankChurn-Predictor (4 errores)

| Archivo | Línea | Error | Severidad |
|---------|-------|-------|-----------|
| `config.py` | 12 | Library stubs not installed for "yaml" | ⚠️ Warning |
| `config.py` | 55 | Missing named argument "voting" for EnsembleConfig | ❌ Error |
| `config.py` | 123 | Missing named argument "test_size" for ModelConfig | ❌ Error |
| `config.py` | 123 | Missing named argument "cv_folds" for ModelConfig | ❌ Error |

**Análisis**: Los errores en líneas 55 y 123 indican que las dataclasses tienen campos requeridos que se están pasando sin nombre o que faltan valores por defecto.

**Corrección sugerida:**
```python
# Antes
@dataclass
class EnsembleConfig:
    voting: str  # Requerido

# Después
@dataclass
class EnsembleConfig:
    voting: str = "soft"  # Con default
```

#### CarVision-Market-Intelligence (1 error)

| Archivo | Línea | Error | Severidad |
|---------|-------|-------|-----------|
| `data.py` | 33 | Incompatible default for argument "filters" | ❌ Error |

**Análisis**: El parámetro `filters: dict[str, float] = None` usa `None` como default pero el tipo no incluye `Optional`.

**Corrección:**
```python
from typing import Optional

def clean_data(df: pd.DataFrame, filters: Optional[dict[str, float]] = None):
    ...
```

#### TelecomAI-Customer-Intelligence (0 errores, 2 warnings)

| Archivo | Línea | Warning |
|---------|-------|---------|
| `evaluation.py` | 12 | Library stubs not installed for "yaml" |
| `config.py` | 5 | Library stubs not installed for "yaml" |

**Corrección global:**
```bash
pip install types-PyYAML
```

---

## 5) Análisis de Complejidad (Radon)

### ¿Qué es Radon?
Radon mide la complejidad ciclomática del código. Una complejidad alta indica código difícil de testear y mantener.

### Escala de Complejidad

| Grado | Rango | Significado | Acción |
|-------|-------|-------------|--------|
| A | 1-5 | Simple | ✅ Mantener |
| B | 6-10 | Más complejo | ✅ Aceptable |
| C | 11-20 | Complejo | ⚠️ Considerar refactor |
| D | 21-30 | Muy complejo | ❌ Refactorizar |
| E | 31-40 | Alto riesgo | ❌ Urgente |
| F | >40 | Inmantenible | ❌ Crítico |

### Resultados Consolidados

```
┌──────────────────────────────────────┬────────────┬──────────────┬──────────┐
│ Proyecto                             │ Promedio   │ Funciones A-B│ Func. C+ │
├──────────────────────────────────────┼────────────┼──────────────┼──────────┤
│ BankChurn-Predictor                  │ A (3.76)   │ 40           │ 2        │
│ CarVision-Market-Intelligence        │ A (4.19)   │ 30           │ 2        │
│ TelecomAI-Customer-Intelligence      │ A (2.73)   │ 11           │ 0        │
├──────────────────────────────────────┼────────────┼──────────────┼──────────┤
│ TOTAL                                │ A (3.69)   │ 81           │ 4        │
└──────────────────────────────────────┴────────────┴──────────────┴──────────┘
```

### Funciones con Complejidad C (Candidatas a Refactor)

| Proyecto | Función | Archivo | CC | Recomendación |
|----------|---------|---------|----|--------------
| BankChurn | `ChurnPredictor.predict` | `prediction.py:78` | 13 | Extraer validación y formateo |
| BankChurn | `ChurnTrainer.build_preprocessor` | `training.py:136` | 11 | Separar en builders |
| CarVision | `infer_feature_types` | `data.py:64` | 14 | Extraer lógica de inferencia |
| CarVision | `generate_executive_summary` | `analysis.py:145` | 13 | Dividir en secciones |

### Ejemplo de Refactor: `infer_feature_types`

**Antes (CC=14):**
```python
def infer_feature_types(df):
    numeric = []
    categorical = []
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            if df[col].nunique() < 10:
                categorical.append(col)
            else:
                numeric.append(col)
        elif df[col].dtype == 'object':
            categorical.append(col)
        elif df[col].dtype == 'bool':
            categorical.append(col)
        # ... más condiciones
    return numeric, categorical
```

**Después (CC~5 cada una):**
```python
def infer_feature_types(df):
    """Orchestrator function."""
    numeric = _identify_numeric_features(df)
    categorical = _identify_categorical_features(df)
    return numeric, categorical

def _identify_numeric_features(df):
    """Identify numeric features."""
    return [col for col in df.columns 
            if _is_numeric(df[col]) and not _is_low_cardinality(df[col])]

def _identify_categorical_features(df):
    """Identify categorical features."""
    return [col for col in df.columns 
            if _is_categorical(df[col]) or _is_low_cardinality(df[col])]

def _is_numeric(series):
    return series.dtype in ['int64', 'float64']

def _is_categorical(series):
    return series.dtype in ['object', 'bool']

def _is_low_cardinality(series, threshold=10):
    return series.nunique() < threshold
```

---

## 6) Análisis de Cobertura de Tests

### Resultados por Proyecto

| Proyecto | Tests | Pasando | Fallando | Cobertura | Umbral |
|----------|-------|---------|----------|-----------|--------|
| BankChurn-Predictor | 88 | 87 | 0 | 78% | 65% ✅ |
| CarVision-Market-Intelligence | 17 | 17 | 0 | 86% | 70% ✅ |
| TelecomAI-Customer-Intelligence | 14 | 13 | 0 | 91% | 72% ✅ |

### Módulos con Baja Cobertura

| Proyecto | Módulo | Cobertura | Razón |
|----------|--------|-----------|-------|
| BankChurn | `prediction.py` | 55% | Funciones de explicabilidad sin tests |
| CarVision | `visualization.py` | 0% | Módulo de gráficos Plotly sin tests |
| TelecomAI | `fastapi_app.py` | 72% | Error handlers sin tests |

### Recomendación de Tests Prioritarios

1. **CarVision `visualization.py`**: Añadir tests básicos que verifiquen que los gráficos se generan sin error
2. **BankChurn `prediction.py`**: Añadir tests para `explain_prediction` y métodos auxiliares
3. **TelecomAI `fastapi_app.py`**: Tests para casos de error (422, 500)

---

## 7) Plan de Acción Consolidado

### Semana 1 — Correcciones Rápidas

```bash
# 1. Formatear CarVision
cd CarVision-Market-Intelligence
black src/carvision/data.py src/carvision/visualization.py app/streamlit_app.py

# 2. Instalar type stubs (todos los proyectos)
pip install types-PyYAML

# 3. Corregir Optional en CarVision/data.py
# Cambiar: filters: dict[str, float] = None
# A:       filters: Optional[dict[str, float]] = None
```

### Semana 2-3 — Correcciones de Tipado

1. Añadir defaults a `EnsembleConfig.voting` en BankChurn
2. Añadir defaults a `ModelConfig.test_size` y `cv_folds` en BankChurn
3. Verificar con `mypy --strict` después de correcciones

### Mes 1 — Refactoring de Complejidad

1. Refactorizar `ChurnPredictor.predict` (BankChurn)
2. Refactorizar `infer_feature_types` (CarVision)
3. Añadir tests a `visualization.py` (CarVision)

---

## 8) Métricas Clave para Monitoreo Continuo

Recomendamos configurar estas métricas en CI/CD:

```yaml
quality-gates:
  coverage:
    minimum: 70%
    target: 85%
  complexity:
    max_function_cc: 15
    max_average_cc: 5
  linting:
    black: required
    flake8: required
  typing:
    mypy_errors: 0
```

### Script de Verificación Rápida

```bash
#!/bin/bash
# scripts/check_quality.sh

echo "=== Verificación de Calidad ==="

echo -e "\n[1/4] Black check..."
black --check . --quiet && echo "✅ Black OK" || echo "❌ Black FAIL"

echo -e "\n[2/4] Flake8 check..."
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics && echo "✅ Flake8 OK" || echo "❌ Flake8 FAIL"

echo -e "\n[3/4] mypy check..."
mypy . --ignore-missing-imports --no-error-summary && echo "✅ mypy OK" || echo "⚠️ mypy warnings"

echo -e "\n[4/4] Radon complexity..."
radon cc . -a -s | tail -1
```

---

## 9) Conclusiones

### Fortalezas del Portafolio
- ✅ Complejidad promedio A — código mantenible
- ✅ Todos los proyectos pasan Flake8
- ✅ Cobertura de tests superior al umbral en todos los proyectos
- ✅ TelecomAI es un modelo de buenas prácticas

### Oportunidades de Mejora
- ⚠️ 3 archivos sin formatear en CarVision
- ⚠️ 5 errores de mypy a corregir
- ⚠️ 4 funciones con complejidad C
- ⚠️ `visualization.py` sin cobertura de tests

### Próximo Paso Recomendado
Ejecutar las correcciones de Semana 1 y establecer quality gates en CI/CD para prevenir regresiones.

---

*Reporte generado automáticamente como parte del proceso de auditoría del portafolio ML-MLOps.*
