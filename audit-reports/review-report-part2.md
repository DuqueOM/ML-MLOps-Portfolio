## 📂 Análisis Archivo por Archivo

### Archivos en Raíz del Monorepo

| Archivo | Propósito | Estado | Issues | Recomendación | Prioridad |
|---------|-----------|--------|--------|---------------|-----------|
| `.gitignore` | Ignorar archivos temporales | ⚠️ Warning | Incompleto: falta coverage/, .env, OS files | Extender con patrón estándar Python | P0 |
| `.pre-commit-config.yaml` | Hooks de calidad de código | ✅ OK | Bien configurado (black, isort, flake8, mypy) | Agregar bandit para seguridad | P1 |
| `README.md` | Documentación principal | ✅ OK | Completo y bien estructurado | Agregar badges de CI status | P2 |
| `README_PORTFOLIO.md` | Versión portfolio | ⚠️ Warning | Duplica contenido de README.md | Consolidar o eliminar | P2 |
| `common_utils/seed.py` | Gestión de semillas | ✅ OK | Bien implementado, type hints modernos | Ninguna | - |
| `common_utils/__init__.py` | Package marker | ❌ Missing | Archivo no existe | Crear para importabilidad | P1 |
| **LICENSE** | **Licencia del proyecto** | ❌ **ERROR** | **No existe en raíz** | **Agregar MIT license** | **P0** |
| `.env.example` | Ejemplo de variables de entorno | ❌ Missing | No documentadas las env vars | Crear con SEED, MLFLOW_URI, etc. | P0 |
| `CONTRIBUTING.md` | Guía de contribución | ❌ Missing | No existe | Crear con proceso de PR, style guide | P2 |
| `CHANGELOG.md` | Registro de cambios | ❌ Missing | No existe | Crear siguiendo Keep a Changelog | P2 |

### .github/workflows/

| Archivo | Propósito | Estado | Issues | Recomendación | Prioridad |
|---------|-----------|--------|--------|---------------|-----------|
| `ci.yml` | Pipeline CI principal | ✅ OK | Funcional, ejecuta tests en matrix | Agregar cache de dependencias | P2 |
| `cd-bankchurn.yml` | CD para BankChurn | ✅ OK | Build y push a GHCR | Agregar smoke tests post-deploy | P1 |
| `cd-oilwell.yml` | CD para OilWell | ✅ OK | Similar a bankchurn | Estandarizar con template | P2 |
| `cd-telecomai.yml` | CD para TelecomAI | ✅ OK | Incluye K8s deployment | Verificar secrets en K8s | P0 |
| `retrain-bankchurn.yml` | Retraining programado | ✅ OK | Workflow de retraining | Agregar validación de modelo | P1 |
| `dependabot.yml` | Actualización de deps | ❌ Missing | No existe | Crear para GitHub Actions | P1 |

**Issues detectados en workflows:**
- L28-32: Uso de `GITHUB_TOKEN` (OK, es el token automático de GitHub)
- L48-52: Condicional para requirements.in vs requirements.txt es frágil
- Falta job de security scanning (Trivy, Snyk)

### infra/

| Archivo | Propósito | Estado | Issues | Recomendación | Prioridad |
|---------|-----------|--------|--------|---------------|-----------|
| `docker-compose-mlflow.yml` | Stack MLflow completo | 🔴 **ERROR** | **Credenciales hardcoded L9, L20, L38** | **Usar ${VAR} + .env** | **P0** |

**Detalles del problema de seguridad:**
```yaml
# ANTES (INSEGURO):
environment:
  POSTGRES_PASSWORD: mlflow        # ❌
  MINIO_ROOT_PASSWORD: minio123    # ❌
  AWS_SECRET_ACCESS_KEY: minio123  # ❌

# DESPUÉS (SEGURO):
environment:
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}  # ✅
  MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
  AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
```

**Crear `infra/.env.example`:**
```bash
POSTGRES_PASSWORD=your_secure_password_here
MINIO_ROOT_PASSWORD=your_secure_password_here
AWS_SECRET_ACCESS_KEY=your_secure_key_here
```

---

## 📦 Análisis por Proyecto Individual

### BankChurn-Predictor (El más completo)

#### Archivos principales

