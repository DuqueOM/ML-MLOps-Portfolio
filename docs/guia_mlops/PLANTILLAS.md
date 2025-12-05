# 📋 Plantillas Reutilizables — Guía MLOps

> **Templates listos para usar en tus proyectos ML**

> 📁 **Ver también**: [templates/](templates/index.md) contiene las plantillas como archivos individuales descargables.

---

## 📄 1. Template README.md

```markdown
# 🚀 [Nombre del Proyecto]

[![CI](https://github.com/USER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/REPO/actions)
[![Coverage](https://img.shields.io/badge/Coverage-XX%25-brightgreen)](reports/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)

> Breve descripción del proyecto en una línea.

## 🎯 Métricas del Modelo

| Métrica | Valor |
|---------|-------|
| Accuracy | XX% |
| F1-Score | X.XX |
| Coverage | XX% |

## ⚡ Quick Start

```bash
# Clonar
git clone https://github.com/USER/REPO.git
cd REPO

# Instalar
pip install -e ".[dev]"

# Entrenar
make train

# Tests
make test

# Servir API
make serve
\`\`\`

## 📁 Estructura

\`\`\`
proyecto/
├── src/proyecto/      # Código fuente
├── app/               # APIs
├── tests/             # Tests
├── configs/           # Configuración
└── artifacts/         # Modelos (gitignored)
\`\`\`

## 📖 Documentación

- [Model Card](docs/model_card.md)
- [API Reference](docs/api.md)
```

---

## 📄 2. Template pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mi-proyecto"
version = "1.0.0"
description = "Descripción del proyecto"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}

dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
api = ["fastapi>=0.104.0", "uvicorn>=0.24.0"]
dev = ["pytest>=7.4.0", "pytest-cov>=4.1.0", "black>=23.0.0", "ruff>=0.1.0"]
all = ["mi-proyecto[api,dev]"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=src/"

[tool.coverage.run]
source = ["src"]

[tool.coverage.report]
fail_under = 80
```

---

## 📄 3. Template Dockerfile

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/deps -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
RUN useradd --create-home appuser
WORKDIR /app
COPY --from=builder /deps /usr/local/lib/python3.11/site-packages/
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser artifacts/ ./artifacts/
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📄 4. Template GitHub Actions

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: pip install -e ".[dev]"
      
      - name: Lint
        run: ruff check src/ tests/
      
      - name: Test
        run: pytest --cov=src/ --cov-fail-under=80
```

---

## 📄 5. Template conftest.py

```python
import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def sample_data():
    np.random.seed(42)
    return pd.DataFrame({
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'target': np.random.randint(0, 2, 100)
    })

@pytest.fixture
def config():
    return {
        'model': {'n_estimators': 10, 'random_state': 42},
        'data': {'test_size': 0.2}
    }
```

---

## 📄 6. Template Model Card

```markdown
# Model Card: [Nombre del Modelo]

## Información General
- **Desarrollador**: [Tu nombre]
- **Fecha**: [Fecha]
- **Versión**: 1.0.0
- **Tipo**: Clasificación binaria

## Uso Previsto
- **Usuarios**: [Quién usará el modelo]
- **Casos de uso**: [Para qué se usará]

## Métricas
| Métrica | Train | Test |
|---------|-------|------|
| Accuracy | X% | X% |
| Precision | X% | X% |
| Recall | X% | X% |
| F1 | X% | X% |

## Limitaciones
- [Limitación 1]
- [Limitación 2]

## Consideraciones Éticas
- [Consideración 1]
```

---

## 📄 7. Template .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# Environments
.venv/
venv/

# Data & Models
data/
artifacts/
*.joblib
mlruns/

# IDE
.vscode/
.idea/

# Coverage
.coverage
htmlcov/

# Env
.env
```

---

## 📄 8. Template Makefile

```makefile
.PHONY: install test lint train serve clean

install:
pip install -e ".[dev]"

test:
pytest --cov=src/ --cov-fail-under=80

lint:
ruff check src/ tests/
black --check src/ tests/

format:
black src/ tests/
ruff check --fix src/ tests/

train:
python -m src.proyecto.training

serve:
uvicorn app.fastapi_app:app --reload --port 8000

clean:
rm -rf __pycache__ .pytest_cache .coverage htmlcov
```

---

## 📚 Módulos que Usan Estas Plantillas

| Plantilla | Módulo |
|-----------|--------|
| README, pyproject, Makefile | [03_ESTRUCTURA_PROYECTO.md](03_ESTRUCTURA_PROYECTO.md) |
| GitHub Actions | [12_CI_CD.md](12_CI_CD.md) |
| Dockerfile | [13_DOCKER.md](13_DOCKER.md) |
| Model Card | [19_DOCUMENTACION.md](19_DOCUMENTACION.md) |

---

<div align="center">

[← Volver al Índice](00_INDICE.md) | [templates/](templates/index.md)

</div>
