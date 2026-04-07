---
trigger: glob
globs: "k8s/**/*.yaml,k8s/**/*.yml"
---

# Kubernetes Conventions

## Structure
- k8s/base/ contains shared manifests (Deployments, Services, ConfigMaps)
- k8s/overlays/gcp/ for GKE-specific patches (Workload Identity annotations)
- k8s/overlays/aws/ for EKS-specific patches (IRSA annotations)
- Always use Kustomize: `kubectl apply -k k8s/overlays/{gcp|aws}/`

## Labels (required on all resources)
- `app: <service-name>` (e.g., bankchurn-predictor)
- `version: <semver>` (e.g., v3.0.0)
- `environment: <env>` (production, staging)
- `managed-by: kustomize`

## HPA Rules
- CPU-only scaling — NEVER add memory metrics (ADR-001)
- BankChurn: targetCPUUtilizationPercentage 70, min 1, max 5
- NLPInsight: targetCPUUtilizationPercentage 70, min 1, max 3
- ChicagoTaxi: targetCPUUtilizationPercentage 70, min 1, max 3

## Pod Spec
- Single-worker uvicorn (workers=1) — NEVER use --workers >1 (ADR-014)
- Resource requests/limits must be set for CPU and memory
- Liveness: /health, readiness: /health, startup probe with failureThreshold=30
- Model download via init container or emptyDir mount (ADR-002)

## Safety
- ALWAYS run `kubectl config current-context` before any apply/delete
- NEVER apply to production without verifying the correct cluster
- Use `--dry-run=client` for validation before actual apply
