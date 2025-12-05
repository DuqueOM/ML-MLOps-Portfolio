# ════════════════════════════════════════════════════════════════════════════════
# MÓDULO 03: ENTORNOS PROFESIONALES
# Virtualenv vs Conda vs Poetry vs Docker: Análisis Comparativo
# Guía MLOps v5.0: Senior Edition | DuqueOM | Noviembre 2025
# ════════════════════════════════════════════════════════════════════════════════

<div align="center">

# 🔧 MÓDULO 03: Entornos Profesionales

### El Arte de la Reproducibilidad a Nivel de Dependencias

*"'Funciona en mi máquina' es la excusa más cara de la industria."*

| Duración             | Teoría               | Práctica             |
| :------------------: | :------------------: | :------------------: |
| **4-5 horas**        | 30%                  | 70%                  |

</div>

---

## 🎯 ADR de Inicio: ¿Por Qué Importan los Entornos?

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ADR-005: Gestión de Entornos como Práctica Obligatoria                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  CONTEXTO:                                                                    ║
║  El 30% de bugs en producción ML se deben a diferencias de versiones          ║
║  entre desarrollo y producción (Google ML Engineering Best Practices).        ║
║                                                                               ║
║  DECISIÓN:                                                                    ║
║  Todo proyecto DEBE tener un sistema de gestión de dependencias con           ║
║  versiones pinneadas y un método documentado de reproducir el entorno.        ║
║                                                                               ║
║  CONSECUENCIAS:                                                               ║
║  (+) Reproducibilidad garantizada entre máquinas                              ║
║  (+) Onboarding de nuevos desarrolladores en minutos, no días                 ║
║  (+) CI/CD confiable (mismas versiones siempre)                               ║
║  (-) Setup inicial requiere más tiempo                                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### Lo Que Lograrás en Este Módulo

1. **Entender** las diferencias entre venv, Conda, Poetry y Docker
2. **Elegir** la herramienta correcta según tu proyecto
3. **Configurar** un entorno profesional con lockfiles
4. **Integrar** el entorno con CI/CD

### 🧩 Cómo se aplica en este portafolio

- En **BankChurn-Predictor**, **CarVision-Market-Intelligence** y
  **TelecomAI-Customer-Intelligence** ya encontrarás:
  - Ficheros `requirements-core.txt`, `requirements.in` y `requirements.txt` para gestionar
    dependencias de forma reproducible.
  - Un `Makefile` con targets como `install`, `test` y `serve` que asumen un entorno activo.
  - Archivos `docker-compose.demo.yml` y `docker-compose.yml` que levantan el stack completo
    (APIs, MLflow, dashboards).
- Usa este módulo para entender **por qué** esas piezas existen y cómo recrear el mismo entorno
  desde cero en tu máquina o en CI/CD.

---

## 3.1 El Problema: "Funciona en Mi Máquina"

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         😱 EL HORROR DE LAS DEPENDENCIAS                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   ESCENARIO TÍPICO:                                                           ║
║                                                                               ║
║   Developer A (laptop):                                                       ║
║   • Python 3.11.4                                                             ║
║   • scikit-learn 1.3.0                                                        ║
║   • pandas 2.0.3                                                              ║
║   • numpy 1.24.3                                                              ║
║   → "Todo funciona perfecto" ✅                                               ║
║                                                                               ║
║   Developer B (otra laptop):                                                  ║
║   • Python 3.9.7                                                              ║
║   • scikit-learn 1.0.2                                                        ║
║   • pandas 1.4.0                                                              ║
║   • numpy 1.21.0                                                              ║
║   → "AttributeError: module 'sklearn' has no attribute 'X'" ❌                ║
║                                                                               ║
║   Servidor de producción:                                                     ║
║   • Python 3.8.10                                                             ║
║   • Versiones "whatever pip installed"                                        ║
║   → CRASH EN PRODUCCIÓN 💥                                                    ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### Las 4 Capas de Reproducibilidad

```mermaid
flowchart TB
    subgraph L4["🐳 NIVEL 4: Contenedor"]
        D[Docker/Podman]
    end
    
    subgraph L3["📦 NIVEL 3: Gestor de Paquetes"]
        C[Poetry / pip-tools / Conda]
    end
    
    subgraph L2["🔒 NIVEL 2: Entorno Virtual"]
        B[venv / virtualenv / conda env]
    end
    
    subgraph L1["🐍 NIVEL 1: Versión Python"]
        A[pyenv / conda / asdf]
    end
    
    L1 --> L2 --> L3 --> L4
    
    style L1 fill:#ffecb3
    style L2 fill:#c8e6c9
    style L3 fill:#bbdefb
    style L4 fill:#e1bee7
```

