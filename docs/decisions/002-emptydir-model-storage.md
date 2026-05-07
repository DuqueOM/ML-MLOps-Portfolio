# ADR-002: emptyDir + Init Container for Model Storage in Kubernetes

- **Status**: Accepted
- **Date**: 2026-02-18
- **Authors**: Duque Ortega Mutis

> **TL;DR**: Models are downloaded from cloud object storage (GCS/S3) into ephemeral `emptyDir` volumes at pod startup via Init Containers. This decouples model versioning from Docker images — a model update is a ConfigMap change, not an image rebuild.

---

## Context

Each ML service requires its trained model artifact at startup. The artifacts are small:

| Service | Artifact | Size | Format |
|---------|----------|------|--------|
| BankChurn | StackingClassifier pipeline | 4.1 MB | `model.joblib` |
| NLPInsight | TF-IDF + LogReg (production) / FinBERT (GPU backend) | ~5 MB / ~440 MB | `model.joblib` / `model.tar.gz` |
| ChicagoTaxi | RandomForest + predictions | ~2 MB | `model.joblib` |

The key design question: **where should the model live relative to the container lifecycle?**

---

## Decision

Use **`emptyDir` volumes** with **Init Containers** that download models from cloud object storage (GCS on GKE, S3 on EKS) before the main container starts.

### Architecture

```
Pod startup
  │
  ├─ Init Container (python:3.11-alpine, 50MB)
  │    ├─ Reads GCS_BUCKET, GCS_MODEL_PATH from ConfigMap
  │    ├─ Downloads model.joblib → /models/model.joblib
  │    └─ Exits (container destroyed, volume persists)
  │
  └─ Main Container (FastAPI app)
       └─ Reads /models/model.joblib from shared emptyDir volume
```

### Model Path Configuration

Each service has a dedicated ConfigMap (`k8s/model-configmaps.yaml`) specifying:
- `GCS_BUCKET` / `S3_BUCKET` — cloud storage bucket name
- `GCS_MODEL_PATH` / `S3_MODEL_PATH` — path within bucket (e.g., `bankchurn/model.joblib`)
- `LOCAL_MODEL_PATH` — mount path inside pod (`/models/model.joblib`)

**Updating a model** requires only: upload new artifact to GCS/S3, then `kubectl rollout restart deployment/<service>`. No Docker rebuild.

---

## Alternatives Considered

| Option | Cost | Startup Overhead | Model Update Strategy | Verdict |
|--------|------|-----------------|----------------------|---------|
| **PersistentVolumeClaim (PVC)** | ~$10/mo per PV | None (already mounted) | Upload to PV (requires write access) | Rejected — persistent cost for <10MB artifacts; complicates multi-cloud (PV provisioners differ) |
| **Bake into Docker image** | $0 | None | Full Docker rebuild + push + rolling update | Rejected — couples model version to image version; 10-min rebuild cycle for a 4MB file change |
| **emptyDir + Init Container** ✅ | ~$0.00005/startup | 2-5s (GCS/S3 download) | ConfigMap change + rollout restart | **Selected** — zero persistent cost, decoupled versioning |
| **CSI ephemeral volume (GCS FUSE / Mountpoint for S3)** | $0 | 1-2s (FUSE mount) | Automatic (reads latest from bucket) | Deferred — requires CSI driver installation; adds cluster dependency |

### Why Not Bake Models into Docker Images?

In production ML, **model release cadence ≠ code release cadence**. Models may be retrained weekly (via drift detection — see [ADR-006](006-drift-triggered-retraining.md)), while application code changes monthly. Coupling them forces unnecessary image rebuilds and increases deployment risk.

---

## Implementation Details

**Init Container** (`scripts/download-model.py`):
- Uses `google-cloud-storage` (GCS) or `boto3` (S3) — no gcloud/awscli SDK bloat
- 3 retries with 10s exponential backoff
- Validates downloaded file size > 0 before exiting
- NLPInsight handles `model.tar.gz` extraction (transformer model directory)

**Standardized model path**: All 3 services use `models/model.joblib` as the canonical path, configurable via `MODEL_PATH` environment variable.

---

## Consequences

- **Positive**: Model versioning fully decoupled from Docker images — deploy new model in <30s
- **Positive**: Zero persistent storage cost ($0 vs $10+/mo for PVC)
- **Positive**: Same pattern works on GKE (GCS) and EKS (S3) — only ConfigMap values differ
- **Positive**: Init Container is disposable — `python:3.11-alpine` (50MB) is destroyed after download
- **Negative**: Models re-downloaded on every pod restart (acceptable for <10MB; GCS/S3 latency is 2-5s)
- **Negative**: Pod startup depends on cloud storage availability (mitigated by retries)

## Revisit When

- Model artifacts exceed 500MB (consider CSI FUSE mount or PVC)
- Pod restart frequency exceeds 1/hour (download cost becomes significant)
- Model registry (MLflow) supports direct K8s integration for model serving

---

## References

- [ADR-006: Drift-Triggered Retraining](006-drift-triggered-retraining.md) — model update trigger
- [Kubernetes Init Containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)
- [GCS FUSE CSI Driver](https://cloud.google.com/kubernetes-engine/docs/how-to/persistent-volumes/cloud-storage-fuse-csi-driver)
