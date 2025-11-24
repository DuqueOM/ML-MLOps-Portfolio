# {PROJECT_NAME}

![CI](https://img.shields.io/badge/CI-Passing-success?style=flat-square&logo=github-actions)
![Coverage](https://img.shields.io/badge/Coverage-{COVERAGE_PERCENT}%25-brightgreen?style=flat-square)
![DVC](https://img.shields.io/badge/DVC-Enabled-blue?style=flat-square&logo=dvc)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-blue?style=flat-square&logo=mlflow)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)

**{TLDR_SUMMARY}**

## 📋 Overview
This project implements a robust Machine Learning solution designed for production environments. It includes end-to-end pipelines for data processing, model training, evaluation, and deployment, adhering to MLOps best practices.

### Key Features
- **Reproducible Pipelines**: Managed via DVC/Make for consistent execution.
- **Experiment Tracking**: MLflow integration for metrics and parameters.
- **Containerization**: Optimized Docker images for training and inference.
- **Quality Assurance**: High test coverage, type checking, and linting.
- **Scalable Serving**: FastAPI for high-performance inference and Streamlit for interactive dashboards.

## 🚀 Quickstart

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Make (optional, but recommended)

### One-Click Demo
Run the entire stack (API + Dashboard + MLflow) with Docker Compose:

```bash
make start-demo
# Or directly:
docker-compose -f docker-compose.demo.yml up --build
```

- **API**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Dashboard**: [http://localhost:8501](http://localhost:8501)
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
     -d '{SAMPLE_REQUEST_JSON}'
```

**Response:**
```json
{SAMPLE_RESPONSE_JSON}
```

### Dashboard (Streamlit)
Interactive UI for market analysis and "What-if" scenarios.
```bash
streamlit run app/streamlit_app.py
```

## 📈 Monitoring & Operations
- **Health Check**: `GET /health` returns 200 OK if model is loaded.
- **MLflow**: Tracks all training runs. View with `mlflow ui`.
- **Logging**: Structured logging in `logs/` directory.

See [OPERATIONS.md](docs/OPERATIONS.md) for detailed runbook.

## 🛠️ Architecture
See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design, data flow, and component diagrams.

## 🐛 Troubleshooting
- **Docker issues**: Run `docker-compose down -v` to clear volumes.
- **Missing dependencies**: Ensure `requirements.txt` is synced.
- **Tests failing**: Run `pytest` to identify regressions.

## 👥 Maintainers
- **MLOps Team**: [Daniel Duque]