---

## 3.2 Comparativa de Herramientas

### Matriz de Decisión

| Criterio | venv + pip | Conda | Poetry | Docker Dev |
| :------- | :--------: | :---: | :----: | :--------: |
| **Simplicidad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Reproducibilidad** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Deps no-Python** | ❌ | ✅ | ❌ | ✅ |
| **Lockfile nativo** | ❌ (req pip-tools) | ❌ | ✅ | N/A |
| **Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **CI/CD friendly** | ✅ | ⚠️ | ✅ | ✅ |
| **Espacio disco** | Bajo | Alto | Bajo | Medio-Alto |
| **Curva aprendizaje** | Baja | Media | Baja | Media |

### ¿Cuándo Usar Cada Uno?

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    GUÍA DE SELECCIÓN DE HERRAMIENTA                           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  USA venv + pip-tools SI:                                                     ║
║  • Proyecto simple, solo dependencias Python                                  ║
║  • Equipo pequeño, ya conoce pip                                              ║
║  • CI/CD en GitHub Actions (pip es más rápido)                                ║
║  • No necesitas lockfile sofisticado                                          ║
║                                                                               ║
║  USA Conda SI:                                                                ║
║  • Necesitas librerías con dependencias C/C++ (CUDA, MKL, OpenCV)             ║
║  • Trabajas en Data Science pesado (numpy, scipy optimizados)                 ║
║  • Tu equipo ya usa Conda                                                     ║
║  • Necesitas múltiples versiones de Python fácilmente                         ║
║                                                                               ║
║  USA Poetry SI:                                                               ║
║  • Proyecto serio que necesita reproducibilidad exacta                        ║
║  • Quieres publicar en PyPI                                                   ║
║  • Valoras lockfiles y dependency resolution robusta                          ║
║  • Equipo moderno que aprecia herramientas bien diseñadas                     ║
║                                                                               ║
║  USA Docker Dev Containers SI:                                                ║
║  • Reproducibilidad TOTAL es crítica                                          ║
║  • Múltiples servicios (DB, Redis, etc.) en desarrollo                        ║
║  • Onboarding debe ser "clone & run"                                          ║
║  • Equipo usa VS Code con extensión Dev Containers                            ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## 3.3 Opción 1: venv + pip-tools (Simple y Efectivo)

### Setup Básico

```bash
# Crear entorno virtual
python3.11 -m venv .venv

# Activar
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar pip-tools para lockfiles
pip install pip-tools
```

### Estructura de Archivos

```
project/
├── requirements.in        # Dependencias directas (lo que escribes)
├── requirements.txt       # Lockfile generado (no editar manualmente)
├── requirements-dev.in    # Dependencias de desarrollo
├── requirements-dev.txt   # Lockfile de desarrollo
└── .python-version        # Versión de Python (para pyenv)
```

### requirements.in (Lo que escribes)

```
# requirements.in - Dependencias directas
# Solo especifica las que usas directamente, pip-tools resuelve el resto

pandas>=2.0.0,<3.0.0
scikit-learn>=1.3.0
pydantic>=2.0.0
fastapi>=0.100.0
mlflow>=2.8.0
pyyaml>=6.0
```

### Generar Lockfile

```bash
# Genera requirements.txt con TODAS las versiones exactas
pip-compile requirements.in --output-file=requirements.txt

# Para desarrollo
pip-compile requirements-dev.in --output-file=requirements-dev.txt

# Instalar desde lockfile
pip-sync requirements.txt requirements-dev.txt
```

### requirements.txt Generado (NO EDITAR)

```
# This file is autogenerated by pip-compile with Python 3.11
# Do not edit manually.

annotated-types==0.6.0
    # via pydantic
anyio==4.0.0
    # via
    #   httpx
    #   starlette
certifi==2023.11.17
    # via httpx
fastapi==0.104.1
    # via -r requirements.in
numpy==1.26.2
    # via
    #   pandas
    #   scikit-learn
pandas==2.1.3
    # via -r requirements.in
pydantic==2.5.2
    # via
    #   -r requirements.in
    #   fastapi
# ... etc (versiones EXACTAS)
```

