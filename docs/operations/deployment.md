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
| NLPInsight API | 8003 | `curl localhost:8003/health` |
| MLflow | 5000 | `curl localhost:5000/health` |

## Production (GKE — GCP)

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

## Production (EKS — AWS)

```bash
# 1. Infrastructure
eksctl create cluster --name ml-portfolio-eks --region us-east-1 --nodes 3 --node-type t3.small

# 2. Configure kubectl
aws eks update-kubeconfig --region us-east-1 --name ml-portfolio-eks

# 3. Install nginx-ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.3/deploy/static/provider/cloud/deploy.yaml

# 4. Deploy
kubectl apply -k k8s/overlays/aws/
kubectl get pods -n ml-portfolio

# 5. Get ELB DNS
kubectl get svc -n ingress-nginx ingress-nginx-controller
curl http://<ELB_DNS>/bankchurn/health
```

## Port Forwarding (GKE)

```bash
kubectl port-forward svc/bankchurn-service 8001:80 -n ml-portfolio
kubectl port-forward svc/nlpinsight-service 8003:80 -n ml-portfolio
kubectl port-forward svc/chicagotaxi-service 8004:80 -n ml-portfolio
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

- [x] Health checks passing (GKE + EKS)
- [x] Resource limits calibrated per service
- [x] Monitoring dashboards (Grafana auto-provisioned, both clouds)
- [x] Load testing GCP (Locust — 0% errors, p95 190ms via Ingress IP)
- [x] Load testing AWS (Locust — 0% errors, p95 450ms via Classic ELB)
- [x] Stress testing AWS (25 users, 0% errors, 20.99 RPS)
- [x] Drift detection (daily CronJobs on both clouds)
- [x] Security scanning (Trivy, Bandit, Gitleaks)

---

*Last Updated: March 2026 — v3.5.3*
