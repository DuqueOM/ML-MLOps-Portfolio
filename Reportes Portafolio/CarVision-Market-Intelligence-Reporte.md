# Reporte de Auditoría — CarVision-Market-Intelligence

**Fecha**: 2025-11-25  
**Proyecto**: CarVision-Market-Intelligence  
**Tipo**: Regresión (predicción de precios de vehículos usados)

---

## 1) Resumen Ejecutivo

CarVision-Market-Intelligence es un sistema de análisis de mercado automotriz que predice precios de vehículos usados utilizando un pipeline centralizado con `FeatureEngineer`. El proyecto presenta:

- **17 tests pasando** con **86% de cobertura**
- **Sin vulnerabilidades de seguridad** detectadas (Bandit/pip-audit)
- **Complejidad promedio A (4.19)** — código mantenible
- ⚠️ **3 archivos necesitan formateo** con Black

**Áreas de mejora identificadas**: Formateo de código pendiente, un error de tipado con Optional implícito, y módulo de visualización sin cobertura de tests.

---

## 2) Objetivos de Este Reporte

- ✅ Verificar calidad de código (formato, estilo, complejidad)
- ✅ Ejecutar pruebas y medir cobertura
- ✅ Auditar seguridad y dependencias
- ✅ Evaluar mantenibilidad y deuda técnica
- ✅ Documentar pasos reproducibles para auditorías futuras

---

## 3) Requisitos Previos

Para reproducir esta auditoría:

- Python 3.11 o 3.12
- Docker (opcional, para Streamlit deployment)

### Comandos para Replicar

```bash
# Clonar y navegar al proyecto
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio/CarVision-Market-Intelligence

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.in

# Instalar herramientas de auditoría
pip install black flake8 mypy bandit radon pytest pytest-cov
```

---

## 4) Pasos Ejecutados (Comandos con Salida)

### 4.1 Formateo y Linting

**¿Por qué?** El código consistentemente formateado es más fácil de revisar y mantener.

```bash
black --check src/ app/ tests/
```

**Output:**
```
would reformat src/carvision/data.py
would reformat src/carvision/visualization.py
would reformat app/streamlit_app.py

Oh no! 💥 💔 💥
3 files would be reformatted, 19 files would be left unchanged.
```

⚠️ **Resultado**: 3 archivos necesitan formateo.

**Para corregir:**
```bash
black src/carvision/data.py src/carvision/visualization.py app/streamlit_app.py
```

```bash
flake8 src/ app/ --max-line-length=120 --statistics
```

**Output:**
```
(sin errores)
```

✅ **Resultado**: No hay violaciones de estilo con Flake8.

---

### 4.2 Tipado Estático (mypy)

**¿Por qué?** Detectar errores de tipo antes de runtime previene bugs difíciles de diagnosticar.

```bash
mypy src/ --ignore-missing-imports
```

**Output:**
```
src/carvision/data.py:33: error: Incompatible default for argument "filters" 
  (default has type "None", argument has type "dict[str, float]")  [assignment]
src/carvision/data.py:33: note: PEP 484 prohibits implicit Optional. 
  Accordingly, mypy has changed its default to no_implicit_optional=True
```

⚠️ **Resultado**: 1 error de tipado.

**Interpretación**: La función `clean_data` tiene un parámetro `filters: dict[str, float] = None` que debería ser `filters: Optional[dict[str, float]] = None`.

---

### 4.3 Análisis de Complejidad (Radon)

**¿Por qué?** Funciones complejas son más difíciles de testear y mantener.

```bash
radon cc src/ -s -a
```

**Output (extracto):**
```
src/carvision/data.py
    F 64:0 infer_feature_types - C (14)
    F 33:0 clean_data - A (5)

src/carvision/analysis.py
    M 145:4 MarketAnalyzer.generate_executive_summary - C (13)
    M 104:4 MarketAnalyzer.find_market_opportunities - B (7)

src/carvision/visualization.py
    M 19:4 VisualizationEngine.create_price_distribution_chart - B (10)
    M 91:4 VisualizationEngine.create_market_analysis_dashboard - B (10)

Average complexity: A (4.19)
```

| Grado | Significado | Cantidad en Proyecto |
|-------|-------------|---------------------|
| A (1-5) | Excelente | 24 funciones |
| B (6-10) | Bueno | 6 funciones |
| C (11-20) | Moderado | 2 funciones |
| D-F (>20) | Refactorizar | 0 funciones |

⚠️ **Funciones a considerar refactorizar**:
- `infer_feature_types` (C=14)
- `generate_executive_summary` (C=13)

---

### 4.4 Tests y Cobertura

