# ADR-013: Multi-Cloud Parity Policy (GKE vs EKS)

- **Status**: Accepted
- **Date**: 2026-03-13
- **Authors**: Duque Ortega Mutis
- **Related**: [ADR-016](016-gcp-aws-performance-parity.md) (performance trade-off)

> **TL;DR**: Maintain functional parity (all ML services, monitoring, CI/CD, IaC) across GCP and AWS while accepting intentional infrastructure asymmetries (instance types, node counts, ingress controllers). Node counts are autoscaler-managed, not hard-coded — the right answer differs per cloud.

## Decision

We accept **intentional asymmetries** between cloud environments while maintaining **functional parity** on all ML-critical workloads.

### Functional Parity (must match)

| Component | GCP (GKE) | AWS (EKS) | Status |
|-----------|-----------|-----------|--------|
| ML services (3 APIs) | ✅ Running | ✅ Running | Parity |
| SHAP explainability | ✅ Working | ✅ Working | Parity |
| Prometheus + Grafana | ✅ Running | ✅ Running | Parity |
| MLflow tracking | ✅ Running | ✅ Running | Parity |
| Drift detection CronJob | ✅ Completing | ✅ Completing | Parity (2026-03-13) |
| CI/CD (GitHub Actions) | ✅ deploy-gcp.yml | ✅ deploy-aws.yml | Parity |
| IaC (Terraform) | ✅ infra/terraform/gcp | ✅ infra/terraform/aws | Parity |

### Accepted Asymmetries

| Dimension | GCP | AWS | Rationale |
|-----------|-----|-----|-----------|
| Node count | 4 | 3 | Different instance sizes (e2-medium vs t3.medium); autoscaler decides independently per cloud |
| Instance memory | 4 GB/node | 4 GB/node | Both use 4GB instances; node count differs based on bin-packing |
| Ingress | GCE Ingress (L7 LB) | nginx-ingress (Classic ELB) | Both use real LoadBalancer; cloud-specific LB type |
| Container registry | Artifact Registry | ECR (private) | Cloud-native equivalents |
| Object storage | GCS | S3 | Cloud-native equivalents |
| Drift detection | Jobs complete | Jobs complete | Parity achieved (2026-03-13) |

### Node Count Philosophy

The autoscaler operates **independently per cloud** based on:
- Available memory per node (GKE e2-medium 4GB vs EKS t3.medium 4GB)
- Pod resource requests and bin-packing efficiency
- Cloud-specific overhead (kube-system, CNI, etc.)

**Professional pattern**: Node counts should never be hard-coded equal across clouds. The autoscaler's job is to right-size per environment.

## Consequences

- Drift detection on AWS requires a follow-up fix (resource constraints or endpoint accessibility)
- Node count differences are expected and not a parity violation
- Ingress type difference is documented as a temporary AWS account limitation
- All ML-critical paths (predict, explain, health, metrics) work identically on both clouds
