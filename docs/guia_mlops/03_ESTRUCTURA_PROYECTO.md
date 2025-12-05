# 03. Estructura de Proyecto ML Profesional

## 🎯 Objetivo del Módulo

Crear la estructura de proyecto que usarás en los 3 proyectos del portafolio.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  Una buena estructura de proyecto es como los cimientos de una casa:         ║
║  invisible cuando está bien hecha, DESASTROSA cuando está mal.               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 📋 La Estructura del Portafolio

```
MiProyecto-ML/
│
├── src/                          # 📦 CÓDIGO FUENTE (instalable)
│   ├── __init__.py
│   └── miproyecto/
│       ├── __init__.py
│       ├── config.py             # Configuración Pydantic
│       ├── data.py               # Carga y validación de datos
│       ├── features.py           # Feature engineering
│       ├── training.py           # Pipeline de entrenamiento
│       ├── evaluation.py         # Métricas y evaluación
│       ├── prediction.py         # Inferencia
│       └── models.py             # Custom models/transformers
│
├── app/                          # 🌐 APLICACIONES
│   ├── fastapi_app.py            # API REST
│   └── streamlit_app.py          # Dashboard (opcional)
│
├── tests/                        # 🧪 TESTS (espejo de src/)
│   ├── __init__.py
│   ├── conftest.py               # Fixtures compartidas
│   ├── test_config.py
│   ├── test_data.py
│   ├── test_features.py
│   ├── test_training.py
│   └── test_api.py
│
├── configs/                      # ⚙️ CONFIGURACIÓN
│   └── config.yaml               # Hiperparámetros, paths, etc.
│
├── data/                         # 📊 DATOS (gitignored)
│   ├── raw/                      # Datos originales
│   └── processed/                # Datos procesados (opcional)
│
├── artifacts/                    # 📁 ARTEFACTOS (gitignored)
│   ├── model.joblib              # Modelo entrenado
│   └── metrics.json              # Métricas de entrenamiento
│
├── scripts/                      # 🔧 SCRIPTS AUXILIARES
│   └── run_mlflow.py             # Script de MLflow
│
├── docs/                         # 📖 DOCUMENTACIÓN
│   ├── model_card.md
│   └── data_card.md
│
├── infra/                        # 🏗️ INFRAESTRUCTURA (opcional)
│   └── terraform/
│
├── pyproject.toml                # 📋 METADATA DEL PROYECTO
├── requirements.txt              # 📋 DEPENDENCIAS (para CI)
├── Makefile                      # 🔨 COMANDOS COMUNES
├── Dockerfile                    # 🐳 CONTAINERIZACIÓN
├── .github/workflows/            # 🔄 CI/CD
│   └── ci.yml
├── .gitignore                    # 🚫 ARCHIVOS IGNORADOS
├── .pre-commit-config.yaml       # 🔍 HOOKS PRE-COMMIT
└── README.md                     # 📖 DOCUMENTACIÓN PRINCIPAL
```

## 🧩 Cómo se aplica en este portafolio

Esta estructura no es teórica: los **3 proyectos** del portafolio la siguen con ligeras
variaciones. Esto conecta directamente con los macro-módulos **00** y **01** de la
**Ruta 0 → Senior/Staff** descrita en el [SYLLABUS](SYLLABUS.md).

| Proyecto | Carpeta raíz | Paquete principal | Archivos clave |
|----------|--------------|-------------------|----------------|
| BankChurn Predictor | `BankChurn-Predictor/` | `src/bankchurn/` | `pyproject.toml`, `main.py`, `Makefile`, `tests/` |
| CarVision Market Intelligence | `CarVision-Market-Intelligence/` | `src/carvision/` | `pyproject.toml`, `main.py`, `Makefile`, `tests/` |
| TelecomAI Customer Intelligence | `TelecomAI-Customer-Intelligence/` | `src/telecom/` | `pyproject.toml`, `main.py`, `Makefile`, `tests/` |

Para aprovechar este módulo al máximo en el repositorio real:

- **Compara** el árbol genérico de `MiProyecto-ML/` con, por ejemplo,
  `BankChurn-Predictor/` (fíjate especialmente en `src/`, `configs/`, `tests/`,
  `Makefile` y `pyproject.toml`).
- **Verifica** que los comandos que defines aquí (`make install`, `make test`,
  `make train`, `make serve`) tienen su equivalente funcional en los Makefiles de
  cada proyecto.
- **Usa** esta plantilla como referencia si creas un **cuarto proyecto** durante el
  [20_PROYECTO_INTEGRADOR](20_PROYECTO_INTEGRADOR.md).

---

## 📄 pyproject.toml Completo

