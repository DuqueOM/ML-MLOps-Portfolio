# ADR-002: emptyDir for Model Storage in Kubernetes

**Status**: Accepted  
**Date**: 2026-02-18  
**Decision Makers**: DuqueOM

## Context

ML models (~4-6MB each) need to be available inside pods at startup. Options considered:
1. **PersistentVolumeClaim (PVC)** — persistent storage across pod restarts
2. **emptyDir + Init Container** — ephemeral, download from GCS on each start
3. **Bake into Docker image** — models inside the image

## Decision

Use `emptyDir` volumes with Init Containers that download models from GCS at pod startup.

## Rationale

- Models are small (4-6MB), GCS download takes 2-5s → negligible startup overhead
- Cost: $0.00005/startup vs $10/month for PVC
- Model updates = ConfigMap change (GCS path), not Docker rebuild
- Init Container uses `python:3.11-alpine` (50MB) — no gcloud SDK bloat

## Consequences

- **Positive**: Decoupled model versioning from Docker images
- **Positive**: Zero persistent storage cost
- **Negative**: Models re-downloaded on every pod restart (acceptable for <10MB)

## Revisit When

Models exceed 500MB or pods restart more than 1/hour.