| Archivo | LOC | Propósito | Estado | Issues | Prioridad |
|---------|-----|-----------|--------|--------|-----------|
| `main.py` | 841 | CLI principal | ✅ OK | Archivo largo, considerar módulos | P2 |
| `app/fastapi_app.py` | ~300 | API de inferencia | ✅ OK | Bien estructurado | - |
| `configs/config.yaml` | ~200 | Configuración | ⚠️ Warning | L189-196: `secrets` con valores null, confuso | P1 |
| `Dockerfile` | ~40 | Contenedor API | ✅ OK | Multi-stage build bueno | - |
| `docker-compose.yml` | ~70 | Orquestación local | ✅ OK | Incluye healthcheck | - |
| `Makefile` | 247 | Automatización | ✅ OK | Completo y documentado | - |
| `requirements.txt` | 3571 | Dependencias | ⚠️ Warning | 255KB con hashes, difícil mantenimiento | P1 |
| `requirements-core.txt` | 18 | Deps mínimas | ✅ OK | Limpio y conciso | - |
| `requirements.in` | ~30 | Deps fuente | ✅ OK | Para pip-compile | - |
| `dvc.yaml` | ~30 | Pipeline DVC | ✅ OK | Define stages train/eval | - |
| `monitoring/check_drift.py` | ~200 | Detección drift | ✅ OK | KS/PSI implementado | - |
| `tests/test_*.py` | ~800 | Tests unitarios | ✅ OK | 5 archivos, cobertura 75% | - |
| `README.md` | 176 | Documentación | ✅ OK | Excelente, muy completo | - |
| `model_card.md` | ~80 | Ficha de modelo | ✅ OK | Sigue plantilla estándar | - |
| `data_card.md` | ~50 | Ficha de datos | ✅ OK | Documenta sesgos | - |

**Observaciones específicas BankChurn:**

1. **main.py** (L1-841):
   - ✅ Buena separación en clases (ResampleClassifier, BankChurnPredictor)
   - ✅ Manejo de argumentos con argparse
   - ⚠️ L83: Type hint moderno `int | None` (requiere Python 3.10+)
   - ⚠️ L70: `warnings.filterwarnings("ignore")` demasiado amplio
   - 💡 Considerar extraer ResampleClassifier a módulo separado

2. **configs/config.yaml**:
   - ⚠️ L189-196: Sección `secrets` confusa (todos null)
   - 💡 Eliminar o documentar claramente que son placeholders

3. **Makefile**:
   - ✅ Excelente documentación inline
   - ✅ Targets útiles: install, test, train, api-start, docker-*
   - ⚠️ L175-213: Target `benchmark` incrustado en Python
   - 💡 Mover benchmark a script separado

4. **Tests**:
   - ✅ `test_data.py`: Validación de esquema
   - ✅ `test_model.py`: Tests de entrenamiento/predicción
   - ✅ `test_fairness.py`: Tests de sesgo demográfico
   - ✅ `test_main_cli.py`: Tests de integración CLI
   - ❌ Falta: Tests E2E con Docker
   - ❌ Falta: Tests de carga API

5. **Documentación**:
   - ✅ Muy completa: README, model_card, data_card, EXECUTIVE_SUMMARY
   - ✅ API_EXAMPLES.md con curl commands
   - ✅ COMMANDS.md con reproducibilidad
   - ❌ Falta: Architecture diagram

### Problemas comunes en TODOS los proyectos

#### 1. Type Hints Inconsistentes

**Problema:** Mezcla de sintaxis Python 3.10+ y legacy

```python
# common_utils/seed.py (3.10+)
def set_seed(seed: Optional[int] = None) -> int:  # ❌ Inconsistente

# Debería ser (consistente 3.10+):
def set_seed(seed: int | None = None) -> int:  # ✅

# O usar __future__ para compatibilidad:
from __future__ import annotations
def set_seed(seed: int | None = None) -> int:  # ✅
```

**Archivos afectados:**
- `common_utils/seed.py` L19
- Todos los `main.py` en varios lugares
- Archivos en `app/`, `monitoring/`, `scripts/`

**Recomendación:**
- Estandarizar a Python 3.10+ sintaxis (`|` en vez de `Union`)
- O agregar `from __future__ import annotations` en todos los archivos

#### 2. Requirements.txt Masivos

**Problema:** Archivos de 255KB con hashes SHA256

```bash
$ wc -l */requirements.txt
  3571 BankChurn-Predictor/requirements.txt
  3200 CarVision-Market-Intelligence/requirements.txt
  ...
```