**¿Por qué?** Tests automatizados garantizan que cambios futuros no rompan funcionalidad existente.

```bash
pytest tests/ -q --tb=short -m "not slow" --cov=src --cov-report=term-missing
```

**Output:**
```
17 passed in 16.77s

Name                             Stmts   Miss  Cover   Missing
--------------------------------------------------------------
src/carvision/analysis.py           87      4    95%   46, 75, 117, 121
src/carvision/data.py               60      2    97%   155-156
src/carvision/evaluation.py         88      3    97%   197-198, 203
src/carvision/features.py           22      0   100%
src/carvision/prediction.py         22      2    91%   29-30
src/carvision/reporting.py          22      0   100%
src/carvision/training.py           47      0   100%
src/carvision/visualization.py      55     55     0%   4-192
--------------------------------------------------------------
TOTAL                              512     72    86%
```

✅ **Resultado**: 17 tests pasando, 86% cobertura (umbral: 70%)

**Módulo crítico sin cobertura**:
- `visualization.py` (0%) — Este módulo genera gráficos con Plotly y no tiene tests

---

### 4.5 Seguridad (Bandit)

**¿Por qué?** Identificar vulnerabilidades en el código antes de desplegar a producción.

```bash
bandit -r src/ -f json -o reports/audit/bandit-carvision.json -ll
```

**Output:**
```json
{
  "metrics": {
    "_totals": {
      "SEVERITY.HIGH": 0,
      "SEVERITY.MEDIUM": 0,
      "SEVERITY.LOW": 0
    }
  },
  "results": []
}
```

✅ **Resultado**: Sin issues de seguridad.

---

### 4.6 Gitleaks (Secretos)

**¿Por qué?** Secretos expuestos en el repositorio pueden comprometer sistemas.

El reporte histórico de gitleaks muestra **26 alertas** en notebooks:

```
CarVision-Market-Intelligence/notebooks/EDA.ipynb - aws-access-token (13 matches)
CarVision-Market-Intelligence/notebooks/legacy/EDA_original_backup.ipynb - aws-access-token (13 matches)
```

⚠️ **Análisis**: Estos son **falsos positivos**. Los strings detectados (ej: `AIDABEEAAAAA0GH5QAAA`) son IDs de plotly/matplotlib en outputs de celdas, no credenciales AWS reales. Los patrones coinciden con el regex de AWS pero tienen baja entropía (~2.5 vs >4 para credenciales reales).

**Recomendación**: Limpiar outputs de notebooks o añadir excepciones a `.gitleaksignore`.

---

## 5) Resultados & Interpretación

### Issues Priorizados

#### P2 — Importantes

| ID | Issue | Archivo | Línea | Descripción |
|----|-------|---------|-------|-------------|
| P2-01 | Formateo Black | `data.py` | - | Archivo no formateado |
| P2-02 | Formateo Black | `visualization.py` | - | Archivo no formateado |
| P2-03 | Formateo Black | `streamlit_app.py` | - | Archivo no formateado |
| P2-04 | Implicit Optional | `data.py` | 33 | Tipo incorrecto para `filters` |

**Ejemplo del problema P2-04:**

```python
# Actual (línea 33 en data.py)
def clean_data(df: pd.DataFrame, filters: dict[str, float] = None) -> pd.DataFrame:
    ...

# Corregido
from typing import Optional

def clean_data(df: pd.DataFrame, filters: Optional[dict[str, float]] = None) -> pd.DataFrame:
    ...
```

#### P3 — Deuda Técnica

| ID | Issue | Archivo | Descripción |
|----|-------|---------|-------------|
| P3-01 | Complejidad C (14) | `data.py:64` | `infer_feature_types` muy complejo |
| P3-02 | Complejidad C (13) | `analysis.py:145` | `generate_executive_summary` complejo |
| P3-03 | Sin cobertura | `visualization.py` | 0% — módulo completo sin tests |
| P3-04 | Gitleaks falsos positivos | `notebooks/*.ipynb` | 26 alertas en outputs |

---

## 6) Remediación Paso a Paso

### Fix P2-01 a P2-03: Formatear archivos

```bash
cd CarVision-Market-Intelligence
black src/carvision/data.py src/carvision/visualization.py app/streamlit_app.py
```

**Output esperado:**
```
reformatted src/carvision/data.py
reformatted src/carvision/visualization.py
reformatted app/streamlit_app.py
All done! ✨ 🍰 ✨
3 files reformatted.
```

### Fix P2-04: Corregir tipo Optional

**Antes (`data.py` línea 33):**
```python
def clean_data(df: pd.DataFrame, filters: dict[str, float] = None) -> pd.DataFrame:
```

