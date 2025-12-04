# 08 — CI/CD & Testing

> **Tiempo estimado**: 3 días (24 horas)
> 
> **Prerrequisitos**: Módulos 01-07 completados

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Configurar **GitHub Actions** para CI/CD
2. ✅ Implementar **matrix testing** multi-versión
3. ✅ Alcanzar **80%+ coverage** con pytest
4. ✅ Configurar **security scanning**

---

## 📖 Contenido Teórico

### 1. Estructura de Workflow CI

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install linters
        run: pip install ruff mypy
      - name: Run Ruff
        run: ruff check src/ tests/
      - name: Run MyPy
        run: mypy src/ --ignore-missing-imports

  test:
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests
        run: pytest tests/ --cov=src --cov-report=xml --cov-fail-under=80
      - name: Upload coverage
        if: matrix.python-version == '3.11'
        uses: codecov/codecov-action@v4

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
      - name: Run pip-audit
        run: |
          pip install pip-audit
          pip-audit
```

---

### 2. Testing con pytest

#### Estructura de Tests

```
tests/
├── __init__.py
├── conftest.py         # Fixtures compartidas
├── unit/
│   ├── test_data.py
│   ├── test_features.py
│   └── test_model.py
└── integration/
    ├── test_pipeline.py
    └── test_api.py
```

#### Fixtures en conftest.py

```python
"""tests/conftest.py — Fixtures compartidas."""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """DataFrame de ejemplo para tests."""
    np.random.seed(42)
    n = 100
    return pd.DataFrame({
        "age": np.random.randint(18, 80, n),
        "balance": np.random.uniform(0, 100000, n),
        "tenure": np.random.randint(0, 60, n),
        "is_active": np.random.choice([True, False], n),
        "churn": np.random.choice([0, 1], n),
    })


@pytest.fixture
def trained_pipeline(sample_data):
    """Pipeline entrenado para tests."""
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier
    
    X = sample_data.drop("churn", axis=1)
    y = sample_data["churn"]
    
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(n_estimators=10, random_state=42)),
    ])
    pipeline.fit(X, y)
    return pipeline


@pytest.fixture
def temp_dir(tmp_path) -> Path:
    """Directorio temporal para tests."""
    return tmp_path
```

#### Tests de Cobertura

```python
"""tests/unit/test_data.py — Tests unitarios."""
import pytest
import pandas as pd
from src.data import load_csv, validate_data


class TestLoadCsv:
    """Tests para load_csv."""
    
    def test_load_existing_file(self, temp_dir):
        # Crear archivo temporal
        path = temp_dir / "test.csv"
        pd.DataFrame({"a": [1, 2], "b": [3, 4]}).to_csv(path, index=False)
        
        df = load_csv(path)
        assert len(df) == 2
        assert list(df.columns) == ["a", "b"]
    
    def test_load_nonexistent_raises(self):
        with pytest.raises(FileNotFoundError):
            load_csv("nonexistent.csv")
    
    def test_load_with_columns(self, temp_dir):
        path = temp_dir / "test.csv"
        pd.DataFrame({"a": [1], "b": [2], "c": [3]}).to_csv(path, index=False)
        
        df = load_csv(path, columns=["a", "b"])
        assert list(df.columns) == ["a", "b"]


class TestValidateData:
    """Tests para validate_data."""
    
    def test_valid_data_passes(self, sample_data):
        # No debería lanzar excepción
        validate_data(sample_data)
    
    def test_empty_df_raises(self):
        with pytest.raises(ValueError):
            validate_data(pd.DataFrame())
    
    @pytest.mark.parametrize("column", ["age", "balance", "churn"])
    def test_missing_column_raises(self, sample_data, column):
        df = sample_data.drop(columns=[column])
        with pytest.raises(KeyError):
            validate_data(df)
```

---

### 3. Simulación Local con act

```bash
# Instalar act
brew install act  # macOS
# o
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Ejecutar workflow localmente
act -j lint          # Solo job lint
act -j test          # Solo job test
act push             # Simular push
```

---

### 4. Coverage Report

```bash
# Ejecutar con coverage
pytest tests/ --cov=src --cov-report=html

# Abrir reporte
open htmlcov/index.html
```

---

## 🔧 Mini-Proyecto: Pipeline CI

### Objetivo

1. Crear workflow GitHub Actions
2. Configurar matrix testing
3. Alcanzar 80% coverage
4. Agregar security scanning

### Criterios de Éxito

- [ ] Workflow ejecuta en GitHub
- [ ] Tests pasan en Python 3.10, 3.11, 3.12
- [ ] Coverage >= 80%
- [ ] Sin vulnerabilidades críticas

---

## ✅ Validación

```bash
make check-08
```

---

## ➡️ Siguiente Módulo

**[09 — Model & Dataset Cards](../09_modelcards_datasetcards/index.md)**

---

*Última actualización: 2024-12*