**Ventaja:** Seguridad supply chain (hash verification)  
**Desventaja:** Diffs imposibles de revisar, conflictos en PRs

**Soluciones:**

**Opción A (Recomendada): Poetry/uv**
```bash
# Migrar a pyproject.toml
cd BankChurn-Predictor
poetry init
poetry add pandas numpy scikit-learn fastapi uvicorn
poetry lock
# Resultado: pyproject.toml (legible) + poetry.lock (con hashes)
```

**Opción B (Mantener pip-compile):**
```bash
# Ya implementado en algunos proyectos
# requirements.in → requirements.txt con pip-compile
pip-compile --generate-hashes requirements.in
# Mantener requirements.in versionado, requirements.txt generado
```

**Opción C (Híbrido):**
```bash
# requirements-core.txt: runtime sin hashes (legible)
# requirements.txt: full con hashes (CI/CD)
```

#### 3. Sin pyproject.toml (Proyectos no instalables)

**Problema:** No se puede `pip install -e .`

**Solución:** Crear `pyproject.toml` en cada proyecto

```toml
# BankChurn-Predictor/pyproject.toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "bankchurn-predictor"
version = "1.0.0"
description = "Bank churn prediction system"
requires-python = ">=3.10"
dependencies = [
    "pandas>=1.3.0",
    "numpy>=1.21.0",
    "scikit-learn>=1.0.0",
    # ... de requirements-core.txt
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=3.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]

[tool.black]
line-length = 120

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-v --cov=. --cov-report=term-missing"

[tool.mypy]
python_version = "3.10"
ignore_missing_imports = true
strict_optional = true
```

**Beneficios:**
- `pip install -e .` funciona
- Centraliza configuración de tools (black, pytest, mypy)
- Facilita publicación a PyPI si es necesario

---

## 🧪 Resultados de Checks Automatizados (Simulados)

> **Nota:** Los siguientes checks se ejecutarían en una máquina con el entorno configurado.
> Aquí se documentan los comandos y resultados esperados.

### 1. Linting (flake8)

```bash
cd BankChurn-Predictor
flake8 . --max-line-length=120 --count --statistics

# Resultado esperado (basado en .flake8):
# 0 errors - Pre-commit mantiene calidad
```

### 2. Type Checking (mypy)

```bash
mypy main.py app/ monitoring/ scripts/ tests/

# Resultado esperado:
# Success: no issues found in XX source files
# (Pre-commit ya ejecuta mypy)
```

### 3. Formatting (black)

```bash
black --check . --line-length=120

# Resultado esperado:
# All done! ✨ 🍰 ✨
# XX files would be left unchanged.
```

### 4. Security Scan (bandit) - NO CONFIGURADO ⚠️

```bash
pip install bandit
bandit -r . -ll

# Resultado esperado:
# [HIGH] hardcoded_password_string en infra/docker-compose-mlflow.yml
# RECOMENDACIÓN: Agregar bandit a pre-commit
```

### 5. Dependency Check (pip-audit) - NO CONFIGURADO ⚠️

```bash
pip install pip-audit
pip-audit

# Checks conocidos CVEs en dependencias
# RECOMENDACIÓN: Ejecutar periódicamente en CI
```

### 6. Tests (pytest)

```bash
cd BankChurn-Predictor
pytest --cov=. --cov-report=term-missing --cov-fail-under=75

# Resultado esperado (según CI):
# Coverage: 75% (threshold met)
# XX passed in XXs
```

### 7. Docker Build

```bash
docker build -t bankchurn:test .

# Resultado esperado:
# Successfully built XXX
# Successfully tagged bankchurn:test
```

### 8. Smoke Test

```bash
python main.py --mode train --config configs/config.yaml --seed 42 --input data/raw/Churn.csv

# Resultado esperado:
# Training completed
# Model saved to models/best_model.pkl
# Metrics: F1=0.XX, AUC=0.XX
```

---

## 🔐 Reporte de Seguridad

### Secrets Encontrados

| Archivo | Línea | Tipo | Severidad | Remediación |
|---------|-------|------|-----------|-------------|
| `infra/docker-compose-mlflow.yml` | 9 | Password | 🔴 Alta | Usar ${POSTGRES_PASSWORD} + .env |
| `infra/docker-compose-mlflow.yml` | 20 | Password | 🔴 Alta | Usar ${MINIO_ROOT_PASSWORD} + .env |
| `infra/docker-compose-mlflow.yml` | 38 | API Key | 🔴 Alta | Usar ${AWS_SECRET_ACCESS_KEY} + .env |

