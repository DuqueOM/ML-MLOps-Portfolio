---
trigger: glob
globs: "k8s/**/*.yaml,k8s/**/*.yml,helm/**/*.yaml,helm/**/*.yml"
---

# Kubernetes & Helm Conventions

## Structure
- `k8s/base/` contains shared manifests (Deployments, Services, ConfigMaps, HPAs)
- `k8s/overlays/gcp/` for GKE-specific patches (Workload Identity annotations)
- `k8s/overlays/aws/` for EKS-specific patches (IRSA annotations)
- `helm/ml-portfolio/` for Helm chart (3 services + HPA + drift CronJob)
- Always use Kustomize: `kubectl apply -k k8s/overlays/{gcp|aws}/`

## Labels (required on all resources)
- `app: <service-name>` (e.g., bankchurn-predictor)
- `version: <semver>` (e.g., v3.6.0)
- `environment: <env>` (production, staging)
- `managed-by: kustomize`

## HPA Rules — CPU-ONLY (ADR-001)

**NEVER** add memory metrics to HPA — ML models have fixed RAM footprint, making memory-based
HPA mathematically unable to scale down (verified incident: 3 pods stuck for hours post-load).

| Service | CPU Target | Min Pods | Max Pods | scaleUp Stabilization |
|---------|-----------|---------|---------|----------------------|
| BankChurn-Predictor | **50%** | 1 | 5 | 30s |
| NLPInsight-Analyzer | **60%** | 1 | 3 | 30s |
| ChicagoTaxi-Demand-Pipeline | **60%** | 1 | 3 | 30s |

> Thresholds were refined from 70–75% → 50–60% by ADR-014 to ensure earlier scale-out for
> CPU-bound inference. If you see 70% or 75% anywhere, that is the pre-ADR-014 value — update it.

## Pod Spec
- **Single-worker uvicorn (workers=1)** — NEVER use `--workers >1` under K8s (ADR-014)
  - Multiple workers share the pod's CPU budget → thrashing, not parallelism
  - Horizontal scaling is the K8s-native approach (via HPA)
- Resource requests/limits MUST be set for both CPU and memory
- Liveness: `/health`, readiness: `/health`, startup probe with `failureThreshold=30`
- Model artifacts delivered via `emptyDir` volume + Init Container from GCS/S3 (ADR-002)

## Init Container Pattern
```yaml
initContainers:
  - name: model-downloader
    image: python:3.11-alpine
    command: ["python", "/scripts/download-model.py"]
    volumeMounts:
      - name: model-volume
        mountPath: /models
volumes:
  - name: model-volume
    emptyDir: {}
```

## Safety
- ALWAYS run `kubectl config current-context` before any apply/delete/patch
- NEVER apply to production without verifying the correct cluster context
- Use `--dry-run=client` for validation before actual apply
- Use `kubectl rollout status` to confirm deployments complete successfully