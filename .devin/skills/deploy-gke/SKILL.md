---
name: deploy-gke
description: Deploy ML service to GKE with Kustomize overlays and Workload Identity
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(docker:*)
  - Bash(gcloud:*)
  - Bash(gsutil:*)
  - Bash(kubectl:*)
  - Bash(kustomize:*)
  - Bash(curl:*)
when_to_use: >
  Use when deploying a service to GCP GKE cluster.
  Examples: 'deploy bankchurn to GKE', 'push to GCP production', 'GKE deployment'
argument-hint: "<service-name> <version-tag> [environment]"
arguments:
  - service-name
  - version-tag
  - environment
authorization_mode:
  dev: AUTO        # reversible, sandbox
  staging: CONSULT # show diff, wait for approval
  prod: STOP       # require PR + Platform Engineer approval via GitHub Environment
---

# Deploy to GKE

## Authorization Protocol

This skill enforces the Agent Behavior Protocol (AGENTS.md). Actions per environment:

| Env | Mode | What the agent does |
|-----|------|---------------------|
| `dev` | AUTO | Execute all steps without asking |
| `staging` | CONSULT | Show the full plan (image tag, diff, namespace) and wait for a human "proceed" before `kubectl apply` |
| `prod` | **STOP** | Do NOT apply. Instruct the user to merge an approved PR and let GitHub Actions with `environment: production` (required_reviewers) perform the deploy |

If you are in `prod` mode and the human insists, output:
```
[AGENT MODE: STOP]
Operation: Direct kubectl apply to production cluster
Reason: Prod deploys require the governed path (see ADR-002)
Waiting for: Merge to main + GitHub Environment approval
```
Then halt.

## Pre-Flight Checklist

- [ ] Verify context: `kubectl config current-context` must be GKE cluster
- [ ] Docker image built and pushed to Artifact Registry
- [ ] Kustomize overlay patched with correct image tag
- [ ] Terraform applied for any new infrastructure
- [ ] Model artifact uploaded to GCS
- [ ] All tests passing in CI

## Step 1: Verify Cluster Context

```bash
kubectl config current-context
# Expected: gke_{PROJECT_ID}_{REGION}_{CLUSTER_NAME}
```

NEVER proceed if context is wrong. Switch with:
```bash
gcloud container clusters get-credentials {CLUSTER} --region {REGION} --project {PROJECT}
```

## Step 2: Build and Push Image

```bash
# Tag with version and SHA
export VERSION=v{X.Y.Z}
export SHA=$(git rev-parse --short HEAD)
export REGISTRY={REGION}-docker.pkg.dev/{PROJECT_ID}/{REPO}

docker build -t ${REGISTRY}/{service}:${VERSION} -t ${REGISTRY}/{service}:sha-${SHA} .
docker push ${REGISTRY}/{service}:${VERSION}
docker push ${REGISTRY}/{service}:sha-${SHA}
```

## Step 3: Update Kustomize Overlay

```bash
# k8s/overlays/gcp-{env}/kustomization.yaml  (env = dev | staging | production)
images:
  - name: {service}-predictor
    newName: {REGION}-docker.pkg.dev/{PROJECT_ID}/{REPO}/{service}
    newTag: {VERSION}
```

## Step 4: Apply Manifests

```bash
# Apply the overlay matching the target environment.
# Production deploys are gated by the dev → staging → prod chain (ADR-011);
# manual application here is for dev iteration or emergency only.
kubectl apply -k k8s/overlays/gcp-{env}/    # env = dev | staging | production
kubectl rollout status deployment/{service}-predictor -n {namespace} --timeout=300s
```

## Step 5: Smoke Test

```bash
# Get service URL
export SVC_URL=$(kubectl get ingress -n {namespace} -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')

# Health check
curl -f http://${SVC_URL}/health
curl -f http://${SVC_URL}/ready

# Test prediction with a schema-valid scaffold payload. Add
# `-H "X-API-Key: ${API_KEY}"` when API_AUTH_ENABLED=true.
curl -X POST http://${SVC_URL}/predict \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "deploy-smoke-001",
    "slice_values": {"smoke": "gke"},
    "feature_a": 42.0,
    "feature_b": 50000.0,
    "feature_c": "category_A"
  }'

# Metrics scrape smoke
curl -s http://${SVC_URL}/metrics | grep "_requests_total"
```

## Step 6: Verify Monitoring

- [ ] Prometheus scraping `/metrics` from new pods
- [ ] Grafana dashboard showing new version
- [ ] No alert firing in AlertManager

## Rollback (if needed)

```bash
kubectl rollout undo deployment/{service}-predictor -n {namespace}
kubectl rollout status deployment/{service}-predictor -n {namespace}
```

## Workload Identity Verification

```bash
# Verify SA annotation
kubectl get serviceaccount {service}-sa -n {namespace} -o yaml | grep "iam.gke.io"

# Test GCS access from pod
kubectl exec -it {pod} -n {namespace} -- gsutil ls gs://{model-bucket}/
```