### Pasos de Remediación

```bash
# 1. Crear .env en infra/
cat > infra/.env << EOF
POSTGRES_PASSWORD=$(openssl rand -base64 32)
MINIO_ROOT_PASSWORD=$(openssl rand -base64 32)
AWS_SECRET_ACCESS_KEY=$(openssl rand -base64 32)
EOF

# 2. Actualizar docker-compose-mlflow.yml
# Ver fixes/0001-remove-hardcoded-credentials.patch

# 3. Asegurar que .env está en .gitignore
echo "infra/.env" >> .gitignore

# 4. Crear .env.example para documentación
cp infra/.env infra/.env.example
# Reemplazar valores reales con placeholders
```

### Vulnerabilidades Potenciales en Dependencias

**Recomendación:** Ejecutar `pip-audit` regularmente

```bash
pip install pip-audit
pip-audit -r requirements.txt

# Alternativamente: Safety
pip install safety
safety check -r requirements.txt
```

### Mejoras de Seguridad Recomendadas

1. **Agregar bandit a pre-commit**
```yaml
# .pre-commit-config.yaml
- repo: https://github.com/PyCQA/bandit
  rev: '1.7.5'
  hooks:
    - id: bandit
      args: ['-ll', '-i']
```

2. **Configurar Dependabot**
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/BankChurn-Predictor"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

3. **Secrets Scanning en CI**
```yaml
# .github/workflows/security.yml
- name: TruffleHog Secrets Scan
  uses: trufflesecurity/trufflehog@main
  with:
    path: ./
    base: ${{ github.event.repository.default_branch }}
```

---

## 📖 Guía de Reproducibilidad en Máquina Limpia

### Prerequisitos

- OS: Ubuntu 22.04 / macOS / Windows WSL2
- Python: 3.10+
- Git
- Docker (opcional, para deploy)
- Make (opcional, facilita comandos)

### Setup Paso a Paso (BankChurn como ejemplo)

```bash
# 1. Clonar repositorio
git clone https://github.com/DuqueOM/Portafolio-ML-MLOps.git
cd "Projects Tripe Ten"

# 2. Crear entorno virtual
python3.10 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# 3. Actualizar pip
pip install --upgrade pip

# 4. Navegar al proyecto deseado
cd BankChurn-Predictor

# 5. Instalar dependencias
pip install -r requirements-core.txt

# 6. Verificar instalación
python -c "import pandas, numpy, sklearn, fastapi; print('OK')"

# 7. Descargar/preparar datos
# (Asumiendo que data/raw/Churn.csv ya existe en repo)
ls data/raw/Churn.csv

# 8. Entrenar modelo
python main.py --mode train \
  --config configs/config.yaml \
  --seed 42 \
  --input data/raw/Churn.csv

# Salida esperada:
# Seeds configuradas: 42
# Loading data from data/raw/Churn.csv...
# Training model...
# Model saved to models/best_model.pkl
# Results saved to results/training_results.json

# 9. Evaluar modelo
python main.py --mode eval \
  --config configs/config.yaml \
  --input data/raw/Churn.csv

# Salida esperada:
# F1 Score: 0.XX
# ROC-AUC: 0.XX

# 10. Iniciar API
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000 --reload

# 11. Probar API (otra terminal)
curl -X GET http://localhost:8000/health
# {"status": "healthy"}

curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d @app/example_payload.json
# {"prediction": 0, "probability": 0.XX, "risk_level": "low"}

# 12. (Opcional) Ejecutar tests
pip install pytest pytest-cov
pytest --cov=. --cov-report=term-missing

# 13. (Opcional) Docker
docker build -t bankchurn:local .
docker run -p 8000:8000 bankchurn:local
```

### Reproducibilidad con DVC (BankChurn)

```bash
# Si el proyecto usa DVC (solo BankChurn actualmente)
pip install dvc

# Reproducir pipeline completo
dvc repro

# Equivalente a:
# python main.py --mode train ...
# python main.py --mode eval ...
```

### Variables de Entorno Importantes

```bash
# Semilla para reproducibilidad
export SEED=42

# MLflow tracking (si configurado)
export MLFLOW_TRACKING_URI=file:./mlruns

# Nivel de logging
export LOG_LEVEL=INFO
```

---

