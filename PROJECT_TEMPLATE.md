# 📐 Template de Proyecto ML/MLOps - Estándar Tier-1

Este template define la estructura estándar que TODOS los proyectos del portafolio deben seguir.

---

## 📁 Estructura de Directorios Obligatoria

```
ProjectName/
├── src/
│   └── projectname/              # Package principal
│       ├── __init__.py
│       ├── models.py             # Clasificadores/Regresores custom
│       ├── config.py             # Pydantic configs
│       ├── training.py           # Pipeline entrenamiento
│       ├── evaluation.py         # Métricas y evaluación
│       ├── prediction.py         # Inferencia
│       └── cli.py                # CLI moderna
├── app/
│   ├── fastapi_app.py           # API REST
│   └── example_load.py          # Demo de uso
├── tests/
│   ├── conftest.py              # Fixtures compartidos
│   ├── test_models.py           # Tests de modelos
│   ├── test_config.py           # Tests de config
│   ├── test_training.py         # Tests de training
│   ├── test_evaluation.py       # Tests de eval
│   ├── test_prediction.py       # Tests de predicción
│   └── test_api.py              # Tests de API
├── configs/
│   └── config.yaml              # Configuración principal
├── data/
│   ├── raw/                     # Datos originales
│   └── preprocess.py            # Preprocessing
├── monitoring/
│   └── check_drift.py           # Drift detection
├── scripts/
│   └── run_mlflow.py            # MLflow experiments
├── notebooks/
│   └── exploration.ipynb        # EDA
├── .github/
│   └── workflows/
│       └── ci.yml               # CI/CD pipeline
├── Dockerfile                    # Containerización
├── docker-compose.yml           # Orquestación local
├── Makefile                     # Comandos automatizados
├── pyproject.toml               # Modern Python packaging
├── requirements-core.txt        # Deps runtime
├── requirements.txt             # Deps full con hashes
├── README.md                    # Documentación principal
├── model_card.md                # Ficha de modelo
├── data_card.md                 # Ficha de datos
└── LICENSE                      # MIT License
```

---

## 🐍 Módulos Python Estándar

### `src/projectname/models.py`
```python
"""Custom models for [PROJECT_NAME].

Implements domain-specific classifiers/regressors.
"""

from __future__ import annotations
from sklearn.base import BaseEstimator, ClassifierMixin

class CustomModel(BaseEstimator, ClassifierMixin):
    """Custom model implementation."""
    
    def __init__(self, param1: int = 42):
        self.param1 = param1
    
    def fit(self, X, y):
        # Implementation
        return self
    
    def predict(self, X):
        # Implementation
        return predictions
```

### `src/projectname/config.py`
```python
"""Configuration management with Pydantic."""

from __future__ import annotations
from pathlib import Path
from pydantic import BaseModel, Field
import yaml

class ModelConfig(BaseModel):
    """Model configuration."""
    test_size: float = Field(0.2, ge=0.0, le=1.0)
    random_state: int = 42

class DataConfig(BaseModel):
    """Data configuration."""
    target_column: str
    features: list[str] = []

class ProjectConfig(BaseModel):
    """Complete configuration."""
    model: ModelConfig
    data: DataConfig
    
    @classmethod
    def from_yaml(cls, path: str | Path) -> ProjectConfig:
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
```

### `src/projectname/training.py`
```python
"""Training pipeline."""

from __future__ import annotations
import joblib
from pathlib import Path

class Trainer:
    """Training pipeline."""
    
    def __init__(self, config: ProjectConfig):
        self.config = config
    
    def load_data(self, path: Path):
        # Load and validate
        pass
    
    def prepare_features(self, data):
        # Feature engineering
        pass
    
    def train(self, X, y):
        # Training with CV
        return model, metrics
    
    def save_model(self, path: Path):
        joblib.dump(self.model, path)
```

### `src/projectname/evaluation.py`
```python
"""Model evaluation."""

from __future__ import annotations
from sklearn.metrics import classification_report

class Evaluator:
    """Model evaluator."""
    
    def __init__(self, model, preprocessor):
        self.model = model
        self.preprocessor = preprocessor
    
    def evaluate(self, X, y):
        # Compute metrics
        return metrics
    
    def compute_fairness(self, X, y, sensitive_features):
        # Fairness analysis
        return fairness_metrics
```

