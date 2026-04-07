---
name: deploy-gke
description: Guides deployment of ML services to Google Kubernetes Engine (GKE) with safety checks, Kustomize overlays, smoke tests, and rollback procedures.
---

## Pre-Deployment Checklist

1. **Verify CI status**: All checks on `main` branch must be green
2. **Verify cluster context**: `kubectl config current-context` must show GKE cluster
3. **Verify Docker images**: Images tagged and pushed to Artifact Registry
4. **Verify model artifacts**: Models uploaded to GCS bucket

## Deployment Steps

### 1. Authenticate and Set Context
```bash
gcloud container clusters get-credentials ml-portfolio-gke-production \
  --region us-central1 \
  --project ml-portfolio-duque-om-202602

kubectl config current-context
# Expected: gke_ml-portfolio-duque-om-202602_us-central1_ml-portfolio-gke-production
```

### 2. Update Image Tags
Edit `k8s/base/` deployment manifests to reference new image tags:
- `bankchurn-predictor-deployment.yaml`
- `nlpinsight-analyzer-deployment.yaml`
- `chicagotaxi-demand-deployment.yaml`

### 3. Dry Run
```bash
kubectl apply -k k8s/overlays/gcp/ --dry-run=client
```

### 4. Apply
```bash
kubectl apply -k k8s/overlays/gcp/
```

### 5. Watch Rollout
```bash
kubectl rollout status deployment/bankchurn-predictor -w
kubectl rollout status deployment/nlpinsight-analyzer -w
kubectl rollout status deployment/chicagotaxi-demand -w
```

### 6. Smoke Tests
```bash
./scripts/smoke_test.sh
```

### 7. Verify HPA
```bash
kubectl get hpa
# All HPAs should show TARGETS with CPU metrics (no memory)
```

## Rollback Procedure

See `checklist.md` in this skill directory for the full rollback procedure.

## Key Reminders
- Single-worker uvicorn only (ADR-014)
- CPU-only HPA (ADR-001)
- Workload Identity for GCS access (no service account keys)
