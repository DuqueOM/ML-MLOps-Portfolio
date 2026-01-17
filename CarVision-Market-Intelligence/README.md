# CarVision Market Intelligence

[![Documentation](https://img.shields.io/badge/Docs-Project%20Site-blue)](https://duqueom.github.io/ML-MLOps-Portfolio/projects/carvision/)
[![CI Status](https://img.shields.io/github/actions/workflow/status/DuqueOM/ML-MLOps-Portfolio/ci-mlops.yml?branch=main&label=CI)](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml)
[![codecov](https://codecov.io/gh/DuqueOM/ML-MLOps-Portfolio/branch/main/graph/badge.svg?flag=CarVision-Market-Intelligence)](https://codecov.io/gh/DuqueOM/ML-MLOps-Portfolio?flag=CarVision-Market-Intelligence)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue)](pyproject.toml)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2?logo=mlflow&logoColor=white)](configs/config.yaml)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)](app/streamlit_app.py)

---

<div align="center">

**API Demo:**

![CarVision API Demo](../docs/media/gifs/carvision-preview.gif)

**Streamlit Dashboard:**

![Streamlit Dashboard](../docs/media/gifs/streamlit-carvision.gif)

### 📺 Portfolio Demo

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

</div>

---

**End-to-end ML system for vehicle price prediction and market analytics. Features centralized `FeatureEngineer` class, FastAPI serving, Streamlit dashboards, and MLflow experiment tracking.**

## 📋 Overview
This project implements a robust Machine Learning solution designed for production environments. It includes end-to-end pipelines for data processing, model training, evaluation, and deployment, adhering to MLOps best practices.

### Key Features
- **Reproducible Pipelines**: Managed via DVC/Make for consistent execution.
- **Experiment Tracking**: MLflow integration for metrics and parameters.
- **Containerization**: Optimized Docker images for training and inference.
- **Quality Assurance**: High test coverage (97%), type checking, and linting.
- **Scalable Serving**: FastAPI with Prometheus metrics and Streamlit for interactive dashboards.
- **Observability**: Prometheus metrics endpoint (`/metrics`) for production monitoring.

### Architecture

```mermaid
flowchart LR
    A[Raw Data CSV] --> B[Feature Engineering]
    B --> C[Training Pipeline]
    C --> D[Model Registry]
    D --> E[Inference API]
    E --> F[Dashboard]
```

## 🚀 Quickstart

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Make (optional, but recommended)

### One-Click Demo (Local)
Train the model and run both API + Dashboard locally:

```bash
make start-demo
```

- **API (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Dashboard (Streamlit)**: [http://localhost:8501](http://localhost:8501)

### Full Portfolio Demo (Docker)
Run all 3 projects together from the portfolio root:

```bash
cd ..  # Go to portfolio root
docker compose -f docker-compose.demo.yml up --build
```

- **CarVision API**: [http://localhost:8002/docs](http://localhost:8002/docs)
- **CarVision Dashboard**: [http://localhost:8501](http://localhost:8501)
- **MLflow**: [http://localhost:5000](http://localhost:5000)

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run training
python main.py --mode train --config configs/config.yaml

# Run API
uvicorn app.fastapi_app:app --reload
```

## 📊 Data
The project uses a structured data pipeline:
1.  **Raw Data**: Ingested from source (CSV/DB).
2.  **Processing**: Cleaning, validation, and feature engineering via `src.carvision.features`.
3.  **Splitting**: Train/Val/Test splits saved as artifacts.

Data versioning is handled by DVC. To reproduce data stages:
```bash
dvc repro data_processing
```

## 🧠 Training
Training is configured via `configs/config.yaml`. The pipeline includes:
- Feature Engineering (temporal features, binning)
- Preprocessing (Imputation, OneHotEncoding, Scaling)
- Model Training (RandomForest/LightGBM)
- Evaluation (CV, Bootstrap, Temporal Backtesting)

To retrain:
```bash
python main.py --mode train
```

## 🔌 Serving
### API (FastAPI)
REST endpoint for real-time inference.

**Request Example:**
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
  "model_year": 2018,
  "odometer": 45000,
  "model": "ford f-150",
  "fuel": "gas",
  "transmission": "automatic"
}'
```

**Response:**
```json
{
  "prediction": 24500.0,
  "vehicle_age": 6,
  "brand": "ford"
}
```

### Dashboard (Streamlit)
Interactive UI for market analysis, model performance review and price prediction.

Sections:
- **Overview** – Portfolio KPIs, price distribution and inventory breakdown.
- **Market Analysis** – Executive-level investment and risk insights powered by `MarketAnalyzer` and `VisualizationEngine`.
- **Model Metrics** – RMSE/MAE/R²/MAPE, bootstrap confidence intervals and temporal backtest from `artifacts/metrics*.json`.
- **Price Predictor** – Single-vehicle ML price estimator with market percentile positioning and gauge visualization.

Run locally:
```bash
streamlit run app/streamlit_app.py
```

Requirements for the dashboard:
- Trained model artifact at `artifacts/model.joblib`.
- Metrics files at `artifacts/metrics.json` (and optionally `metrics_baseline.json`, `metrics_bootstrap.json`, `metrics_temporal.json`).
- Dataset `data/raw/vehicles_us.csv` available in the project root or under `data/raw/`.

Optional enhancements:
- `pip install pandera` to enable data schema validation on load.
- `pip install shap` to enable SHAP-based prediction explanations in the Price Predictor tab.

## 📊 MLflow Integration

This project integrates with MLflow for experiment tracking with **3 tracked experiments** comparing different regression approaches.

### Tracked Experiments

| Run | Model | Test RMSE | Test R² | Purpose |
|-----|-------|-----------|---------|--------|
| CV-1_Baseline_Ridge | Ridge Regression | $5,591 | 0.63 | Linear baseline |
| **CV-2_RandomForest_Tuned** | RandomForest | **$4,396** | **0.77** | Best model |
| CV-3_GradientBoosting | GradientBoosting | $4,416 | 0.77 | Alternative |

### Run Experiments

```bash
# Point to the portfolio's central MLflow server
export MLFLOW_TRACKING_URI=http://localhost:5000

# Run all CarVision experiments (from portfolio root)
python scripts/run_experiments.py
```

---

## 📝 Monitoring & Operations
- **Health Check**: `GET /health` returns 200 OK if model is loaded.
- **MLflow**: Tracks all training runs at `http://localhost:5000`.
- **Logging**: Structured logging in `logs/` directory.

See [OPERATIONS.md](docs/OPERATIONS.md) for detailed runbook.

## 🛠️ Architecture
See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design, data flow, and component diagrams.

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Docker issues | Run `docker-compose down -v` to clear volumes |
| Missing dependencies | Ensure `requirements.txt` is synced |
| Tests failing | Run `pytest -v` to identify regressions |
| Model not found | Run training first: `python main.py --mode train` |

---

## 📋 CI Notes

| Component | Details |
|-----------|---------|
| **Workflow** | `.github/workflows/ci-mlops.yml` |
| **Coverage** | 97% (threshold: 80%) |
| **Python** | 3.11, 3.12 (matrix) |

**If tests fail**: Check the `tests` job logs → expand coverage artifact.

---

## 📄 Model Card

See [models/model_card.md](models/model_card.md) for:
- Model architecture (RandomForest with FeatureEngineer pipeline)
- Performance metrics (RMSE, MAE, R², MAPE)
- Validation methods (Cross-validation, Bootstrap, Temporal backtest)
- Reproduction instructions

---

## ✅ Acceptance Checklist

- [x] Tests pass (`pytest`)
- [x] API starts and responds
- [x] Dashboard loads without errors
- [x] Docker image builds
- [x] Model card documented

---

## 👥 Maintainers

- **Duque Ortega Mutis (DuqueOM)** - Lead MLOps Engineer - [GitHub](https://github.com/DuqueOM)
