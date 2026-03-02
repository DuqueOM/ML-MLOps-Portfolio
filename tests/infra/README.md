# Infrastructure Tests

Professional infrastructure validation for Terraform IaC and Kubernetes manifests.

## Test Suite Overview

| Category | Tool | Type | Scope |
|----------|------|------|-------|
| **Terraform** | `terraform fmt` | Hard gate | Canonical formatting |
| **Terraform** | `terraform validate` | Hard gate | Syntax + type checking |
| **Terraform** | `tfsec` | Advisory | Security scanning (SARIF) |
| **Terraform** | `checkov` | Advisory | Policy-as-code compliance |
| **Kubernetes** | YAML syntax | Hard gate | Parse validation |
| **Kubernetes** | `kube-linter` | Advisory | Best practices linting |
| **Kubernetes** | `conftest` (OPA) | Hard gate | Custom policy enforcement |
| **Kubernetes** | Security checks | Hard gate | Privileged containers, hostNetwork |
| **Smoke** | `pytest` + `requests` | Integration | Health, predictions, metrics |

## Quick Start

```bash
# Run all infra tests (skip smoke if services aren't running)
bash tests/infra/run_all_tests.sh --skip-smoke

# Run only Terraform tests
bash tests/infra/terraform/test_terraform.sh all    # both providers
bash tests/infra/terraform/test_terraform.sh gcp    # GCP only
bash tests/infra/terraform/test_terraform.sh aws    # AWS only

# Run only Kubernetes tests
bash tests/infra/kubernetes/test_kubernetes.sh all
bash tests/infra/kubernetes/test_kubernetes.sh base
bash tests/infra/kubernetes/test_kubernetes.sh overlays

# Run smoke tests (requires running services)
pytest tests/infra/smoke/test_smoke_services.py -v
```

## Tool Installation

```bash
# Terraform (already installed in CI)
# tfsec
curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash

# checkov
pip install checkov

# kube-linter
curl -sL https://github.com/stackrox/kube-linter/releases/download/v0.7.1/kube-linter-linux -o /usr/local/bin/kube-linter && chmod +x /usr/local/bin/kube-linter

# conftest (OPA)
LATEST=$(curl -s https://api.github.com/repos/open-policy-agent/conftest/releases/latest | grep tag_name | cut -d '"' -f 4 | sed 's/v//')
curl -sL "https://github.com/open-policy-agent/conftest/releases/download/v${LATEST}/conftest_${LATEST}_Linux_x86_64.tar.gz" | tar xz -C /usr/local/bin conftest
```

## Test Results (March 2026)

### Terraform — GCP

| Test | Status | Details |
|------|--------|---------|
| `terraform fmt` | ✅ Pass | Canonical formatting |
| `terraform validate` | ✅ Pass | All resources valid |
| `tfsec` | ✅ Advisory | 51/71 checks passed, 2 HIGH (acceptable: deprecated PodSecurityPolicy, default node pool metadata) |
| `checkov` | ✅ Advisory | 51/71 passed, 20 findings (cost/complexity trade-offs) |

### Terraform — AWS

| Test | Status | Details |
|------|--------|---------|
| `terraform fmt` | ✅ Pass | Canonical formatting |
| `terraform validate` | ✅ Pass | All resources valid |
| `tfsec` | ✅ Advisory | 84/116 checks passed, 2 CRITICAL (EKS public access restricted to VPC CIDRs), 5 HIGH (S3 uses AWS KMS, not CMK) |
| `checkov` | ✅ Advisory | 84/116 passed, 32 findings (cost trade-offs) |

### Kubernetes Manifests

| Test | Status | Details |
|------|--------|---------|
| YAML syntax (base) | ✅ Pass | 13/13 files valid |
| kube-linter (base) | ✅ Advisory | 17 findings (tuned for MLOps) |
| conftest OPA (base) | ✅ Pass | 13/13 files, 0 policy violations |
| Required resources | ✅ Pass | 6 kinds, 5 deployments |
| Security checks | ✅ Pass | No privileged containers, hostNetwork, hostPID |
| YAML syntax (AWS overlay) | ✅ Pass | 10/10 files valid |
| conftest OPA (AWS overlay) | ✅ Pass | 10/10 files, 0 violations |
| YAML syntax (GCP overlay) | ✅ Pass | 1/1 files valid |
| conftest OPA (GCP overlay) | ✅ Pass | 1/1 files, 0 violations |

## CI Integration

Infrastructure tests run automatically via `.github/workflows/ci-infra.yml` on:
- Push to `main`/`develop` (when `infra/`, `k8s/`, or `tests/infra/` change)
- Pull requests to `main`
- Manual trigger (`workflow_dispatch`)

## OPA Policies

Custom Rego policies in `kubernetes/policies/kubernetes.rego` enforce:

- **Resource limits/requests** on all containers
- **Liveness/readiness probes** on all containers
- **Namespace** required on all resources
- **App label** on Deployments
- **No LoadBalancer** services (use Ingress)
- **HPA scaleDown stabilization** to prevent flapping
- **ResourceQuota** must define CPU requests

## Security Hardening Applied

### GCP (via tfsec/checkov findings)
- Master authorized networks with VPC subnet CIDR
- Private cluster with private nodes
- Network policy (Calico) enabled
- IP aliasing (VPC-native cluster)
- Node pool: COS_CONTAINERD, auto-repair, auto-upgrade, dedicated SA
- Workload metadata protection (GKE_METADATA mode)
- VPC flow logs enabled
- Cloud SQL: TLS required, full logging flags

### AWS (via tfsec/checkov findings)
- EKS: restricted public access CIDRs, private endpoint, full audit logging
- S3: KMS encryption, public access blocks, access logging on all buckets
- ECR: immutable image tags, scan-on-push
- RDS: deletion protection, IAM authentication
- Security group: VPC-scoped egress only