### Makefile para Automatización

```makefile
# Makefile
.PHONY: venv install lock sync clean

PYTHON := python3.11
VENV := .venv
BIN := $(VENV)/bin

venv:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip pip-tools

lock: venv
	$(BIN)/pip-compile requirements.in -o requirements.txt
	$(BIN)/pip-compile requirements-dev.in -o requirements-dev.txt

sync: venv
	$(BIN)/pip-sync requirements.txt requirements-dev.txt

install: venv lock sync

clean:
	rm -rf $(VENV)
	rm -f requirements.txt requirements-dev.txt
```

---

## 3.4 Opción 2: Poetry (Moderno y Robusto)

### Instalación

```bash
# Instalar Poetry (método oficial)
curl -sSL https://install.python-poetry.org | python3 -

# Verificar
poetry --version
```

### Inicializar Proyecto

```bash
# En proyecto existente
poetry init

# O crear nuevo proyecto
poetry new bankchurn-predictor
```

### pyproject.toml Completo

```toml
[tool.poetry]
name = "bankchurn"
version = "0.1.0"
description = "Predictor de churn bancario con MLOps"
authors = ["Tu Nombre <tu@email.com>"]
readme = "README.md"
packages = [{include = "bankchurn", from = "src"}]

[tool.poetry.dependencies]
python = "^3.10"
pandas = "^2.0.0"
scikit-learn = "^1.3.0"
pydantic = "^2.0.0"
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
mlflow = "^2.8.0"
pyyaml = "^6.0"
joblib = "^1.3.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
mypy = "^1.6.0"
ruff = "^0.1.0"
pre-commit = "^3.5.0"
ipython = "^8.0.0"

[tool.poetry.group.docs.dependencies]
mkdocs = "^1.5.0"
mkdocs-material = "^9.4.0"

[tool.poetry.scripts]
bankchurn-train = "bankchurn.cli:train"
bankchurn-predict = "bankchurn.cli:predict"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

# ════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE HERRAMIENTAS
# ════════════════════════════════════════════════════════════════════

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "W", "B", "C4", "UP"]
ignore = ["E501"]
src = ["src"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
disallow_untyped_defs = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=src/bankchurn --cov-report=term-missing"

[tool.coverage.run]
source = ["src"]
omit = ["tests/*"]
```

### Comandos Esenciales

```bash
# Instalar dependencias (crea poetry.lock automáticamente)
poetry install

# Añadir dependencia
poetry add pandas
poetry add --group dev pytest

# Actualizar dependencias
poetry update

# Ejecutar comando en el entorno
poetry run python src/bankchurn/main.py
poetry run pytest

# Activar shell en el entorno
poetry shell

# Exportar a requirements.txt (para Docker)
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Build del paquete
poetry build
```

### poetry.lock (Generado Automáticamente)

El archivo `poetry.lock` contiene TODAS las versiones exactas de TODAS las dependencias (directas y transitivas). **SIEMPRE** commitear este archivo.

---

## 3.5 Opción 3: Conda (Para Data Science Pesado)

### Cuándo Conda es la Mejor Opción

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         ✅ USA CONDA SI NECESITAS:                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   • CUDA / cuDNN para GPU computing                                           ║
║   • NumPy/SciPy compilados con MKL (Intel) o OpenBLAS optimizado              ║
║   • OpenCV con dependencias de sistema                                        ║
║   • R + Python en el mismo entorno                                            ║
║   • Librerías geoespaciales (GDAL, GEOS, PROJ)                                ║
║   • Dependencias de sistema que pip no puede instalar                         ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### environment.yml

```yaml
# environment.yml
name: bankchurn
channels:
  - conda-forge  # Preferir conda-forge sobre defaults
  - defaults

dependencies:
  # Python version
  - python=3.11
  
  # Core data science (optimizados con MKL)
  - numpy=1.26.*
  - pandas=2.1.*
  - scikit-learn=1.3.*
  
  # Si necesitas GPU
  # - pytorch
  # - cudatoolkit=11.8
  
  # Dependencias que tienen componentes C
  - pyyaml
  - joblib
  
  # pip dependencies (las que no están en conda o prefieres de PyPI)
  - pip
  - pip:
    - pydantic>=2.0.0
    - fastapi>=0.104.0
    - uvicorn>=0.24.0
    - mlflow>=2.8.0
    - pytest>=7.4.0
    - mypy>=1.6.0
    - ruff>=0.1.0
```