```toml
# pyproject.toml - El corazón del proyecto

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "bankchurn"
version = "1.0.0"
description = "Bank Customer Churn Prediction System"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Tu Nombre", email = "tu@email.com"}
]
keywords = ["machine-learning", "churn", "prediction"]

dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0",
    "joblib>=1.3.0",
]

[project.optional-dependencies]
api = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
]
mlflow = [
    "mlflow>=2.9.0",
]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
    "pre-commit>=3.5.0",
]
all = [
    "bankchurn[api,mlflow,dev]",
]

[project.scripts]
bankchurn = "bankchurn.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

# ═══════════════════════════════════════════════════════════════════════════
# HERRAMIENTAS
# ═══════════════════════════════════════════════════════════════════════════

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --cov=src/bankchurn --cov-report=term-missing"

[tool.coverage.run]
source = ["src"]
omit = ["tests/*"]

[tool.coverage.report]
fail_under = 79

[tool.black]
line-length = 100
target-version = ["py311"]

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "W"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
ignore_missing_imports = true
```

---

## 🔨 Makefile

```makefile
# Makefile - Comandos comunes

.PHONY: install test lint format train serve clean

# Instalación
install:
pip install -e ".[all]"

install-prod:
pip install -e ".[api]"

# Testing
test:
pytest --cov=src/ --cov-fail-under=80

test-fast:
pytest -m "not slow" -x

# Linting y formato
lint:
ruff check src/ tests/
mypy src/

format:
black src/ tests/ app/
ruff check --fix src/ tests/

# Entrenamiento
train:
python main.py --seed 42 train --config configs/config.yaml --input data/raw/Churn.csv
serve:
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000 --reload

serve-prod:
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

# Docker
docker-build:
docker build -t bankchurn:latest .

docker-run:
docker run -p 8000:8000 bankchurn:latest

# MLflow
mlflow-ui:
mlflow ui --host 0.0.0.0 --port 5000

# Limpieza
clean:
rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
rm -rf *.egg-info build dist
rm -rf htmlcov .coverage
```

---

## 🚫 .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
.pytest_cache/
.mypy_cache/
*.egg-info/
dist/
build/

# Entornos
.venv/
venv/
env/

# Datos y artefactos (muy grandes para Git)
data/
artifacts/
models/
*.joblib
*.pkl
*.h5

# MLflow
mlruns/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Coverage
.coverage
htmlcov/

