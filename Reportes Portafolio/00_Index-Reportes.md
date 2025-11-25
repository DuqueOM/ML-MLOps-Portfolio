# Índice de Reportes de Auditoría — Portafolio ML-MLOps

**Fecha de auditoría**: 2025-11-25  
**Auditor**: Sistema automatizado de evaluación de calidad  
**Repositorio**: [ML-MLOps-Portfolio](https://github.com/DuqueOM/ML-MLOps-Portfolio)

---

## 1) Resumen Ejecutivo

Este documento sirve como índice principal para los reportes de auditoría del portafolio ML-MLOps. La auditoría cubre tres proyectos principales de Machine Learning con enfoque en MLOps:

| Proyecto | Cobertura Tests | Estado Linting | Complejidad Promedio |
|----------|----------------|----------------|----------------------|
| BankChurn-Predictor | 78% | ✅ Passing | A (3.76) |
| CarVision-Market-Intelligence | 86% | ⚠️ 3 archivos por formatear | A (4.19) |
| TelecomAI-Customer-Intelligence | 91% | ✅ Passing | A (2.73) |

**Hallazgos clave:**
- ✅ No se encontraron vulnerabilidades críticas de seguridad (Bandit, pip-audit)
- ✅ No se detectaron secretos expuestos en el código actual (gitleaks)
- ⚠️ Hallazgos históricos de gitleaks en notebooks (26 falsos positivos en EDA.ipynb)
- ⚠️ Algunos errores de tipado en mypy que requieren corrección

---

## 2) Lista de Reportes Disponibles

### Reportes por Proyecto (Español)

| Archivo | Descripción |
|---------|-------------|
| `BankChurn-Predictor-Reporte.md` | Auditoría completa del predictor de abandono bancario |
| `CarVision-Market-Intelligence-Reporte.md` | Auditoría del analizador de mercado automotriz |
| `TelecomAI-Customer-Intelligence-Reporte.md` | Auditoría del predictor de churn de telecomunicaciones |

### Reportes Globales (Español)

| Archivo | Descripción |
|---------|-------------|
| `Global-Code-Quality-Report.md` | Resultados agregados de linting, tipado y complejidad |
| `Security-Dependency-Report.md` | Análisis de seguridad SAST y vulnerabilidades de dependencias |
| `Security-Audit-Remediation.md` | Auditoría de seguridad completa y acciones de remediación |
| `DVC-Cloud-Configuration.md` | Guía de configuración de DVC con almacenamiento cloud |
| `CI-Improvements-Proposal.md` | Propuestas de mejora para CI/CD con snippets YAML |

### Outputs Crudos (English filenames)

Los outputs de las herramientas de auditoría se encuentran en:

```
reports/
├── audit/
│   ├── bandit-bankchurn.json      # SAST BankChurn
│   ├── bandit-carvision.json      # SAST CarVision
│   ├── bandit-telecom.json        # SAST TelecomAI
│   ├── pip-audit.json             # Dependency vulnerabilities
│   ├── bankchurn-pytest.txt       # Test output BankChurn
│   └── telecom-pytest.txt         # Test output TelecomAI
├── gitleaks-report.json           # Secret scanning (historical, raw)
└── gitleaks-report-sanitized.json # Secret scanning (sanitized, safe to share)
```

---

## 3) Cómo Reproducir esta Auditoría

### Prerrequisitos

```bash
# Clonar repositorio
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio

# Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar herramientas de auditoría
pip install -U pip
pip install black flake8 mypy bandit radon pytest pytest-cov coverage pip-audit pre-commit ruff isort

# Instalar dependencias de proyectos (para correr tests)
pip install numpy pandas scikit-learn joblib pyyaml fastapi uvicorn pydantic xgboost imbalanced-learn optuna matplotlib seaborn plotly tqdm requests httpx mlflow
```

### Comandos de Auditoría

#### 1. Formateo y Linting

```bash
# Verificar formato con Black (cada proyecto)
black --check BankChurn-Predictor/src BankChurn-Predictor/app
black --check CarVision-Market-Intelligence/src CarVision-Market-Intelligence/app
black --check TelecomAI-Customer-Intelligence/src TelecomAI-Customer-Intelligence/app

# Verificar estilo con Flake8
flake8 BankChurn-Predictor/src --max-line-length=120 --statistics
flake8 CarVision-Market-Intelligence/src --max-line-length=120 --statistics
flake8 TelecomAI-Customer-Intelligence/src --max-line-length=120 --statistics
```

#### 2. Tipado Estático

```bash
mypy BankChurn-Predictor/src --ignore-missing-imports
mypy CarVision-Market-Intelligence/src --ignore-missing-imports
mypy TelecomAI-Customer-Intelligence/src --ignore-missing-imports
```

#### 3. Análisis de Complejidad

```bash
radon cc BankChurn-Predictor/src -s -a
radon cc CarVision-Market-Intelligence/src -s -a
radon cc TelecomAI-Customer-Intelligence/src -s -a
```

#### 4. Escaneo de Seguridad

```bash
# SAST con Bandit
bandit -r BankChurn-Predictor/src -f json -o reports/audit/bandit-bankchurn.json -ll
bandit -r CarVision-Market-Intelligence/src -f json -o reports/audit/bandit-carvision.json -ll
bandit -r TelecomAI-Customer-Intelligence/src -f json -o reports/audit/bandit-telecom.json -ll

# Vulnerabilidades de dependencias
pip-audit --format=json > reports/audit/pip-audit.json

# Secretos (ya ejecutado previamente)
# gitleaks detect --source . --report-path reports/gitleaks-report.json
```

#### 5. Tests con Cobertura

```bash
# BankChurn-Predictor
cd BankChurn-Predictor
pytest tests/ -q --tb=short -m "not slow" --cov=src --cov-report=term-missing
cd ..

# CarVision-Market-Intelligence
cd CarVision-Market-Intelligence
pytest tests/ -q --tb=short -m "not slow" --cov=src --cov-report=term-missing
cd ..

# TelecomAI-Customer-Intelligence
cd TelecomAI-Customer-Intelligence
pytest tests/ -q --tb=short -m "not slow" --cov=src --cov-report=term-missing
cd ..
```

---

## 4) Resumen de Issues por Prioridad

### P1 — Críticos (Acción Inmediata)

| ID | Proyecto | Issue | Recomendación |
|----|----------|-------|---------------|
| - | - | No se encontraron issues críticos | - |

### P2 — Importantes (Próxima Iteración)

| ID | Proyecto | Issue | Recomendación |
|----|----------|-------|---------------|
| P2-01 | CarVision | 3 archivos sin formatear con Black | Ejecutar `black CarVision-Market-Intelligence/src` |
| P2-02 | BankChurn | Errores de mypy en config.py | Añadir tipos Optional y defaults faltantes |
| P2-03 | CarVision | Error mypy: implicit Optional | Cambiar `filters: dict = None` a `filters: Optional[dict] = None` |
| P2-04 | TelecomAI | Library stubs faltantes para PyYAML | Instalar `types-PyYAML` |

### P3 — Deuda Técnica (Backlog)

| ID | Proyecto | Issue | Recomendación |
|----|----------|-------|---------------|
| P3-01 | BankChurn | Complejidad C (13) en `ChurnPredictor.predict` | Refactorizar en métodos más pequeños |
| P3-02 | CarVision | Complejidad C (14) en `infer_feature_types` | Extraer lógica a funciones auxiliares |
| P3-03 | CarVision | 0% cobertura en visualization.py | Añadir tests unitarios |
| P3-04 | Global | Gitleaks histórico (26 alertas en notebooks) | Limpiar outputs de notebooks |

---

## 5) Estructura del Repositorio Auditado

```
ML-MLOps-Portfolio/
├── BankChurn-Predictor/          # Predicción de abandono bancario
│   ├── src/bankchurn/            # Código fuente principal
│   ├── app/                      # FastAPI endpoints
│   ├── tests/                    # 88 tests, 78% cobertura
│   └── configs/                  # Configuración YAML
├── CarVision-Market-Intelligence/ # Análisis de mercado automotriz
│   ├── src/carvision/            # Código fuente principal
│   ├── app/                      # FastAPI + Streamlit
│   ├── tests/                    # 17 tests, 86% cobertura
│   └── configs/                  # Configuración YAML
├── TelecomAI-Customer-Intelligence/ # Predicción de churn telecom
│   ├── src/telecom/              # Código fuente principal
│   ├── app/                      # FastAPI endpoints
│   ├── tests/                    # 13 tests, 91% cobertura
│   └── configs/                  # Configuración YAML
├── .github/workflows/            # CI/CD pipelines
│   ├── ci-mlops.yml              # Pipeline principal
│   ├── ci-portfolio-top3.yml     # Tests Top-3 projects
│   └── drift-detection.yml       # Detección de drift
├── infra/                        # Infrastructure as Code
├── k8s/                          # Kubernetes manifests
└── reports/                      # Outputs de auditoría
```

---

## 6) CI/CD Pipeline Actual

El archivo `.github/workflows/ci-mlops.yml` contiene:

| Job | Descripción | Triggers |
|-----|-------------|----------|
| `tests` | Tests unitarios con matrix (Python 3.11, 3.12) | push, PR |
| `security` | Gitleaks + Bandit | push, PR |
| `docker` | Build + Trivy scan | push, PR |
| `e2e` | End-to-end tests | after tests |
| `integration-test` | Cross-project integration | after docker |
| `validate-docs` | Verificar model/data cards | push, PR |

**Mejoras sugeridas** (ver `Security-Dependency-Report.md`):
- Añadir job `quality-gates` con umbrales de cobertura
- Añadir `pip-audit` al job de seguridad
- Generar artifacts de reportes automáticamente

---

## 7) Próximos Pasos Recomendados

1. **Inmediato (esta semana)**:
   - [ ] Ejecutar `black CarVision-Market-Intelligence/src/` para formatear
   - [ ] Corregir tipos Optional en `data.py` de CarVision
   - [ ] Instalar `types-PyYAML` y corregir mypy warnings

2. **Corto plazo (2 semanas)**:
   - [ ] Refactorizar funciones con complejidad C
   - [ ] Añadir tests a `visualization.py`
   - [ ] Limpiar outputs de notebooks (gitleaks)

3. **Mediano plazo (1 mes)**:
   - [ ] Implementar quality-gates en CI/CD
   - [ ] Automatizar generación de reportes
   - [ ] Crear ADRs para decisiones arquitectónicas

---

## 8) Referencias

- **Documentación del portafolio**: `README.md`, `QUICK_START.md`
- **Arquitectura**: `docs/ARCHITECTURE_PORTFOLIO.md`
- **CI/CD**: `.github/workflows/ci-mlops.yml`
- **Pre-commit hooks**: `.pre-commit-config.yaml`

---

*Este reporte fue generado automáticamente como parte del proceso de auditoría del portafolio ML-MLOps.*
