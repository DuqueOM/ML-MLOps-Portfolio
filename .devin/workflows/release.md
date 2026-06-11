---
description: Full multi-cloud release process — build, deploy GCP + AWS, verify, rollback if needed
---

# /release Workflow

## 1. Pre-Release Checks

Verify all CI checks are green:
```bash
gh run list --workflow=ci.yml --limit=1
```
// turbo

## 2. Run Full Test Suite

```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```

## 3. Tag the Release

```bash
git tag -a v{VERSION} -m "Release v{VERSION}: {summary}"
git push origin v{VERSION}
```

## 4. Build and Push Docker Images (GCP)

For each service in the project:
```bash
docker build -t ${GCP_REGISTRY}/${SERVICE}:v{VERSION} ${SERVICE}/
docker push ${GCP_REGISTRY}/${SERVICE}:v{VERSION}
```

## 5. Build and Push Docker Images (AWS)

```bash
aws ecr get-login-password | docker login --username AWS --password-stdin ${AWS_REGISTRY}
docker build -t ${AWS_REGISTRY}/${SERVICE}:v{VERSION} ${SERVICE}/
docker push ${AWS_REGISTRY}/${SERVICE}:v{VERSION}
```

## 6. Deploy to GKE

```bash
kubectl config use-context ${GKE_CONTEXT}
kubectl apply -k k8s/overlays/gcp-prod/
kubectl rollout status deployment --all -n ${NAMESPACE} --timeout=300s
```

## 7. Smoke Test GCP

```bash
curl -f http://${GCP_ENDPOINT}/health
curl -X POST http://${GCP_ENDPOINT}/predict -H "Content-Type: application/json" -d '${TEST_PAYLOAD}'
```

## 8. Deploy to EKS

```bash
kubectl config use-context ${EKS_CONTEXT}
kubectl apply -k k8s/overlays/aws-prod/
kubectl rollout status deployment --all -n ${NAMESPACE} --timeout=300s
```

## 9. Smoke Test AWS

```bash
curl -f http://${AWS_ENDPOINT}/health
curl -X POST http://${AWS_ENDPOINT}/predict -H "Content-Type: application/json" -d '${TEST_PAYLOAD}'
```

## 10. Post-Deploy Verification

- Check Grafana dashboards show new version
- Check Prometheus scraping all services
- Check AlertManager has no active P1/P2 alerts
- Verify HPA is functioning correctly

## 11. Rollback (if needed)

```bash
# GKE
kubectl config use-context ${GKE_CONTEXT}
kubectl rollout undo deployment --all -n ${NAMESPACE}

# EKS
kubectl config use-context ${EKS_CONTEXT}
kubectl rollout undo deployment --all -n ${NAMESPACE}
```

## 12. Update Documentation

- Update CHANGELOG.md
- Close related GitHub Issues
- Update cost projections if resources changed
