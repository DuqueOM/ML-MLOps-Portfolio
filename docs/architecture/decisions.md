# Architectural Decision Records

Key technical decisions with rationale. Written for technical reviewers and hiring managers.

**Last Updated**: March 2026 | **Portfolio Version**: 3.2.0

> **Granular ADRs**: See [`docs/decisions/`](../decisions/) for detailed per-decision records (ADR-001 through ADR-005).

---

## Summary

| # | Decision | Choice | Key Rationale | Revisit When |
|---|----------|--------|---------------|--------------|
| 001 | K8s Storage | emptyDir ephemeral | Models ~4MB, GCS download 2-5s, $0.00005/startup | Models >500MB |
| 002 | Init Container | python:3.11-alpine + pinned deps | 50MB image, no gcloud SDK bloat, pip at runtime | Pods recreate >1/hour |
| 003 | Model Versioning | ConfigMaps separate from Deployments | Model updates = config change, not infra change | Adopt MLflow Registry |
| 004 | Download Resilience | 3 retries, 10s backoff | Handles GCS transient 503s, clean CrashLoopBackOff | N/A |
| 005 | GKE Cluster | e2-medium × 3 nodes | ~$25/node, 4GB RAM fits all pods, 91% savings vs e2-standard-4 | Need dedicated vCPUs |
| 006 | Networking | Custom VPC, private subnets | Single-region (us-central1), VPC peering for Cloud SQL | Multi-region needed |
| 007 | Ingress | GCE-native Load Balancer | Managed, path-based routing, single IP, $18/mo | Need NGINX/Istio features |
| 008 | Docker Images | Multi-stage builds | 1.2GB→400-500MB, no build tools in prod, non-root | N/A |
| 009 | Serialization | Joblib over Pickle | 60-80% compression, numpy-optimized, safer | N/A |
| 010 | Model Selection | Auto-selection pipeline | Compare RF/XGB/LGB, select best by primary metric | Add neural network |
| 011 | Experiment Tracking | Self-hosted MLflow on GKE | Full control, 9 runs tracked, Cloud SQL backend | SaaS MLflow alternative |
| 012 | Monitoring | Prometheus + Grafana on GKE | 15s scrape, 10-panel dashboard, auto-provisioned | Managed monitoring |
| 013 | CI/CD | GitHub Actions matrix | 3 projects × Python versions, security + docker + integration | N/A |
| 014 | Container Registry | GCP Artifact Registry | Regional, cleanup policies, integrated with GKE | Multi-cloud registry |
| 015 | Storage | GCS with lifecycle policies | Versioned, Nearline after 90d, public access prevention | N/A |
| 016 | IaC | Terraform with remote state | GCP + AWS modules, `terraform plan` = no drift | N/A |
| 017 | Security | Defense in depth | Trivy + Bandit + Gitleaks + non-root + Workload Identity | N/A |

## HPA Design Decision

CPU-only autoscaling for all ML services. Memory-based HPA removed because ML models have fixed RAM footprint (model loaded at startup). Memory never decreases → HPA never scales down. CPU correlates with request traffic → correct scaling signal.

| Service | CPU Target | Pods | Scale-down | Scale-up |
|---------|-----------|------|------------|----------|
| BankChurn | 70% | 1–3 | 300s / 50% | 60s / max(100%, +2) |
| CarVision | 70% | 1–3 | 300s / 50% | 60s / max(100%, +2) |
| NLPInsight | 75% | 1–3 | 300s / 50% | 60s / max(100%, +2) |

---

*Last Updated: March 2026*
