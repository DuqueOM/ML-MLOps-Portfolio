# System Architecture Overview

## Components

| Layer | Components | Technology |
|-------|-----------|------------|
| **Data** | DVC versioning, raw/processed data | DVC + GCS/S3 |
| **Training** | Feature engineering, model training, evaluation | sklearn, LightGBM, Transformers, MLflow |
| **Serving** | REST APIs (3 services) | FastAPI, Pydantic |
| **Monitoring** | Metrics, dashboards, drift detection | Prometheus, Grafana, Evidently |

## Project Architectures

### BankChurn
`API Request → Pydantic Validation → ColumnTransformer → StackingClassifier(RF+GB+XGB+LGB→LR) → Prediction + Risk Level`
- Unified sklearn Pipeline, SHAP explainability via `?explain=true`, fairness audits (disparate impact)

### NLPInsight
`Text → TF-IDF+LogReg (production) or FinBERT (GPU) → Sentiment Prediction`
- Dual backend: TF-IDF+LogReg (production, <5ms) / FinBERT (GPU), fairness audits (F1 parity)

### ChicagoTaxi
`6.3M Trips → PySpark ETL → Lag Features → RandomForest → Batch Predictions`
- Temporal split, leak-free lag features, Dask batch inference (19K rows/sec)

## Deployment (Multi-Cloud)

| Resource | GCP (Primary) | AWS |
|----------|--------------|-----|
| **Cluster** | GKE (us-central1) | EKS (us-east-1) |
| **Registry** | Artifact Registry | ECR |
| **Storage** | GCS (models + datasets) | S3 |
| **Database** | Cloud SQL (MLflow) | RDS |
| **Ingress** | nginx + GCE LB (static IP) | nginx + NLB (AWS Load Balancer Controller) |
| **IaC** | Terraform | Terraform |

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **ML** | Python 3.11, scikit-learn 1.8.0, LightGBM 4.6+, HuggingFace Transformers, SHAP 0.50.0 |
| **APIs** | FastAPI, Pydantic |
| **MLOps** | MLflow 3.10, DVC, Evidently AI, OpenTelemetry |
| **Responsible AI** | Fairness audits (×3), drift detection (KS+PSI+Evidently), Pandera validation |
| **Infra** | Docker, Kubernetes (GKE/EKS), Terraform |
| **CI/CD** | GitHub Actions, Trivy, Bandit, Gitleaks |

---

*Last Updated: March 2026 — v3.5.3*