### Comandos Conda

```bash
# Crear entorno desde archivo
conda env create -f environment.yml

# Activar
conda activate bankchurn

# Exportar entorno exacto (para reproducibilidad)
conda env export > environment-lock.yml

# Exportar solo dependencias explícitas
conda env export --from-history > environment.yml

# Actualizar entorno
conda env update -f environment.yml --prune

# Listar entornos
conda env list

# Eliminar entorno
conda env remove -n bankchurn
```

### Mamba: Conda Acelerado

```bash
# Instalar mamba (resolver mucho más rápido)
conda install -c conda-forge mamba

# Usar mamba en lugar de conda
mamba env create -f environment.yml
mamba install numpy
```

---

## 3.6 Opción 4: Docker Dev Containers

### ¿Por Qué Docker para Desarrollo?

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                       DOCKER DEV CONTAINERS: PROS/CONS                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   ✅ PROS:                                                                    ║
║   • Reproducibilidad TOTAL (mismo OS, mismas versiones de todo)               ║
║   • Onboarding = "git clone && code ." (con VS Code Dev Containers)           ║
║   • Mismo entorno en dev, CI y producción                                     ║
║   • Puedes incluir servicios (PostgreSQL, Redis, MLflow server)               ║
║                                                                               ║
║   ❌ CONS:                                                                    ║
║   • Overhead de Docker (memoria, CPU)                                         ║
║   • Más complejo de configurar inicialmente                                   ║
║   • Debugging puede ser más difícil                                           ║
║   • Performance de I/O en volúmenes (especialmente macOS)                     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### .devcontainer/devcontainer.json

```json
{
    "name": "BankChurn Dev",
    "dockerComposeFile": "docker-compose.yml",
    "service": "app",
    "workspaceFolder": "/workspace",
    
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "charliermarsh.ruff",
                "ms-toolsai.jupyter",
                "redhat.vscode-yaml",
                "GitHub.copilot"
            ],
            "settings": {
                "python.defaultInterpreterPath": "/workspace/.venv/bin/python",
                "python.formatting.provider": "none",
                "editor.formatOnSave": true,
                "[python]": {
                    "editor.defaultFormatter": "charliermarsh.ruff"
                }
            }
        }
    },
    
    "postCreateCommand": "make install",
    
    "forwardPorts": [8000, 5000, 3000],
    
    "remoteUser": "vscode"
}
```

### .devcontainer/docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build:
      context: ..
      dockerfile: .devcontainer/Dockerfile
    volumes:
      - ..:/workspace:cached
      - venv:/workspace/.venv
    environment:
      - PYTHONDONTWRITEBYTECODE=1
      - PYTHONUNBUFFERED=1
    command: sleep infinity
    
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.8.0
    ports:
      - "5000:5000"
    volumes:
      - mlflow-data:/mlflow
    command: mlflow server --host 0.0.0.0 --backend-store-uri sqlite:///mlflow/mlflow.db --default-artifact-root /mlflow/artifacts
    
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: bankchurn
      POSTGRES_PASSWORD: bankchurn
      POSTGRES_DB: bankchurn
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  venv:
  mlflow-data:
  postgres-data:
```

### .devcontainer/Dockerfile

```dockerfile
FROM python:3.11-slim

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Usuario no-root
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# Workspace
WORKDIR /workspace

# Cambiar a usuario no-root
USER $USERNAME

# Pre-instalar pip-tools
RUN pip install --user pip-tools

ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"
```

---

## 3.7 Integración con CI/CD

### GitHub Actions con pip

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'  # Cachea dependencias
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: pytest tests/ -v --cov
```

### GitHub Actions con Poetry

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: 1.7.0
          virtualenvs-create: true
          virtualenvs-in-project: true
      
      - name: Load cached venv
        uses: actions/cache@v3
        with:
          path: .venv
          key: venv-${{ runner.os }}-${{ hashFiles('poetry.lock') }}
      
      - name: Install dependencies
        run: poetry install --no-interaction
      
      - name: Run tests
        run: poetry run pytest tests/ -v --cov
