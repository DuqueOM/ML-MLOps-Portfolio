---
trigger: always_on
---

# ML-MLOps Portfolio Core Conventions

## Tech Stack
- Python 3.11+, sklearn 1.8.x, FastAPI, Docker, Kubernetes
- Multi-cloud: GKE (us-central1) + EKS (us-east-1)
- IaC: Terraform for cloud, Kustomize overlays for K8s
- CI/CD: GitHub Actions with matrix testing
- Monitoring: Prometheus custom metrics + Grafana dashboards

## Critical Architecture Decisions
- CPU-only HPA — memory footprint is fixed for ML models (ADR-001)
- Single-worker uvicorn pod + HPA horizontal scaling (ADR-014)
- AsyncIO ThreadPoolExecutor(4) for inference — sklearn releases GIL (ADR-015)
- KernelExplainer for SHAP with StackingClassifier (ADR-010)
- Compatible release pinning (~=) for all dependencies (ADR-005)

## Code Standards
- Type hints on ALL public functions
- Pydantic BaseModel for configuration and request/response schemas
- Google-style docstrings
- No comments stating the obvious
- Prefer minimal, targeted edits over full rewrites

## Project Layout
- 3 services: BankChurn-Predictor, NLPInsight-Analyzer, ChicagoTaxi-Demand-Pipeline
- K8s: k8s/base/ (shared) + k8s/overlays/{gcp,aws}/
- Infra: infra/terraform/
- Docs: docs/ with MkDocs Material, 17 ADRs in docs/decisions/
- CI: .github/workflows/ (ci-mlops, ci-infra, deploy-gcp, deploy-aws, drift, retrain)