### `src/projectname/prediction.py`
```python
"""Prediction pipeline."""

from __future__ import annotations
import pandas as pd

class Predictor:
    """Batch predictor."""
    
    def predict(self, X: pd.DataFrame):
        # Transform and predict
        return predictions
    
    def predict_batch(self, input_path, output_path):
        # Batch processing
        pass
```

### `src/projectname/cli.py`
```python
"""Command-line interface."""

from __future__ import annotations
import argparse
import sys

def create_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    
    # train
    train = subparsers.add_parser("train")
    train.add_argument("--config", required=True)
    train.add_argument("--input", required=True)
    
    # evaluate
    eval = subparsers.add_parser("evaluate")
    # ...
    
    # predict
    predict = subparsers.add_parser("predict")
    # ...
    
    return parser

def main(argv=None):
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if args.command == "train":
        # Execute training
        pass
    # ...
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## ✅ pyproject.toml Estándar

```toml
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "projectname"
version = "1.0.0"
description = "Brief description"
requires-python = ">=3.10"
dependencies = [
    "pandas>=1.3.0",
    "numpy>=1.21.0",
    "scikit-learn>=1.0.0",
    "pydantic>=2.0.0",
    "joblib>=1.1.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=3.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]

[project.scripts]
projectname = "src.projectname.cli:main"

[tool.black]
line-length = 120

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=src --cov-report=term-missing --cov-fail-under=75"

[tool.mypy]
python_version = "3.10"
ignore_missing_imports = true
```

---

## 🧪 Tests Estándar

### `tests/conftest.py`
```python
"""Shared fixtures."""
import pytest
from common_utils.seed import set_seed

@pytest.fixture(autouse=True)
def deterministic_seed():
    """Set seed before each test."""
    set_seed(42)
```

### `tests/test_models.py`
```python
"""Test custom models."""
import pytest
from src.projectname.models import CustomModel

def test_model_initialization():
    model = CustomModel(param1=100)
    assert model.param1 == 100

def test_model_fit_predict():
    model = CustomModel()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    assert len(predictions) == len(X_test)
```

---

## 🔄 CI/CD Estándar

### `.github/workflows/ci.yml`
```yaml
name: CI

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install
        run: pip install -e ".[dev]"
      - name: Black
        run: black --check .
      - name: Mypy
        run: mypy src/
      - name: Tests
        run: pytest --cov=src --cov-fail-under=75
```

---

## 📝 README Estándar

```markdown
# Project Name

Brief description (1 sentence).

## Quick Start

\`\`\`bash
# Install
pip install -e .

# Train
projectname train --config configs/config.yaml --input data/raw/data.csv

# Predict
projectname predict --input new_data.csv --output predictions.csv
\`\`\`

## Features

- ✅ Feature 1
- ✅ Feature 2

## Architecture

[Diagram or description]

## Performance

| Metric | Value |
|--------|-------|
| Accuracy | 0.XX |
| F1 Score | 0.XX |

## License

MIT
```

---

## 🎯 Checklist de Conformidad

### Estructura
- [ ] Tiene `src/projectname/` con 6 módulos
- [ ] Tiene `tests/` con cobertura ≥75%
- [ ] Tiene `pyproject.toml` moderno
- [ ] Tiene `Dockerfile` funcional

### Código
- [ ] Type hints en todas las funciones
- [ ] Docstrings estilo NumPy/Google
- [ ] Pasa black, isort, flake8, mypy
- [ ] Complejidad ciclomática <10

### Tests
- [ ] Tests unitarios para cada módulo
- [ ] Tests de integración E2E
- [ ] Tests de API
- [ ] Cobertura ≥75%

### CI/CD
- [ ] GitHub Actions configurado
- [ ] Tests ejecutan en múltiples OS
- [ ] Security scan (bandit)
- [ ] Docker build automático

### Documentación
- [ ] README comprehensivo
- [ ] model_card.md
- [ ] data_card.md
- [ ] API examples

---

## 🚀 Comandos Make Estándar

```makefile
.PHONY: install test lint format train api clean

install:
	pip install -e ".[dev]"

test:
	pytest --cov=src --cov-report=html

lint:
	black --check .
	mypy src/
	flake8 .

format:
	black .
	isort .

train:
	python -m src.projectname.cli train --config configs/config.yaml

api:
	uvicorn app.fastapi_app:app --reload

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
```

---

Este template asegura **consistencia, calidad y profesionalismo** en todos los proyectos del portafolio.
