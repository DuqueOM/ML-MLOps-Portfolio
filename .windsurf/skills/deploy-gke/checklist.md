# GKE Deployment Checklist & Rollback

## Pre-Deploy Verification

- [ ] CI pipeline green on `main`
- [ ] `kubectl config current-context` shows GKE cluster
- [ ] Docker images built, tagged, and pushed to Artifact Registry
- [ ] Model artifacts uploaded to GCS
- [ ] Version bumped in deployment manifests
- [ ] CHANGELOG.md updated

## Post-Deploy Verification

- [ ] All pods Running (no CrashLoopBackOff)
- [ ] All deployments at desired replica count
- [ ] Smoke tests pass (`./scripts/smoke_test.sh`)
- [ ] HPA showing CPU metrics (no memory metrics)
- [ ] Prometheus scraping new pods
- [ ] Grafana dashboards showing traffic

## Rollback Procedure

### Quick Rollback (undo last deployment)
```bash
kubectl rollout undo deployment/bankchurn-predictor
kubectl rollout undo deployment/nlpinsight-analyzer
kubectl rollout undo deployment/chicagotaxi-demand
```

### Targeted Rollback (to specific revision)
```bash
kubectl rollout history deployment/bankchurn-predictor
kubectl rollout undo deployment/bankchurn-predictor --to-revision=<N>
```

### Full Rollback (revert to previous Git tag)
```bash
git checkout v<previous-version>
kubectl apply -k k8s/overlays/gcp/
./scripts/smoke_test.sh
```

## Emergency Contacts
- GCP Console: https://console.cloud.google.com/kubernetes/list?project=ml-portfolio-duque-om-202602
- Grafana: Port-forward `kubectl port-forward svc/grafana 3000:3000`
- Prometheus: Port-forward `kubectl port-forward svc/prometheus 9090:9090`
