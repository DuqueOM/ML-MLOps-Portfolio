---
name: deploy-aws
description: Guides deployment of ML services to Amazon EKS with IRSA authentication, Kustomize overlays, ECR image management, smoke tests, and rollback procedures.
---

## Pre-Deployment Checklist

1. **Verify CI status**: All checks on `main` branch must be green
2. **Verify cluster context**: `kubectl config current-context` must show EKS cluster
3. **Verify Docker images**: Images tagged and pushed to ECR
4. **Verify model artifacts**: Models uploaded to S3 bucket
5. **Verify IRSA**: ServiceAccount annotations match IAM role ARN

## Deployment Steps

### 1. Authenticate and Set Context
```bash
aws eks update-kubeconfig \
  --region us-east-1 \
  --name ml-portfolio-eks-production \
  --alias eks-ml-portfolio

kubectl config current-context
# Expected: eks-ml-portfolio
```

### 2. Verify IRSA Configuration
```bash
kubectl get sa -n default -o yaml | grep eks.amazonaws.com/role-arn
# Must show the correct IAM role ARN for S3 model access
```

### 3. Update Image Tags
Edit `k8s/overlays/aws/` patches to reference ECR image URIs:
```
<account-id>.dkr.ecr.us-east-1.amazonaws.com/bankchurn-predictor:v${VERSION}
<account-id>.dkr.ecr.us-east-1.amazonaws.com/nlpinsight-analyzer:v${VERSION}
<account-id>.dkr.ecr.us-east-1.amazonaws.com/chicagotaxi-demand:v${VERSION}
```

### 4. Dry Run
```bash
kubectl apply -k k8s/overlays/aws/ --dry-run=client
```

### 5. Apply
```bash
kubectl apply -k k8s/overlays/aws/
```

### 6. Watch Rollout
```bash
kubectl rollout status deployment/bankchurn-predictor -w
kubectl rollout status deployment/nlpinsight-analyzer -w
kubectl rollout status deployment/chicagotaxi-demand -w
```

### 7. Smoke Tests
```bash
# Get NodePort or LoadBalancer IP
kubectl get svc
./scripts/smoke_test.sh --target eks
```

### 8. Verify HPA
```bash
kubectl get hpa
# CPU-only metrics (ADR-001), no memory metrics
```

## EKS-Specific Considerations

| Aspect | GKE | EKS | ADR |
|--------|-----|-----|-----|
| Auth to storage | Workload Identity → GCS | IRSA → S3 | — |
| Image registry | Artifact Registry | ECR | — |
| Node type | e2-medium (shared) | t3.medium (burst) | ADR-016 |
| Load balancer | GKE Ingress | Classic ELB / NodePort | — |
| Cost | ~$24/mo | ~$145/mo | ADR-016 |

## Rollback Procedure

See `checklist.md` in this skill directory for the full rollback and IRSA troubleshooting.

## Cross-References
- For GKE deployment: invoke `deploy-gke` skill
- For performance comparison: see ADR-016 (GCP/AWS parity)
- For release process: use `/release` workflow