```

---

## 🧨 Errores habituales y cómo depurarlos en entornos

Los problemas de este módulo se manifiestan como **inconsistencias entre máquinas**: algo funciona en tu laptop pero no en el servidor, o en CI. Aquí van los patrones más frecuentes y cómo atacarlos.

### 1) Entorno virtual mal activado (`pip` instala en el sitio equivocado)

**Síntomas típicos**

- Ejecutas `pip install` y luego `python -c "import pandas"` y obtienes `ModuleNotFoundError`.
- Tienes varias versiones de Python (`python`, `python3`, `pyenv`, Conda) y no sabes cuál está usando tu proyecto.
- En CI funciona con una versión de paquete y en local con otra.

**Cómo identificarlo**

- Ejecuta:
  ```bash
  which python
  python -m pip --version
  ```
  y verifica que ambos apuntan al **mismo entorno** (`.venv/bin/python`, por ejemplo).
- En Windows, revisa la ruta de `Scripts` y que estés en el entorno correcto (`(.venv)` en el prompt).

**Cómo corregirlo**

- Usa siempre `python -m pip` en lugar de `pip` a secas:
  ```bash
  python -m pip install -r requirements.txt
  ```
- Documenta en el README/Makefile **cómo activar el entorno** (`source .venv/bin/activate`, `poetry shell`, `conda activate ...`).
- Si usas `.python-version` con `pyenv`, asegúrate de que coincide con la versión definida en `pyproject.toml` o `environment.yml`.

---

### 2) Lockfiles ignorados (`requirements.txt` / `poetry.lock` / `environment-lock.yml`)

**Síntomas típicos**

- Dos personas hacen `pip install -r requirements.txt` y obtienen versiones distintas de las mismas librerías.
- En tu máquina funciona con `pandas==2.0.3` pero en producción falla con `pandas==2.2.0`.
- `poetry.lock` o `requirements-dev.txt` no están commiteados.

**Cómo identificarlo**

- Revisa el repositorio:
  - ¿Existe `requirements.txt` generado por pip-tools y está en Git?
  - ¿Existe `poetry.lock` y está versionado?
  - ¿Hay algún `environment-lock.yml` de Conda?
- Compara lo que dice el lockfile con lo que tienes instalado:
  ```bash
  pip freeze | grep pandas
  ```

**Cómo corregirlo**

- **Siempre** commitea el lockfile (requirements.txt, poetry.lock, environment-lock.yml).
- Define una única fuente de verdad: si usas pip-tools, no edites `requirements.txt` a mano, solo `requirements.in`.
- En CI, instala **desde el lockfile**, no desde las dependencias sueltas.

---

### 3) Mezclar gestores (pip + Conda + Poetry + Docker) sin una estrategia clara

**Síntomas típicos**

- Instalas algo con `conda install` y luego con `pip install` y el entorno se rompe.
- Tienes `environment.yml`, `requirements.txt` y `pyproject.toml` en el mismo proyecto sin que ninguno esté claro.
- El contenedor Docker instala versiones diferentes a las de tu entorno local.

**Cómo identificarlo**

- Lista tus archivos de configuración: ¿hay más de un gestor activo a la vez?
- Revisa el `Dockerfile`: ¿instala desde `requirements.txt`, desde `pyproject.toml` exportado o desde `environment.yml`?

**Cómo corregirlo**

- Elige un **flujo principal** por proyecto:
  - pip-tools → `requirements.in` → `requirements.txt` → Docker/CI.
  - Poetry → `pyproject.toml` + `poetry.lock` → export a `requirements.txt` solo para Docker.
  - Conda → `environment.yml`/`environment-lock.yml` → `conda env create` en todas partes.
- Documenta en este módulo (y en el README del proyecto) **qué gestor es el canónico** y qué archivos deben editarse.

---

### 4) CI instala un entorno distinto al local

**Síntomas típicos**

- En local todo pasa, pero en GitHub Actions los tests fallan por versiones de librerías.
- Ves que en CI se instala directamente con `pip install -r requirements.txt` pero en local usas Poetry o Conda.

**Cómo identificarlo**

- Abre el workflow (`.github/workflows/*.yml`) y verifica:
  - ¿Está usando la misma versión de Python que tú?
  - ¿Instala dependencias desde los mismos archivos (`requirements.txt`, `poetry.lock`, `environment.yml`)?

**Cómo corregirlo**

- Alinea CI con tu flujo local:
  - pip-tools: usa el snippet de "GitHub Actions con pip" de este módulo.
  - Poetry: usa el bloque de "GitHub Actions con Poetry" y cachea `.venv`.
  - Conda: usa `conda env create -f environment.yml` o `mamba`.
- Haz al menos una vez la prueba de **clonar en limpio** y seguir los pasos de CI en tu máquina; esto detecta diferencias.

---

### 5) Docker que no refleja el entorno real

**Síntomas típicos**

- La aplicación en Docker falla con `ImportError` o con versiones diferentes de librerías.
- Tu `Dockerfile` instala con `pip install pandas scikit-learn ...` en lugar de usar el lockfile.

**Cómo identificarlo**

- Revisa el `Dockerfile` (y `.devcontainer/Dockerfile` si aplica):
  - ¿Copia `requirements.txt` o usa `poetry export` antes de instalar?
  - ¿Especifica la misma versión de Python que usas localmente?

**Cómo corregirlo**

- Haz que Docker **derive** de tu configuración de entorno:
  - Con pip-tools: `COPY requirements.txt` → `pip install -r requirements.txt`.
  - Con Poetry: `poetry export -f requirements.txt --output requirements.txt` y usa eso en la imagen.
- Mantén la versión de Python del contenedor alineada con tu `.python-version` / `pyproject.toml` / `environment.yml`.

---

### Patrón general de debugging de entornos

1. **Congela la versión de Python**: pyenv, Conda o imagen base de Docker clara.
2. **Define un único gestor principal** (pip-tools, Poetry o Conda) y sigue su flujo.
3. **Asegúrate de que CI y Docker consumen el mismo lockfile**.
4. **Verifica el entorno activado** antes de instalar o ejecutar (`which python`, `python -m pip`).

Con este patrón, "funciona en mi máquina" se convierte en "funciona en cualquier máquina que siga estos pasos".

---

## 3.8 Ejercicio Práctico: Configura Tu Entorno

### Opción A: pip-tools (Recomendado para empezar)

```bash
# 1. Crear estructura
mkdir -p bankchurn-predictor && cd bankchurn-predictor

# 2. Crear archivos
cat > requirements.in << 'EOF'
pandas>=2.0.0
scikit-learn>=1.3.0
pydantic>=2.0.0
fastapi>=0.104.0
uvicorn>=0.24.0
mlflow>=2.8.0
pyyaml>=6.0
joblib>=1.3.0
EOF

cat > requirements-dev.in << 'EOF'
-r requirements.in
pytest>=7.4.0
pytest-cov>=4.1.0
mypy>=1.6.0
ruff>=0.1.0
pre-commit>=3.5.0
EOF

# 3. Crear entorno y lockfiles
python3.11 -m venv .venv
source .venv/bin/activate
pip install pip-tools
pip-compile requirements.in
pip-compile requirements-dev.in
pip-sync requirements.txt requirements-dev.txt

# 4. Verificar
python -c "import pandas; print(pandas.__version__)"
```

### Opción B: Poetry

```bash
# 1. Crear proyecto
poetry new bankchurn-predictor --src
cd bankchurn-predictor

# 2. Añadir dependencias
poetry add pandas scikit-learn pydantic fastapi uvicorn mlflow pyyaml joblib
poetry add --group dev pytest pytest-cov mypy ruff pre-commit

# 3. Instalar
poetry install

# 4. Verificar
poetry run python -c "import pandas; print(pandas.__version__)"
```

### Checklist de Verificación

```
[ ] Entorno virtual creado y activable
[ ] Lockfile generado con versiones exactas
[ ] Lockfile commiteado en Git
[ ] Puedo recrear el entorno desde cero
[ ] CI puede instalar las mismas versiones
```

---

## 3.9 Autoevaluación

### Checklist de Competencias

```
CONCEPTOS:
[ ] Entiendo la diferencia entre dependencias directas y transitivas
[ ] Sé qué es un lockfile y por qué es importante
[ ] Puedo explicar cuándo usar Conda vs pip vs Poetry

pip-tools:
[ ] Puedo crear requirements.in con restricciones de versión
[ ] Sé usar pip-compile y pip-sync
[ ] Entiendo el formato del lockfile generado

Poetry:
[ ] Puedo crear un pyproject.toml funcional
[ ] Sé añadir dependencias y grupos de dependencias
[ ] Puedo exportar a requirements.txt para Docker

CI/CD:
[ ] Puedo configurar caching de dependencias en GitHub Actions
[ ] Sé cómo asegurar reproducibilidad en CI
```

### Preguntas de Reflexión

1. ¿Por qué no basta con `pip install pandas` sin especificar versión?
2. ¿Cuál es la diferencia entre `requirements.in` y `requirements.txt`?
3. ¿Cuándo preferirías Conda sobre Poetry?
4. ¿Por qué es importante cachear dependencias en CI?

---

## 📦 Cómo se Usó en el Portafolio

Cada proyecto del portafolio implementa la gestión de entornos descrita:

### pyproject.toml Real

```toml
# BankChurn-Predictor/pyproject.toml (extracto)
[project]
name = "bankchurn"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "pandas>=2.0.0",
    "scikit-learn>=1.3.0",
    "pydantic>=2.5.0",
    "mlflow>=2.9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.9",
]
```

### Comandos Make del Portafolio

Todos los proyectos tienen Makefile con comandos consistentes:

```makefile
# Comandos disponibles en los 3 proyectos
make install     # pip install -e ".[dev]"
make test        # pytest con coverage
make lint        # ruff check
make train       # Entrena el modelo
make serve       # Inicia API FastAPI
```

### Estructura de Dependencias

| Proyecto | Archivo | Dependencias Core |
|----------|---------|-------------------|
| BankChurn | `pyproject.toml` | pandas, sklearn, pydantic, mlflow |
| CarVision | `pyproject.toml` | pandas, sklearn, pydantic, pyyaml |
| TelecomAI | `pyproject.toml` | pandas, sklearn, pydantic |

### 🔧 Ejercicio: Instala un Proyecto Real

```bash
# 1. Ve a BankChurn
cd BankChurn-Predictor

# 2. Crea entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Instala con dependencias de desarrollo
pip install -e ".[dev]"

# 4. Verifica que funciona
python -c "from bankchurn.config import BankChurnConfig; print('OK')"
make test
```

---

## 💼 Consejos Profesionales

> **Recomendaciones para destacar en entrevistas y proyectos reales**

### Para Entrevistas

1. **"¿Cómo manejas dependencias?"**: Explica pip-tools, Poetry, o uv. Menciona lock files y reproducibilidad.

2. **Containers vs Virtualenvs**: Conoce cuándo usar cada uno (dev local vs producción).

3. **DevContainers**: Menciona que usas VS Code DevContainers para entornos reproducibles.

### Para Proyectos Reales

| Situación | Consejo |
|-----------|---------|
| Conflictos de dependencias | Usa pip-compile para resolver y fijar versiones |
| CI/CD | Usa la misma imagen Docker en local y CI |
| Múltiples versiones de Python | pyenv + tox para testing multi-versión |
| Dependencias de sistema | Documenta en Dockerfile o README |

### Herramientas Modernas

- **uv**: Reemplazo rápido de pip (10-100x más rápido)
- **pip-tools**: pip-compile + pip-sync para reproducibilidad
- **Poetry**: Gestión completa de dependencias y publicación
- **Conda**: Para dependencias científicas complejas (CUDA, etc.)


---

## 📺 Recursos Externos Recomendados

> Ver [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) para la lista completa.

| 🏷️ | Recurso | Tipo |
|:--:|:--------|:-----|
| 🔴 | [Python Virtual Environments - Corey Schafer](https://www.youtube.com/watch?v=Kg1Yvry_Ydk) | Video |
| 🟡 | [pip-tools Tutorial](https://www.youtube.com/watch?v=LAig6s9Hkj0) | Video |

---

## 🔗 Referencias del Glosario

Ver [21_GLOSARIO.md](21_GLOSARIO.md) para definiciones de:
- **venv**: Entornos virtuales de Python
- **pip-tools**: Gestión de dependencias
- **pyproject.toml**: Configuración de proyecto moderno

---

## ✅ Ejercicios

Ver [EJERCICIOS.md](EJERCICIOS.md) - Módulo 04:
- **4.1**: Crear entorno virtual
- **4.2**: Configurar pip-tools

---

## 🔜 Siguiente Paso

Con el entorno configurado, es hora de dominar **Git profesionalmente**.

**[Ir a Módulo 05: Git Profesional →](05_GIT_PROFESIONAL.md)**

---

<div align="center">

[← Estructura de Proyecto](03_ESTRUCTURA_PROYECTO.md) | [Siguiente: Git Profesional →](05_GIT_PROFESIONAL.md)

</div>
