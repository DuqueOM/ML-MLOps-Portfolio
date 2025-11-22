# Data Science Portfolio — Production-Ready Demos (Landing)

## 1. Resumen Ejecutivo

Portafolio centrado en **3 proyectos TOP-3** listos para demo técnica y conversación de MLOps. Cada proyecto incluye:

- **Pipeline reproducible** vía `Makefile` o CLI (`main.py` con `--mode` y `--config`).
- **API de inferencia** (FastAPI/Streamlit) cuando aplica.
- **Artefactos versionados**: modelos (`model_v1.0.0.pkl` o `model.joblib`), métricas JSON y notebooks de demo.
- **Monitoreo básico**: scripts de drift (KS/PSI) y, en proyectos customer-facing, integración opcional con Evidently.
- **Soporte para MLflow** para tracking de runs en modo `file:./mlruns`.
- **Dockerfile** y, en varios casos, `docker-compose.yml` con `HEALTHCHECK`.

Esta landing sintetiza el valor de cada proyecto, el stack técnico y qué parte del trabajo fue realizada específicamente por el autor.

---

## 2. Resumen por Proyecto (TOP-3)

| Proyecto | Dominio | Valor principal | Stack clave | Demo rápida | Rol objetivo |
|---------|---------|-----------------|------------|------------|--------------|
| **BankChurn-Predictor** | Churn bancario | Clasificador con manejo de desbalance, fairness y explicación SHAP | Python, scikit-learn, FastAPI, MLflow, DVC | `make install && make train && make api-start` | Senior Data Scientist — Customer Intelligence / MLOps-aware |
| **CarVision-Market-Intelligence** | Pricing autos usados | Modelo de precio + dashboard Streamlit + API | Python, scikit-learn, FastAPI, Streamlit, Optuna, MLflow | `make start-demo` | Senior Data Scientist — Pricing & Product Analytics |
| **TelecomAI-Customer-Intelligence** | Telecom | Clasificador Ultra vs Smart con API, Docker y drift | Python, scikit-learn, FastAPI, Docker, MLflow, Evidently (opcional) | `make start-demo` | ML Engineer — Customer Analytics / Telco |

## 2.1 Comparativa técnica (modelo, métricas, nivel producción)

| Proyecto | Problema | Modelo principal | Métricas clave (v1) | Stack ML/MLOps | Nivel de producción |
|----------|----------|------------------|----------------------|-----------------|---------------------|
| **BankChurn-Predictor** | Predicción de churn bancario (`Exited`) | Ensemble Voting (LogReg + RandomForest, con resampling + calibración) | F1, ROC-AUC, precision, recall, accuracy | scikit-learn, Optuna (hyperopt), MLflow, DVC, FastAPI | CLI + tests (incl. fairness) + API + Docker + CI + model/data cards |
| **CarVision-Market-Intelligence** | Pricing de vehículos usados (`price`) | RandomForestRegressor en `Pipeline` sklearn | RMSE, MAE, MAPE, R² | scikit-learn, Optuna (HPO script), MLflow, FastAPI, Streamlit | CLI train/eval/predict + dashboard + API + tests + Docker + CI |
| **TelecomAI-Customer-Intelligence** | Recomendación de plan móvil (`is_ultra`) | LogisticRegression en `Pipeline` | F1, ROC-AUC, accuracy, precision, recall | scikit-learn, MLflow, FastAPI, Evidently (drift demo) | CLI train/eval/predict + tests (incl. API contrato) + API + Docker + CI + model/data cards |

---

## 3. Stack Técnico Global

- **Lenguaje**: Python 3.8–3.11.
- **ML / Estadística**: scikit-learn, XGBoost, statsmodels, RandomForest, regresión logística.
- **MLOps / Tracking**: MLflow (modo local `file:./mlruns`), DVC (datasets versionados en proyectos TOP-3).
- **APIs y Frontends**: FastAPI, Streamlit.
- **Monitoreo de datos**: scripts KS/PSI, integración opcional con Evidently.
- **Optimización**: PuLP/CVXPY/OR-Tools para problemas de asignación y recursos cuando aplica.
- **Infraestructura**: Docker, `docker-compose`, GitHub Actions (`.github/workflows/ci-mlops.yml`).

---

## 4. Ownership (¿Qué hizo el autor?)

Trabajo realizado específicamente sobre los **3 proyectos TOP-3**:

- **BankChurn-Predictor**
  - Integración de MLflow demo (`mlruns/` local y stack Docker opcional).
  - Monitoreo de drift (`monitoring/check_drift.py`).
  - API FastAPI y tests de preprocesamiento y modelo.
  - `model_card.md` y `data_card.md` con documentación estructurada.

- **CarVision-Market-Intelligence**
  - API FastAPI de inferencia y demo de carga de modelo (`app/example_load.py`).
  - Dashboard Streamlit integrado con el modelo de precios.
  - Makefile con comandos `train`, `eval`, `serve` y demo integrada.
  - `model_card.md` y `data_card.md` con supuestos y limitaciones.

- **TelecomAI-Customer-Intelligence**
  - CLI reproducible, API FastAPI + Docker, tests de contrato (`tests/`).
  - Monitoreo de churn y scripts de drift KS/PSI.
  - `model_card.md` y `data_card.md` para dataset y modelo.

---

## 5. Calidad, CI y Smoke Tests

- Workflow CI (`.github/workflows/ci-mlops.yml`):
  - Matriz sobre los 3 proyectos TOP-3 (BankChurn, CarVision, TelecomAI).
  - Para cada uno: instala dependencias, corre `pytest --cov=. --cov-report=term-missing`, `mypy .` y `flake8 .`.
  - Para **BankChurn**: paso adicional de smoke-train (`SMOKE=1`) para validar el pipeline de entrenamiento end-to-end.

Esto hace que cada PR tenga una verificación mínima de:

- Estilo (flake8).
- Tests unitarios de datos/modelo (pytest con cobertura).
- Type-checking (mypy) por proyecto.
- Smoke-train en al menos un proyecto representativo.

---

## 6. Demos y Screenshots

- Cada proyecto incluye README con comandos de demo (`make start-demo`, `make api-start`, etc.).
- Para enriquecer el portafolio visualmente se pueden añadir más adelante:
  - GIFs de dashboards (Streamlit, etc.).
  - Capturas de los endpoints en uso (FastAPI docs, curl + jq).

---

## 7. Cómo Navegar este Monorepo

- Ver **README.md** en la raíz para una vista rápida y comandos de demo.
- Ver cada subdirectorio de proyecto para detalles y documentación técnica.
- Esta `portfolio_landing` sirve como índice central para reclutadores y revisores técnicos.
