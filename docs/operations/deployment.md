# Deployment Guide

## Local (Docker Compose)

```bash
bash scripts/setup_demo_models.sh                    # First time only
docker compose -f docker-compose.demo.yml up -d --build
docker compose -f docker-compose.demo.yml ps          # Verify
```

| Service | Port | Health Check |
|---------|------|--------------|
| BankChurn API | 8001 | `curl localhost:8001/health` |
| CarVision API | 8002 | `curl localhost:8002/health` |
| NLPInsight API | 8003 | `curl localhost:8003/health` |
| CarVision Dashboard | 8501 | `curl localhost:8501` |
| MLflow | 5000 | `curl localhost:5000/health` |

## Production (GKE)

```bash
# 1. Infrastructure
cd infra/terraform/gcp && terraform apply -var-file=terraform.tfvars

# 2. Configure kubectl
gcloud container clusters get-credentials ml-portfolio-gke-production \
  --region us-central1 --project ml-portfolio-duque-om-202602

# 3. Build & push images
gcloud auth configure-docker us-central1-docker.pkg.dev
docker build -t us-central1-docker.pkg.dev/PROJECT/ml-portfolio-images/bankchurn:latest ./BankChurn-Predictor
docker push ...

# 4. Deploy
kubectl apply -f k8s/ -n ml-portfolio
kubectl get pods -n ml-portfolio
```

## Port Forwarding (GKE)

```bash
kubectl port-forward svc/bankchurn-service 8001:80 -n ml-portfolio
kubectl port-forward svc/carvision-service 8002:80 -n ml-portfolio
kubectl port-forward svc/nlpinsight-service 8003:80 -n ml-portfolio
kubectl port-forward svc/grafana-service 3000:3000 -n ml-portfolio
```

## Operations

```bash
kubectl rollout restart deployment/<service> -n ml-portfolio   # Restart
kubectl rollout undo deployment/<service> -n ml-portfolio      # Rollback
kubectl scale deployment/<service> --replicas=3 -n ml-portfolio # Scale
kubectl get hpa -n ml-portfolio                                 # HPA status
```

## Production Checklist

- [x] Health checks passing (GKE)
- [x] Resource limits calibrated per service
- [x] Monitoring dashboards (Grafana auto-provisioned)
- [x] Load testing (Locust — 0% errors, p95 480ms, 973 reqs/2min)
- [x] Security scanning (Trivy, Bandit, Gitleaks)

---

*Last Updated: March 2026 — v3.3.1*
