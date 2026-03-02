# System Architecture Overview

## Components

| Layer | Components | Technology |
|-------|-----------|------------|
| **Data** | DVC versioning, raw/processed data | DVC + GCS/S3 |
| **Training** | Feature engineering, model training, evaluation | sklearn, XGBoost, MLflow |
| **Serving** | REST APIs, Streamlit dashboard | FastAPI, Streamlit |
| **Monitoring** | Metrics, dashboards, drift detection | Prometheus, Grafana, Evidently |

## Project Architectures

### BankChurn
`API Request → Pydantic Validation → ColumnTransformer → VotingClassifier(LR+RF) → Prediction + Risk Level`
- Unified sklearn Pipeline, SHAP explainability via `?explain=true`

### CarVision
`Vehicle Data → Data Cleaning → FeatureEngineer (centralized) → Preprocessor → XGBRegressor → Price`
- No data leakage: `price_per_mile`/`price_category` dropped from features
- Dual interface: FastAPI + Streamlit (4 tabs)

### NLPInsight
`Text → TF-IDF Vectorization → LogisticRegression → Sentiment Prediction`
- Dual backend: DistilBERT (production) / TF-IDF (lightweight)

## Deployment (Multi-Cloud)

| Resource | GCP (Primary) | AWS |
|----------|--------------|-----|
| **Cluster** | GKE (us-central1) | EKS (us-east-1) |
| **Registry** | Artifact Registry | ECR |
| **Storage** | GCS (models + datasets) | S3 |
| **Database** | Cloud SQL (MLflow) | RDS |
| **Ingress** | GCE Load Balancer | ALB |
| **IaC** | Terraform | Terraform |

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **ML** | Python 3.11, scikit-learn 1.8.0, XGBoost 3.2.0, SHAP 0.50.0 |
| **APIs** | FastAPI, Streamlit, Pydantic |
| **MLOps** | MLflow 3.10, DVC, Evidently AI |
| **Infra** | Docker, Kubernetes (GKE/EKS), Terraform |
| **CI/CD** | GitHub Actions, Trivy, Bandit, Gitleaks |

---

*Last Updated: March 2026*