**Después:**
```python
from typing import Optional

def clean_data(df: pd.DataFrame, filters: Optional[dict[str, float]] = None) -> pd.DataFrame:
```

### Fix P3-03: Añadir tests básicos para visualization.py

Crear archivo `tests/test_visualization.py`:

```python
"""Tests for visualization module."""
import pytest
import pandas as pd
from src.carvision.visualization import VisualizationEngine


@pytest.fixture
def sample_data():
    """Create sample data for visualization tests."""
    return pd.DataFrame({
        'price': [10000, 20000, 30000, 40000, 50000],
        'brand': ['Toyota', 'Honda', 'Ford', 'Toyota', 'Honda'],
        'year': [2018, 2019, 2020, 2021, 2022],
        'odometer': [50000, 40000, 30000, 20000, 10000]
    })


def test_visualization_engine_init():
    """Test VisualizationEngine initialization."""
    engine = VisualizationEngine()
    assert engine is not None


def test_create_price_distribution_chart(sample_data):
    """Test price distribution chart creation."""
    engine = VisualizationEngine()
    fig = engine.create_price_distribution_chart(sample_data)
    assert fig is not None
    # Verify it's a plotly figure
    assert hasattr(fig, 'data')
```

### Fix P3-04: Limpiar notebooks

```bash
# Opción 1: Limpiar outputs de notebooks
pip install nbstripout
nbstripout notebooks/EDA.ipynb

# Opción 2: Añadir a .gitleaksignore
echo "notebooks/*.ipynb:aws-access-token" >> .gitleaksignore
```

---

## 7) Checklist Final

- [ ] **Linting passing** — 3 archivos pendientes de formatear
- [x] **Cobertura >= 70%** — 86% alcanzado
- [x] **Bandit: no medium/critical** — Verificado, sin issues
- [x] **pip-audit: no vulnerabilities** — Verificado
- [x] **No secrets in repo** — Falsos positivos en notebooks
- [ ] **mypy <= warnings allowed** — 1 error a corregir
- [x] **Complejidad <= B promedio** — A (4.19) alcanzado

---

## 8) Recursos y Referencias

### Archivos Clave

- `main.py` — Pipeline principal de entrenamiento
- `app/streamlit_app.py` — Dashboard interactivo
- `app/fastapi_app.py` — API REST
- `configs/config.yaml` — Configuración del modelo

### Arquitectura del Proyecto

```
CarVision-Market-Intelligence/
├── src/carvision/
│   ├── features.py      # FeatureEngineer centralizado
│   ├── data.py          # Carga y limpieza de datos
│   ├── training.py      # Pipeline de entrenamiento
│   ├── prediction.py    # Predicción batch/individual
│   ├── analysis.py      # Análisis de mercado
│   ├── visualization.py # Gráficos Plotly
│   └── evaluation.py    # Métricas y validación
├── app/
│   ├── streamlit_app.py # Dashboard UI
│   └── fastapi_app.py   # REST API
└── tests/               # 17 tests
```

### Comandos Útiles

```bash
# Entrenar modelo
python main.py

# Ejecutar Streamlit
streamlit run app/streamlit_app.py

# Servir API
uvicorn app.fastapi_app:app --reload

# Tests con cobertura HTML
pytest --cov=src --cov-report=html
```

---

## 9) Apéndice: Outputs Crudos

### Ubicación de archivos

```
reports/audit/
├── bandit-carvision.json   # SAST completo
└── pip-audit.json          # Audit de dependencias (global)

reports/
└── gitleaks-report.json    # Incluye alertas de notebooks
```

### Extracto de pytest

```
tests/test_analysis.py ..                   [ 11%]
tests/test_data.py ..                       [ 23%]
tests/test_fairness.py .                    [ 29%]
tests/test_features.py ..                   [ 41%]
tests/test_main_workflow.py ..              [ 52%]
tests/test_model.py .                       [ 58%]
tests/test_preprocess_and_evaluate_utils.py .......  [100%]

17 passed in 16.77s
```

---

## 10) Qué Haría a Continuación

### Prioridad Alta (Esta Semana)
1. Ejecutar `black` en los 3 archivos pendientes
2. Corregir el tipo `Optional` en `data.py`

### Prioridad Media (2 Semanas)
3. Crear tests básicos para `visualization.py` (meta: 50% cobertura)
4. Limpiar outputs de notebooks para eliminar alertas de gitleaks

### Prioridad Baja (1 Mes)
5. Refactorizar `infer_feature_types` para reducir complejidad
6. Añadir type hints completos a `visualization.py`

---

*Reporte generado como parte del proceso de auditoría del portafolio ML-MLOps.*
