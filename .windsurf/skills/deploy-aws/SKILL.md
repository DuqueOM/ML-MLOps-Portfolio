---
name: deploy-aws
description: Deploy ML service to EKS with Kustomize overlays and IRSA
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(docker:*)
  - Bash(aws:*)
  - Bash(kubectl:*)
  - Bash(kustomize:*)
  - Bash(curl:*)
when_to_use: >
  Use when deploying a service to AWS EKS cluster.
  Examples: 'deploy to EKS', 'push to AWS production', 'EKS deployment'
argument-hint: "<service-name> <version-tag> [environment]"
arguments:
  - service-name
  - version-tag
  - environment
authorization_mode:
  dev: AUTO
  staging: CONSULT
  prod: STOP
---

# Deploy to EKS

## Authorization Protocol

This skill enforces the Agent Behavior Protocol (AGENTS.md).

| Env | Mode | What the agent does |
|-----|------|---------------------|
| `dev` | AUTO | Execute all steps |
| `staging` | CONSULT | Show diff + image tag + namespace, wait for approval before `kubectl apply` |
| `prod` | **STOP** | Never apply directly. Require merge to `main` + GitHub Environment `production` approval |

On `prod` invocation, emit:
```
[AGENT MODE: STOP]
Operation: Direct kubectl apply to EKS production
Reason: Prod deploys flow through GitHub Actions with required_reviewers (ADR-002)
```
and halt.

## Pre-Flight Checklist

- [ ] Verify context: `kubectl config current-context` must be EKS cluster
- [ ] Docker image built and pushed to ECR
- [ ] Kustomize overlay patched with correct image tag
- [ ] Terraform applied for any new infrastructure
- [ ] Model artifact uploaded to S3
- [ ] All tests passing in CI

## Step 1: Verify Cluster Context

```bash
kubectl config current-context
# Expected: arn:aws:eks:{REGION}:{ACCOUNT}:cluster/{CLUSTER_NAME}
```

Switch context:
```bash
aws eks update-kubeconfig --name {CLUSTER} --region {REGION}
```

## Step 2: Build and Push Image

```bash
export VERSION=v{X.Y.Z}
export SHA=$(git rev-parse --short HEAD)
export REGISTRY={ACCOUNT}.dkr.ecr.{REGION}.amazonaws.com/{REPO}

# Authenticate to ECR
aws ecr get-login-password --region {REGION} | docker login --username AWS --password-stdin ${REGISTRY}

docker build -t ${REGISTRY}/{service}:${VERSION} -t ${REGISTRY}/{service}:sha-${SHA} .
docker push ${REGISTRY}/{service}:${VERSION}
docker push ${REGISTRY}/{service}:sha-${SHA}
```

## Step 3: Update Kustomize Overlay

```yaml
# k8s/overlays/aws-{env}/kustomization.yaml  (env = dev | staging | production)
images:
  - name: {service}-predictor
    newName: {ACCOUNT}.dkr.ecr.{REGION}.amazonaws.com/{REPO}/{service}
    newTag: {VERSION}
```

## Step 4: Apply Manifests

```bash
# Apply the overlay matching the target environment.
# Production deploys are gated by the dev → staging → prod chain (ADR-011);
# manual application here is for dev iteration or emergency only.
kubectl apply -k k8s/overlays/aws-{env}/    # env = dev | staging | production
kubectl rollout status deployment/{service}-predictor -n {namespace} --timeout=300s
```

## Step 5: Smoke Test

```bash
export SVC_URL=$(kubectl get svc {service}-service -n {namespace} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

curl -f http://${SVC_URL}/health
curl -f http://${SVC_URL}/ready

# Test prediction with a schema-valid scaffold payload. Add
# `-H "X-API-Key: ${API_KEY}"` when API_AUTH_ENABLED=true.
curl -X POST http://${SVC_URL}/predict \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "deploy-smoke-001",
    "slice_values": {"smoke": "aws"},
    "feature_a": 42.0,
    "feature_b": 50000.0,
    "feature_c": "category_A"
  }'

# Metrics scrape smoke
curl -s http://${SVC_URL}/metrics | grep "_requests_total"
```

## Step 6: Verify IRSA

```bash
# Check SA annotation
kubectl get serviceaccount {service}-sa -n {namespace} -o yaml | grep "eks.amazonaws.com/role-arn"

# Test S3 access from pod
kubectl exec -it {pod} -n {namespace} -- aws s3 ls s3://{model-bucket}/
```

## IRSA Troubleshooting

If S3 access fails:
1. Verify OIDC provider: `aws eks describe-cluster --name {CLUSTER} --query "cluster.identity.oidc"`
2. Verify trust policy on the IAM role allows the service account
3. Verify the role has S3 read permissions on the model bucket
4. Restart the pod (IRSA tokens are injected at pod creation)

## Rollback

```bash
kubectl rollout undo deployment/{service}-predictor -n {namespace}
kubectl rollout status deployment/{service}-predictor -n {namespace}
```
