# EKS Deployment Checklist & Rollback

## Pre-Deploy Verification

- [ ] CI pipeline green on `main`
- [ ] `kubectl config current-context` shows EKS cluster
- [ ] Docker images built, tagged, and pushed to ECR
- [ ] Model artifacts uploaded to S3
- [ ] IRSA ServiceAccount annotations correct
- [ ] Version bumped in overlay patches
- [ ] CHANGELOG.md updated

## Post-Deploy Verification

- [ ] All pods Running (no CrashLoopBackOff)
- [ ] All deployments at desired replica count
- [ ] Smoke tests pass (`./scripts/smoke_test.sh --target eks`)
- [ ] HPA showing CPU metrics only (no memory — ADR-001)
- [ ] Pods can access S3 via IRSA (check model loading logs)
- [ ] Classic ELB / NodePort accessible

## Rollback Procedure

### Quick Rollback
```bash
kubectl rollout undo deployment/bankchurn-predictor
kubectl rollout undo deployment/nlpinsight-analyzer
kubectl rollout undo deployment/chicagotaxi-demand
```

### Targeted Rollback
```bash
kubectl rollout history deployment/bankchurn-predictor
kubectl rollout undo deployment/bankchurn-predictor --to-revision=<N>
```

## IRSA Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `AccessDenied` on S3 | IRSA role policy missing | Add `s3:GetObject` for model bucket |
| Pod can't assume role | ServiceAccount annotation wrong | Check `eks.amazonaws.com/role-arn` |
| OIDC provider mismatch | Cluster OIDC not configured | `eksctl utils associate-iam-oidc-provider` |
| Credential chain error | AWS SDK version mismatch | Check boto3/botocore pinning |

## Emergency Access
- AWS Console: EKS → Clusters → ml-portfolio-eks-production
- CloudWatch Logs: `/aws/eks/ml-portfolio-eks-production/cluster`
- ECR: `<account-id>.dkr.ecr.us-east-1.amazonaws.com/`
