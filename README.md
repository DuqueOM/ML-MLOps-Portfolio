# 🚀 Portfolio ML/MLOps - Tier-1

**Portfolio Profesional de Machine Learning y MLOps centrado en 3 Proyectos "Production-Ready"**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![MLOps](https://img.shields.io/badge/MLOps-Production--Ready-green.svg)](https://mlops.org)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue.svg)](https://github.com/features/actions)
[![Coverage](https://img.shields.io/badge/Coverage-%3E70%25-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage-2496ED.svg?logo=docker&logoColor=white)](Dockerfile)
[![DVC](https://img.shields.io/badge/DVC-Data%20Versioning-945DD6.svg)](https://dvc.org)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC.svg?logo=terraform&logoColor=white)](infra/terraform/)
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2.svg?logo=mlflow&logoColor=white)](https://mlflow.org)
[![Evidently](https://img.shields.io/badge/Evidently-Drift%20Detection-FF6600.svg)](https://evidentlyai.com)

> **Portfolio profesional que demuestra el ciclo de vida completo de Machine Learning: desde el análisis exploratorio y el entrenamiento de modelos, hasta la implementación de pipelines de CI/CD, APIs REST y despliegue containerizado.**

---

## 👨‍💻 Sobre el Portfolio

Este repositorio se centra en **3 Proyectos Principales (Top-3)** que han sido llevados a un nivel de ingeniería de software profesional, demostrando capacidades Senior/Enterprise en:

- ✅ **Machine Learning Avanzado**: Ensembles, Regresión, Clasificación con manejo de desbalance.
- ✅ **MLOps & CI/CD**: Pipelines automatizados unificados (`ci-mlops.yml`), testing riguroso y escaneo de seguridad.
- ✅ **Ingeniería de Software**: Arquitectura modular, Pydantic para validación, APIs con FastAPI.
- ✅ **Despliegue**: Dockerización completa y dashboards interactivos (Streamlit).

---

## 🌟 TOP-3: Proyectos Production-Ready

### 🏦 1. [BankChurn Predictor](BankChurn-Predictor/) (Tier-1 MLOps)
**Sistema robusto de predicción de abandono de clientes**

- **Arquitectura**: Diseño modular (`src/bankchurn`) instalable como paquete.
- **MLOps**: 
  - Integración con **MLflow** para tracking de experimentos.
  - Validación de configuración con **Pydantic**.
  - Pipeline de CI/CD verde con tests unitarios y de integración.
- **Tech Stack**: FastAPI, Scikit-learn, Docker, DVC.
- **Coverage**: >68% (Cumple threshold de calidad).

[Ver Proyecto →](BankChurn-Predictor/)

### 🚗 2. [CarVision Market Intelligence](CarVision-Market-Intelligence/) (Interactive AI)
**Plataforma de valoración de vehículos con Dashboard**

- **Experiencia de Usuario**: Dashboard interactivo construido con **Streamlit**.
- **Backend**: API REST (FastAPI) para servir el modelo de regresión.
- **Modelado**: Random Forest optimizado para alta precisión en precios de mercado.
- **Calidad**: Alta cobertura de tests y validación de datos.

[Ver Proyecto →](CarVision-Market-Intelligence/)

### 📱 3. [TelecomAI Customer Intelligence](TelecomAI-Customer-Intelligence/) (Advanced Analytics)
**Predicción estratégica de churn en telecomunicaciones**

- **Modelado Complejo**: **Voting Classifier** combinando múltiples estrategias.
- **Pipeline**: Preprocesamiento avanzado y feature engineering específico de dominio.
- **Automatización**: Tests end-to-end integrados en el pipeline de CI.
- **Métricas**: AUC-ROC > 0.85.

[Ver Proyecto →](TelecomAI-Customer-Intelligence/)

---

## ️ Stack Tecnológico & MLOps

### Infraestructura CI/CD Unificada (Staff-Level)
Todo el portfolio es validado por un único workflow maestro (`ci-mlops.yml`) que orquesta:

1. **Build & Environment**:
   - Setup de Python 3.11 y 3.12 (matrix testing) con **caché inteligente de pip**.
   - Restauración automática de dependencias por proyecto vía `cache-dependency-path`.
   - **Optimización**: Reduce tiempo de instalación de 5min → 30s.

2. **Data Quality Gates**: 
   - Validación automática de calidad de datos **antes de tests**.
   - Scripts personalizados por proyecto (`data/validate_data.py`).
   - Fail-fast en datasets corruptos/incompletos.

3. **Code Quality**: 
   - `flake8` & `black` para estilo.
   - `mypy` para tipado estático.
   - `bandit` para seguridad en código Python.

4. **Testing**: Ejecución paralela de `pytest` con reportes de cobertura.

5. **Continuous Deployment**:
   - Build automático de imágenes Docker tras pasar tests.
   - Push a **GitHub Container Registry (GHCR)** con tags inmutables (SHA + semver).
   - Cache de layers Docker vía GitHub Actions cache.
   - **Artefactos listos para producción en cada commit**.

6. **Container Security**: Escaneo de imágenes Docker con **Trivy** (CVE detection).

### Infraestructura como Código (IaC)
- **Terraform**: Módulos AWS y GCP en `infra/terraform/`
  - Full stack: EKS, S3, RDS, ECR (ver `main.tf`)
  - **S3 Artifact Store simplificado**: Versionado, encriptación, lifecycle (ver `s3-artifacts-simple.tf`)
- **Uso**: Almacenamiento reproducible y seguro de modelos versionados.

### Tecnologías Clave
- **Core**: Python 3.11+, Pandas, NumPy, Scikit-learn, XGBoost, Optuna.
- **Web**: FastAPI, Streamlit, Uvicorn.
- **Ops**: Docker (Multi-Stage), GitHub Actions, Kubernetes, Makefiles, Terraform.
- **Tracking & Data**: MLflow, DVC.
- **Monitoring**: Prometheus, Grafana.
- **Security**: Trivy, Bandit, Gitleaks.
- **Registry**: GitHub Container Registry (GHCR) para imágenes inmutables.

---

## 📚 Documentación Global

- **[Arquitectura del Portfolio](docs/ARCHITECTURE_PORTFOLIO.md)**: Sistema completo con diagramas Mermaid, Docker multi-stage, CI/CD pipeline y stack tecnológico.
- **[Runbook de Operaciones](docs/OPERATIONS_PORTFOLIO.md)**: Guía completa para despliegue (Docker/K8s), monitoreo con Prometheus/Grafana, troubleshooting y mantenimiento.
- **[Gestión de Dependencias](docs/DEPENDENCY_CONFLICTS.md)**: Análisis de conflictos (PyArrow, Pydantic), plan de remediación y estrategia de versionado.
- **[Proceso de Release](docs/RELEASE.md)**: Workflow completo de releases, publicación a GHCR, rollback procedures y model versioning.
- **[Plan de PRs](docs/PR_PLAN.md)**: 10 Pull Requests priorizados con especificaciones completas, diffs y timeline de 4 semanas.
- **[Quick Start](QUICK_START.md)**: Demo en un comando para evaluación rápida.

---

## 📁 Estructura del Portfolio

```
Portafolio-ML-MLOps/
├── .github/workflows/
│   └── ci-mlops.yml               # ⚡ CI Pipeline Unificado (Build, Test, Scan)
│
├── BankChurn-Predictor/           # 🏦 Proyecto Tier-1
│   ├── src/bankchurn/             # Paquete Python modular
│   ├── tests/                     # Tests unitarios e integración
│   ├── Dockerfile                 # Definición de contenedor
│   └── ...
│
├── CarVision-Market-Intelligence/ # 🚗 App Interactiva
│   ├── app/                       # Streamlit + FastAPI
│   ├── tests/
│   └── Dockerfile
│
├── TelecomAI-Customer-Intelligence/# 📱 Análisis Avanzado
│   ├── models/
│   ├── tests/
│   └── Dockerfile
│
├── common_utils/                  # Utilidades compartidas (seed, logger)
├── tests/integration/             # Tests de integración cross-project
├── infra/                         # Docker Compose, Terraform (AWS/GCP), Prometheus/Grafana
├── k8s/                           # Manifests Kubernetes (deployments, HPA, ingress)
├── docs/                          # Documentación global del portfolio
├── FINAL_PORTFOLIO_STATUS.md      # 📊 Estado detallado del portfolio
├── CONTRIBUTING.md                # Guía de contribución
├── CHANGELOG.md                   # Historial de versiones
└── README.md                      # Este archivo
```

---

## 📈 Métricas de Calidad

| Métrica | Estado | Target |
|---------|--------|--------|
| **CI Pipeline** | 🟢 **Passing** | 100% Green |
| **Test Coverage** | 🟢 **> 75% (Avg)** | > 70% |
| **Seguridad** | 🛡️ **Scanned** | 0 Critical CVEs |
| **Docker Builds** | 🐳 **Multi-Stage** | 50% Size Reduction |
| **Python Support** | ✅ **3.11 & 3.12** | Matrix Testing |

---

## 🚀 Quick Start

### One-Liner Demo (Recommended)
```bash
# 1. Generate demo models first (required for first run)
bash scripts/setup_demo_models.sh

# 2. Start full demo stack with all 3 services + MLflow
make docker-demo
# or: docker-compose -f docker-compose.demo.yml up -d --build

# 3. Run integration tests to verify everything works
bash scripts/run_demo_tests.sh
```

**Demo includes:**
- 🏦 BankChurn API: `http://localhost:8001/docs`
- 🚗 CarVision API: `http://localhost:8002/docs`
- 🚗 CarVision Dashboard: `http://localhost:8501`
- 📱 TelecomAI API: `http://localhost:8003/docs`
- 📊 MLflow UI: `http://localhost:5000`
- 📈 Prometheus: `http://localhost:9090` (with --profile monitoring)
- 📊 Grafana: `http://localhost:3000` (with --profile monitoring)

### Manual Setup (BankChurn)
```bash
# 1. Clone repository
git clone https://github.com/DuqueOM/Portafolio-ML-MLOps.git
cd Portafolio-ML-MLOps

# 2. Using Docker Compose (easiest)
docker-compose -f docker-compose.demo.yml up -d

# 3. Or build individual service
cd BankChurn-Predictor
docker build -t bankchurn:latest .
docker run -p 8000:8000 bankchurn:latest

# 4. Test API
curl -X POST "http://localhost:8001/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "CreditScore": 650,
       "Geography": "France",
       "Gender": "Female",
       "Age": 40,
       "Tenure": 3,
       "Balance": 60000,
       "NumOfProducts": 2,
       "HasCrCard": 1,
       "IsActiveMember": 1,
       "EstimatedSalary": 50000
     }'
```

### Development Setup
```bash
# Install dependencies for all projects
make install

# Run tests
make test

# Run integration tests
pytest tests/integration/test_demo.py -v

# Check service health
make health-check

# Security scans
bandit -r . -f json -o bandit-report.json
docker run --rm aquasec/trivy image <image-name>
```

---

## 👤 Autor

**Duque Ortega Mutis (DuqueOM)**  
*Ingeniero de Machine Learning & MLOps*

[LinkedIn](https://linkedin.com/in/duqueom) | [GitHub](https://github.com/DuqueOM)

---

<div align="center">
**Status**: ✅ Production-Ready | **Última Actualización**: Noviembre 2025
</div>
