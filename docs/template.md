# ML-MLOps Production Template

## The Project I Am Most Proud Of

The [ML-MLOps Production Template](https://github.com/DuqueOM/ML-MLOps-Production-Template)
is a reusable starter framework for machine learning services that need more
than a notebook.

It came from building this portfolio and asking: if I had to start the next ML
service tomorrow, what mistakes would I want to avoid from day one?

## Why It Matters

The template is not only a collection of files. It is a packaged set of lessons:

- how to structure a FastAPI model service;
- how to keep model artifacts out of Docker images;
- how to track experiments and model versions;
- how to add CI/CD and validation early;
- how to prepare deployment manifests for Kubernetes;
- how to document decisions so a future teammate can understand them;
- how to keep AI-assisted development inside safe, reviewable rules.

For non-technical readers: it is like a checklist and starter kit for building
ML services with fewer avoidable mistakes.

For technical reviewers: it includes service scaffolding, Kubernetes/Terraform
patterns, MLflow hooks, drift and retraining workflows, CI validation, security
checks, and an agent behavior protocol.

## What It Shows About Me

| Signal | What it means |
|--------|---------------|
| Product thinking | I turned a personal portfolio into a reusable tool others could start from. |
| Operational mindset | The template focuses on reliability, deployment, monitoring, and handoffs. |
| Documentation discipline | Decisions, runbooks, and rules are written down, not hidden in memory. |
| Safety awareness | Secrets, image scanning, model promotion, and deployment guardrails are treated as first-class concerns. |
| Learning velocity | I used the portfolio lessons to create a stronger second system. |

## Key Capabilities

| Area | Examples |
|------|----------|
| Service foundation | FastAPI, model loading, health/readiness checks, tests. |
| ML workflow | MLflow experiment tracking, model registry patterns, model versioning. |
| Deployment path | Docker, Kubernetes, Kustomize, Terraform examples for GCP and AWS. |
| CI/CD | GitHub Actions validation, smoke checks, security scans. |
| Monitoring | Prometheus/Grafana patterns, drift checks, retraining hooks. |
| Governance | AUTO / CONSULT / STOP workflow rules for safe agent-assisted engineering. |

## Where To Go Next

- [Template repository](https://github.com/DuqueOM/ML-MLOps-Production-Template)
- [Quick Start](https://github.com/DuqueOM/ML-MLOps-Production-Template/blob/main/QUICK_START.md)
- [Architecture decisions](https://github.com/DuqueOM/ML-MLOps-Production-Template/tree/main/docs/decisions)
- [Technical evidence from this portfolio](technical-evidence.md)
