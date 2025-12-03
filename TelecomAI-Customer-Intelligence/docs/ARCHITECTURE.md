# Architecture - TelecomAI Customer Intelligence

**Project:** TelecomAI Customer Intelligence  \
**Domain:** Telecom plan recommendation  \
**Status:** Production-ready demo

---

## 1. System Overview

TelecomAI predicts the most suitable mobile plan (Standard vs Ultra) based on historical
usage patterns (calls, minutes, messages, MB used). The system is composed of:

1. **Training Pipeline** – data loading, preprocessing, model training and evaluation.  
2. **Inference API** – FastAPI service exposing `/predict` and `/health`.  
3. **Operations & Monitoring** – Dockerized deployment with Prometheus metrics.

---

## 2. High-Level Architecture

```mermaid
graph TD
    subgraph Data & Training
        A[Raw Usage Data (CSV)] -->|Load & Validate| B[Preprocessing]
        B --> C[Feature Matrix]
        C --> D[Model Training (GradientBoosting/RandomForest)]
        D --> E[Evaluation & Metrics]
        D --> F[Model Artifact]
    end

    subgraph Serving
        User[Client / CRM] -->|POST /predict| API[FastAPI Service]
        API -->|Load| F
        API -->|Predict| Resp[JSON Response]
        API -->|Metrics| Prom[Prometheus]
    end
```

**Key points:**
- Single sklearn pipeline encapsulating preprocessing + classifier ensures training/serving
  consistency.
- FastAPI handles validation via Pydantic models and exposes Prometheus metrics at `/metrics`.
- Artifacts (model + metrics) are stored under `artifacts/` and tracked in MLflow.

---

## 3. Components

### 3.1 Training
- Entry point: `main.py --mode train`  
- Responsibilities:
  - Load `data/raw/users_behavior.csv`.
  - Split train/validation/test sets.
  - Train GradientBoosting / RandomForest classifier.
  - Log metrics and parameters to MLflow (`artifacts/metrics.json`).

See per-file docs in `docs/_per_file/` for details:
- `training.md` – training loop and configuration.  
- `config.md` – configuration schema and defaults.

### 3.2 Inference API (`app/fastapi_app.py`)
- Endpoints:
  - `GET /health` – reports service status (includes "degraded" when model is not yet loaded).  
  - `POST /predict` – returns plan prediction and probability.
- Uses a persisted sklearn pipeline from `artifacts/model.joblib`.
- Exposes Prometheus metrics at `/metrics` for request count/latency.

See `docs/_per_file/fastapi_app.md` for detailed API design and examples.

### 3.3 CI/CD Integration
- Unified CI workflow: `.github/workflows/ci-mlops.yml` (portfolio root).  
- For TelecomAI, the pipeline runs:
  - Linting & tests (coverage ≈ 97%).
  - Type checks and security scans (Bandit, Gitleaks at portfolio level).
  - Docker build and image scan before publishing to GHCR.

See `docs/_per_file/ci_mlops.md` for how this project fits into the shared pipeline.

---

## 4. Data & Artifacts

- **Data:** `data/raw/users_behavior.csv` (DVC-managed in the portfolio context).  
- **Model:** `artifacts/model.joblib` – sklearn pipeline (preprocessing + classifier).  
- **Metrics:** `artifacts/metrics.json` – Accuracy, AUC-ROC, F1.

MLflow is used at the portfolio level to track experiments across all three projects;
TelecomAI contributes 3 runs (baseline, tuned, alternative).

---

## 5. Future Improvements

- Add SHAP-based explainability endpoints for per-customer plan recommendations.  
- Integrate with a shared Feature Store for consistent feature definitions across
  BankChurn, CarVision y TelecomAI.  
- Extend drift monitoring patterns (as implemented for BankChurn) to this project
  to trigger retraining when traffic distributions change significantly.
