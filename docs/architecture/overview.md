# System Architecture Overview

## Components

| Layer | Components | Technology |
|-------|-----------|------------|
| **Data** | DVC versioning, raw/processed data | DVC + GCS/S3 |
| **Training** | Feature engineering, model training, evaluation | sklearn, LightGBM, Transformers, MLflow |
| **Serving** | REST APIs, Streamlit dashboard | FastAPI, Streamlit |
| **Monitoring** | Metrics, dashboards, drift detection | Prometheus, Grafana, Evidently |

## Project Architectures

### BankChurn
`API Request → Pydantic Validation → ColumnTransformer → StackingClassifier(RF+GB+XGB+LGB→LR) → Prediction + Risk Level`
- Unified sklearn Pipeline, SHAP explainability via `?explain=true`, fairness audits (disparate impact)

### NLPInsight
`Text → FinBERT Tokenizer → FinBERT (ProsusAI) → Sentiment Prediction`
- Dual backend: FinBERT (production) / TF-IDF+LogReg (lightweight fallback), fairness audits (F1 parity)

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
| **ML** | Python 3.11, scikit-learn 1.8.0, LightGBM 4.6+, HuggingFace Transformers, SHAP 0.50.0 |
| **APIs** | FastAPI, Streamlit, Pydantic |
| **MLOps** | MLflow 3.10, DVC, Evidently AI, OpenTelemetry |
| **Responsible AI** | Fairness audits (×3), drift detection (KS+PSI+Evidently), Pandera validation |
| **Infra** | Docker, Kubernetes (GKE/EKS), Terraform |
| **CI/CD** | GitHub Actions, Trivy, Bandit, Gitleaks |

---

*Last Updated: March 2026 — v3.3.1*