# Env vars
.env
.env.local
```

---

## 🧨 Errores habituales y cómo depurarlos en la estructura de proyecto

Aquí los problemas ya no son algoritmos, sino **cómo está organizado el repo**. Son los típicos errores que hacen que algo “funcione en mi máquina pero no en CI” o que el repo se vuelva inmanejable.

### 1) `ModuleNotFoundError` y tests que solo funcionan desde ciertos directorios

**Síntomas típicos**

- En local, ejecutar `pytest` desde la raíz funciona, pero en CI falla con:
  ```text
  ModuleNotFoundError: No module named 'miproyecto'
  ```
- Tienes que hacer trucos como `cd src` o modificar `PYTHONPATH` para que los imports funcionen.

**Cómo identificarlo**

- Revisa tu estructura real:
  - ¿El código está en `src/miproyecto/` o repartido por la raíz?
  - ¿Los tests importan el paquete (`from miproyecto import ...`) o archivos sueltos (`import training`)?
- Mira tu `pyproject.toml`:
  - `[project.name]` → ¿coincide con el nombre del paquete (`miproyecto`, `bankchurn`, etc.)?
  - `[tool.setuptools.packages.find] where = ["src"]` → ¿está configurado?

**Cómo corregirlo**

- Mueve el código a `src/<nombre_paquete>/` siguiendo el árbol de este módulo.
- Asegúrate de que los tests importan siempre el paquete, no rutas relativas.
- Instala en modo editable durante desarrollo/CI:
  ```bash
  pip install -e ".[dev]"
  ```

---

### 2) Datos y modelos dentro de Git (repos gigantes e impracticables)

**Síntomas típicos**

- El repo pesa cientos de MB porque hay CSVs y modelos `.pkl`/`.joblib` versionados.
- `git pull` y `git clone` son lentos, y los PRs están llenos de cambios binarios.

**Cómo identificarlo**

- Ejecuta `git status` y revisa si aparecen archivos en `data/`, `artifacts/`, `models/`.
- Abre tu `.gitignore` y comprueba si tienes entradas como:
  - `data/`, `artifacts/`, `models/`, `*.joblib`, `*.pkl`, `mlruns/`.

**Cómo corregirlo**

- Añade las rutas correctas a `.gitignore` (usa el snippet de este módulo como base).
- Mantén en Git **solo**:
  - Código (`src/`, `app/`, `tests/`).
  - Config (`configs/`).
  - Infra y docs.
- Para datos/modelos usa DVC o un storage externo (se profundiza en `06_VERSIONADO_DATOS.md`).

---

### 3) Tests que no reflejan el árbol de `src/`

**Síntomas típicos**

- Cambias algo en `src/miproyecto/features.py` y ningún test falla, aunque has roto lógica.
- Hay tests sueltos sin relación clara con los módulos de producción.

**Cómo identificarlo**

- Compara árboles:
  - En `src/miproyecto/`: `config.py`, `data.py`, `features.py`, `training.py`, `evaluation.py`, `prediction.py`.
  - En `tests/`: ¿existen `test_config.py`, `test_data.py`, `test_features.py`, etc.?
- Revisa el `pyproject.toml` o `pytest.ini` para ver qué carpeta se usa como `testpaths`.

**Cómo corregirlo**

- Crea un **espejo sencillo**: por cada módulo importante en `src/`, un test correspondiente en `tests/`.
- Usa `conftest.py` para compartir fixtures (datasets pequeños, config de prueba, etc.).
- Integra `pytest --cov=src/` en tu CI para detectar huecos de cobertura.

---

### 4) Makefile y comandos que no se pueden ejecutar

**Síntomas típicos**

- El README dice `make train`, pero:
  - El target `train` no existe.
  - O llama a rutas que no existen (`data/raw/archivo_que_no_existe.csv`).

**Cómo identificarlo**

- Desde la raíz del proyecto, ejecuta:
  ```bash
  make help  # si tienes target de ayuda
  make train
  ```
- Observa los comandos reales que se ejecutan y compáralos con:
  - La estructura de carpetas (`data/raw`, `configs/config.yaml`).
  - El CLI real (como `src/bankchurn/cli.py` en BankChurn).

**Cómo corregirlo**

- Ajusta el `Makefile` para que:
  - Use rutas reales (`data/raw/Churn.csv`, etc.).
  - Delegue en el CLI real (`python main.py ...` o `python -m miproyecto.cli ...`).
- Mantén el `Makefile` como **fachada del developer experience**: pocos comandos (`install`, `test`, `train`, `serve`) pero sólidos.

---

### 5) Patrón general de debugging de estructura

1. **Revisa el árbol de directorios** contra la plantilla de este módulo.
2. **Comprueba imports** corriendo un `python -c` que importe tu paquete.
3. **Ejecuta los comandos principales** (`make install`, `make test`, `make train`, `make serve`).
4. **Asegura que datos/artefactos no están en Git** y que `.gitignore` los protege.

Este checklist de estructura es lo primero que un revisor Senior mira cuando abre un repo ML: si esto está bien, todo lo demás es mucho más fácil de mantener.

---

## 💼 Consejos Profesionales

> **Recomendaciones para destacar en entrevistas y proyectos reales**

### Para Entrevistas

1. **Explica tu estructura**: Los entrevistadores valoran que puedas justificar cada carpeta y archivo de tu proyecto.

2. **Cookiecutter es tu amigo**: Menciona que usas plantillas estandarizadas para consistencia entre proyectos.

3. **Conoce la diferencia `src/` vs flat**: Explica por qué `src/` layout previene imports accidentales del código local.

### Para Proyectos Reales

| Situación | Consejo |
|-----------|---------|
| Proyecto nuevo | Usa cookiecutter-data-science o similar como base |
| Equipo grande | Documenta convenciones en CONTRIBUTING.md |
| Monorepo vs Multirepo | Monorepo para proyectos relacionados, multirepo para independientes |
| Configs | Nunca hardcodees: usa archivos YAML + variables de entorno |

### Checklist de Proyecto Profesional

- [ ] README.md con badges, instalación, y uso rápido
- [ ] pyproject.toml con metadata completa
- [ ] Makefile con comandos estándar (install, test, lint)
- [ ] .pre-commit-config.yaml para calidad automática
- [ ] tests/ con estructura que refleja src/


---

## 📺 Recursos Externos Recomendados

> Ver [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) para la lista completa.

| 🏷️ | Recurso | Tipo |
|:--:|:--------|:-----|
| 🔴 | [Python Project Structure - ArjanCodes](https://www.youtube.com/watch?v=e8IIYRMnxcE) | Video |
| 🟡 | [src Layout - Packaging Guide](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) | Docs |

---

## 🔗 Referencias del Glosario

Ver [21_GLOSARIO.md](21_GLOSARIO.md) para definiciones de:
- **src/ Layout**: Estructura de proyecto profesional
- **pyproject.toml**: Archivo de configuración moderno
- **Makefile**: Automatización de comandos

---

## 📋 Plantillas Relacionadas

Ver [templates/](templates/index.md) para plantillas listas:
- [pyproject_template.toml](templates/pyproject_template.toml) — Configuración de paquete Python
- [README_TEMPLATE.md](templates/README_TEMPLATE.md) — README profesional
- [Makefile](templates/Makefile) — Automatización de tareas

---

## ✅ Ejercicios

Ver [EJERCICIOS.md](EJERCICIOS.md) - Módulo 03:
- **3.1**: Crear estructura de proyecto
- **3.2**: Configurar pyproject.toml

**Ejercicio rápido:**
```bash
mkdir -p mi-proyecto/{src/miproyecto,app,tests,configs,data/raw,artifacts,scripts,docs}
touch mi-proyecto/src/__init__.py mi-proyecto/src/miproyecto/__init__.py
touch mi-proyecto/tests/__init__.py mi-proyecto/README.md
```

---

<div align="center">

[← Diseño de Sistemas](02_DISENO_SISTEMAS.md) | [Siguiente: Entornos →](04_ENTORNOS.md)

</div>
