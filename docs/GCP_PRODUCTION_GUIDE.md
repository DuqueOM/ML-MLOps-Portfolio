# GCP Production Deployment Guide

Complete guide to deploy the ML-MLOps Portfolio to Google Cloud Platform.
This document includes the **real deployment experience** with problems encountered and solutions applied.

> **Deployment Status**: ✅ Successfully deployed on February 18, 2026
> **Ingress IP**: `34.120.120.57` | **Region**: `us-central1` | **Cluster**: `ml-portfolio-gke-production`

---

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| GCP Account | Free tier OK ($300 credit) | Cloud infrastructure |
| `gcloud` CLI | >= 467.0 | GCP management |
| `terraform` | >= 1.5.0 | Infrastructure as Code |
| `kubectl` | >= 1.28 | Kubernetes management |
| `docker` | >= 24.0 | Container builds (or use Cloud Build) |

> **Note**: `helm` is NOT required. All deployments use raw Kubernetes manifests.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    GCP Project                              │
│              ml-portfolio-duque-om-202602                    │
│                                                             │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │  Artifact    │  │  Cloud SQL  │  │  GCS Buckets     │    │
│  │  Registry    │  │  (Postgres) │  │  Models+Datasets │    │
│  │  3 images    │  │  db-f1-micro│  │  +MLflow artifact│    │
│  └──────┬───────┘  └──────┬──────┘  └────────┬─────────┘    │
│         │                 │                  │              │
│  ┌──────┴─────────────────┴──────────────────┴────────┐     │
│  │         GKE Standard Cluster (us-central1)         │     │
│  │         3 zones × 1-5 nodes (e2-medium, 30GB)      │     │
│  │                                                    │     │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────┐         │     │
│  │  │BankChurn │  │CarVision │  │TelecomAI  │         │     │
│  │  │  FastAPI  │  │FastAPI+  │  │  FastAPI  │         │     │
│  │  │  :8000   │  │Streamlit │  │  :8000    │         │     │
│  │  │          │  │:8000+8501│  │           │         │     │
│  │  └────┬─────┘  └─────┬────┘  └──────┬────┘         │     │
│  │       │              │              │              │     │
│  │  ┌────┴──────────────┴──────────────┴──────┐       │     │
│  │  │    GCE Ingress (HTTP Load Balancer)     │       │     │
│  │  │    IP: 34.120.120.57                    │       │     │
│  │  └─────────────────────────────────────────┘       │     │
│  │                                                    │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │     │
│  │  │ MLflow   │  │Prometheus│  │ Grafana  │          │     │
│  │  │ :5000    │  │ :9090    │  │ :3000    │          │     │
│  │  └──────────┘  └──────────┘  └──────────┘          │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: GCP Project Setup (30 min)

### 1.1 Create GCP Project

```bash
# Set your project ID (must be globally unique, NO underscores allowed)
export PROJECT_ID="ml-portfolio-$(whoami | tr '_' '-')-$(date +%Y%m)"
export REGION="us-central1"
export ZONE="us-central1-a"

# Create project
gcloud projects create $PROJECT_ID --name="ML-MLOps Portfolio"

# Set as active project
gcloud config set project $PROJECT_ID

# Enable billing (required - link to your billing account)
gcloud billing accounts list
gcloud billing projects link $PROJECT_ID --billing-account=YOUR_BILLING_ACCOUNT_ID
```

### 1.2 Enable Required APIs

```bash
gcloud services enable \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  sqladmin.googleapis.com \
  compute.googleapis.com \
  iam.googleapis.com \
  cloudresourcemanager.googleapis.com \
  servicenetworking.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  cloudbuild.googleapis.com
```

> **Lesson Learned**: Enable `cloudbuild.googleapis.com` from the start. It's needed if local Docker builds fail.

### 1.3 Create Service Account for CI/CD

```bash
# Create service account
gcloud iam service-accounts create ml-portfolio-deployer \
  --display-name="ML Portfolio Deployer"

# Grant roles
SA_EMAIL="ml-portfolio-deployer@${PROJECT_ID}.iam.gserviceaccount.com"

for ROLE in \
  roles/container.admin \
  roles/artifactregistry.admin \
  roles/storage.admin \
  roles/cloudsql.admin \
  roles/cloudbuild.builds.editor \
  roles/iam.serviceAccountUser; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="$ROLE"
done

# Create key for CI/CD (store securely!)
gcloud iam service-accounts keys create ~/gcp-key.json \
  --iam-account=$SA_EMAIL

# Authenticate with the service account
gcloud auth activate-service-account --key-file=~/gcp-key.json
```

---

## Phase 2: Infrastructure with Terraform (20 min)

### 2.1 Create Terraform State Bucket

```bash
gsutil mb -l $REGION gs://${PROJECT_ID}-terraform-state
gsutil versioning set on gs://${PROJECT_ID}-terraform-state
```

### 2.2 Configure Terraform Variables

```bash
cd infra/terraform/gcp

# Create terraform.tfvars (see terraform.tfvars.example)
cat > terraform.tfvars <<EOF
project_id   = "${PROJECT_ID}"
project_name = "ml-portfolio"
environment  = "production"
region       = "${REGION}"
machine_type = "e2-medium"
node_count   = 1
min_node_count = 1
max_node_count = 5
db_tier      = "db-f1-micro"
db_password  = "$(openssl rand -base64 24)"
EOF
```

> **⚠️ Important**: Use `node_count = 1` to stay within SSD quota limits.
> With 3 zones × 1 node × 30GB disk = 90GB, well within the 250GB SSD quota.
> Using `node_count = 2` would require 3 × 2 × 30 = 180GB (still OK but more costly).

### 2.3 Deploy Infrastructure

```bash
# Update backend bucket name in main.tf
sed -i "s/ml-portfolio-terraform-state/${PROJECT_ID}-terraform-state/" main.tf

# Initialize and apply
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# Save outputs
terraform output -json > ../../terraform-outputs.json
```

### 2.4 Configure kubectl

```bash
CLUSTER_NAME=$(terraform output -raw gke_cluster_name)
gcloud container clusters get-credentials $CLUSTER_NAME \
  --region $REGION --project $PROJECT_ID

# Verify connection
kubectl get nodes
```

### 2.5 Problems Encountered & Solutions

| Problem | Root Cause | Solution |
|---------|-----------|----------|
| `SSD_TOTAL_GB quota exceeded` | Default `node_count=2` × 3 zones × 100GB disk | Reduce `disk_size_gb=30` in `main.tf`, `node_count=1` |
| `deletion_protection` prevents changes | GKE cluster has `deletion_protection=true` | Set `deletion_protection=false` in `main.tf`, apply, then change config |
| Cloud SQL private IP networking | Missing private service connection | Add `google_compute_global_address` + `google_service_networking_connection` in Terraform |
| Terraform state inconsistency | Partial apply left orphaned resources | `terraform state rm` + re-import, or `terraform apply` with updated config |

---

## Phase 3: Build & Push Docker Images (15-30 min)

### 3.1 Configure Artifact Registry

```bash
AR_REPO="${REGION}-docker.pkg.dev/${PROJECT_ID}/ml-portfolio-images"

# Authenticate Docker with Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

### 3.2 Build and Push Images

**Option A: Local Docker Build (fastest if Docker is stable)**

```bash
cd /path/to/ML-MLOps-Portfolio

for PROJECT in BankChurn-Predictor CarVision-Market-Intelligence TelecomAI-Customer-Intelligence; do
  IMAGE_NAME=$(echo $PROJECT | tr '[:upper:]' '[:lower:]')
  echo "Building ${IMAGE_NAME}..."

  DOCKER_BUILDKIT=1 docker build \
    -t ${AR_REPO}/${IMAGE_NAME}:latest \
    -t ${AR_REPO}/${IMAGE_NAME}:v1.0.0 \
    ${PROJECT}/

  docker push ${AR_REPO}/${IMAGE_NAME}:latest
  docker push ${AR_REPO}/${IMAGE_NAME}:v1.0.0
done
```

**Option B: Google Cloud Build (recommended if local Docker is slow/unstable)**

```bash
# Build and push directly in GCP (no local Docker required)
for PROJECT in BankChurn-Predictor CarVision-Market-Intelligence TelecomAI-Customer-Intelligence; do
  IMAGE_NAME=$(echo $PROJECT | tr '[:upper:]' '[:lower:]')
  echo "Cloud Building ${IMAGE_NAME}..."

  gcloud builds submit \
    --tag ${AR_REPO}/${IMAGE_NAME}:latest \
    --project $PROJECT_ID \
    --timeout=1800 \
    ${PROJECT}/

  # Add version tag
  gcloud artifacts docker tags add \
    ${AR_REPO}/${IMAGE_NAME}:latest \
    ${AR_REPO}/${IMAGE_NAME}:v1.0.0
done
```

### 3.3 Verify Images

```bash
gcloud artifacts docker images list ${AR_REPO} --format="table(package,tags,createTime)"
```

### 3.4 Problems Encountered & Solutions

| Problem | Root Cause | Solution |
|---------|-----------|----------|
| `docker push` hangs on large layers (~2GB) | WSL Docker daemon instability with large uploads | **Use Google Cloud Build** (`gcloud builds submit`) |
| BuildKit `CANCELED: context canceled` | Docker daemon instability in WSL environment | Restart Docker daemon or use Cloud Build |
| Image size too large (2.3GB) | ML dependencies (scikit-learn, pandas, etc.) | Multi-stage builds already in place; consider slimmer base images |

> **Best Practice**: Google Cloud Build is faster and more reliable than local builds for large ML images.
> CarVision built in **4m37s** on Cloud Build vs hanging indefinitely locally.

---

## Phase 4: Train & Upload Models + Datasets (15 min)

### 4.1 Train Demo Models Locally

```bash
# Generate demo models
bash scripts/setup_demo_models.sh
```

### 4.2 Upload Models to GCS

```bash
MODELS_BUCKET=$(terraform -chdir=infra/terraform/gcp output -raw ml_models_bucket)

# Upload BankChurn model
gsutil cp BankChurn-Predictor/models/model.joblib \
  gs://${MODELS_BUCKET}/bankchurn/best_model.pkl

# Upload CarVision model
gsutil cp CarVision-Market-Intelligence/models/model.joblib \
  gs://${MODELS_BUCKET}/carvision/model.joblib

# Upload TelecomAI model
gsutil cp TelecomAI-Customer-Intelligence/models/model.joblib \
  gs://${MODELS_BUCKET}/telecom/model.joblib

# Verify uploads
gsutil ls -r gs://${MODELS_BUCKET}/
```

> **Tip**: If `gsutil cp` fails with `ServerNotFoundError`, retry — it's usually a transient DNS issue.

### 4.3 Upload Datasets to GCS

Datasets are stored in a separate GCS bucket with versioning, lifecycle policies, and strict naming conventions.

```bash
DATASETS_BUCKET="${PROJECT_ID}-datasets-production"

# Create datasets bucket with versioning
gsutil mb -l $REGION gs://${DATASETS_BUCKET}
gsutil versioning set on gs://${DATASETS_BUCKET}

# Set lifecycle policy (auto-archive after 90 days)
cat > /tmp/lifecycle.json <<EOF
{"rule": [{"action": {"type": "SetStorageClass", "storageClass": "NEARLINE"}, "condition": {"age": 90}}]}
EOF
gsutil lifecycle set /tmp/lifecycle.json gs://${DATASETS_BUCKET}

# Upload BankChurn dataset
gsutil cp BankChurn-Predictor/data/raw/Churn.csv \
  gs://${DATASETS_BUCKET}/bankchurn/v1/Churn.csv

# Upload CarVision dataset
gsutil cp CarVision-Market-Intelligence/data/raw/vehicles_us.csv \
  gs://${DATASETS_BUCKET}/carvision/v1/vehicles_us.csv

# Upload TelecomAI dataset
gsutil cp TelecomAI-Customer-Intelligence/data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv \
  gs://${DATASETS_BUCKET}/telecom/v1/WA_Fn-UseC_-Telco-Customer-Churn.csv

# Verify uploads
gsutil ls -r gs://${DATASETS_BUCKET}/
```

> **Naming Convention**: `gs://{project-id}-datasets-production/{service}/v{version}/{filename}`
> **Security**: Only the `ml-portfolio-gke-workload` SA has `storage.objectViewer` access.

---

## Phase 5: Deploy to Kubernetes (20 min)

### 5.1 Create Namespace and Secrets

```bash
kubectl apply -f k8s/namespace.yaml

# Create secrets for DB
kubectl create secret generic mlflow-db-secret \
  --namespace=ml-portfolio \
  --from-literal=POSTGRES_PASSWORD="$(grep db_password infra/terraform/gcp/terraform.tfvars | cut -d'"' -f2)"

# Create storage resources
kubectl apply -f k8s/storage.yaml
```

### 5.2 Update K8s Manifests with Your Image URLs

```bash
AR_REPO="${REGION}-docker.pkg.dev/${PROJECT_ID}/ml-portfolio-images"

# Update image references in deployment files
sed -i "s|image: .*bankchurn.*|image: ${AR_REPO}/bankchurn-predictor:latest|" k8s/bankchurn-deployment.yaml
sed -i "s|image: .*carvision.*|image: ${AR_REPO}/carvision-market-intelligence:latest|" k8s/carvision-deployment.yaml
sed -i "s|image: .*telecom.*|image: ${AR_REPO}/telecomai-customer-intelligence:latest|" k8s/telecom-deployment.yaml
```

### 5.3 Deploy Services

```bash
# Deploy ConfigMaps (model + dataset paths)
kubectl apply -f k8s/download-script-configmap.yaml
kubectl apply -f k8s/model-configmaps.yaml
kubectl apply -f k8s/dataset-configmaps.yaml

# Deploy all ML services
kubectl apply -f k8s/bankchurn-deployment.yaml
kubectl apply -f k8s/carvision-deployment.yaml
kubectl apply -f k8s/telecom-deployment.yaml

# Deploy ingress
kubectl apply -f k8s/ingress.yaml

# Deploy monitoring stack
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/grafana-deployment.yaml

# Wait for rollout
kubectl rollout status deployment/bankchurn-predictor -n ml-portfolio --timeout=300s
kubectl rollout status deployment/carvision-intelligence -n ml-portfolio --timeout=300s
kubectl rollout status deployment/telecom-intelligence -n ml-portfolio --timeout=300s
```

### 5.4 Verify Deployment

```bash
# Check all pods are Running
kubectl get pods -n ml-portfolio

# Check services
kubectl get svc -n ml-portfolio

# Get external IP (may take 5-10 min)
kubectl get ingress -n ml-portfolio

# Test health endpoints via kubectl exec
kubectl exec -n ml-portfolio deployment/bankchurn-predictor -- curl -s http://localhost:8000/health
kubectl exec -n ml-portfolio deployment/carvision-intelligence -- curl -s http://localhost:8000/health
kubectl exec -n ml-portfolio deployment/telecom-intelligence -- curl -s http://localhost:8000/health
```

### 5.5 Problems Encountered & Solutions

| Problem | Root Cause | Solution |
|---------|-----------|----------|
| Pods `Pending` - unbound PVC | `ReadWriteMany` + `standard` StorageClass not supported on GKE | Changed to `ReadWriteOnce` + `standard-rwo` in `storage.yaml` |
| Pods `Pending` - model-storage PVC | PVC required but models load from GCS at runtime | Removed `model-storage` volumeMount from BankChurn deployment |
| `ImagePullBackOff` | Docker image not pushed to Artifact Registry | Used Google Cloud Build to push the image |
| `CrashLoopBackOff` (Prometheus/Grafana) | Permission denied on `/var/lib/grafana` and `/prometheus` | Added `securityContext` (runAsUser, fsGroup) + replaced PVC with `emptyDir` |
| `Insufficient cpu` scheduling failures | All nodes at capacity with 6 pods | GKE autoscaler triggered scale-up (1→2 nodes) automatically |
| Services type `ClusterIP` incompatible with GCE ingress | GCE ingress requires `NodePort` backends | Changed all ML services to `type: NodePort` |

> **Key GKE Differences from local K8s**:
> - Use `standard-rwo` StorageClass (not `standard` or `hostPath`)
> - Use `ReadWriteOnce` (not `ReadWriteMany` unless using Filestore)
> - Services backing a GCE Ingress must be `NodePort`
> - Prometheus/Grafana need `securityContext` for proper file permissions

---

## Phase 6: MLflow Server on GKE (10 min)

### 6.1 Deploy MLflow with SQLite Backend

For a portfolio demo, SQLite is sufficient. For production, use Cloud SQL.

```bash
ARTIFACTS_BUCKET=$(terraform -chdir=infra/terraform/gcp output -raw mlflow_artifacts_bucket)

cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mlflow-server
  namespace: ml-portfolio
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mlflow
  template:
    metadata:
      labels:
        app: mlflow
    spec:
      containers:
      - name: mlflow
        image: ghcr.io/mlflow/mlflow:v2.9.2
        ports:
        - containerPort: 5000
        command: ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000",
                  "--backend-store-uri", "sqlite:///mlflow/mlflow.db",
                  "--default-artifact-root", "gs://${ARTIFACTS_BUCKET}/artifacts"]
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        volumeMounts:
        - name: mlflow-data
          mountPath: /mlflow
      volumes:
      - name: mlflow-data
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: mlflow-service
  namespace: ml-portfolio
spec:
  selector:
    app: mlflow
  ports:
  - port: 5000
    targetPort: 5000
  type: ClusterIP
EOF
```

### 6.2 Access MLflow UI

```bash
kubectl port-forward svc/mlflow-service 5000:5000 -n ml-portfolio &
# Open http://localhost:5000
```

---

## Phase 7: Monitoring Stack (10 min)

### 7.1 Prometheus + Grafana

```bash
# Deploy monitoring (ConfigMaps are embedded in the deployment YAMLs)
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/grafana-deployment.yaml
```

### 7.2 Access Dashboards

```bash
# Grafana (default: admin/admin)
kubectl port-forward svc/grafana-service 3000:3000 -n ml-portfolio &
# Open http://localhost:3000

# Prometheus
kubectl port-forward svc/prometheus-service 9090:9090 -n ml-portfolio &
# Open http://localhost:9090/targets
```

> **Note**: Prometheus and Grafana use `emptyDir` volumes (non-persistent).
> Data is lost on pod restart. For production, use PVCs with `standard-rwo`.

### 7.3 Auto-Provisioned Grafana Dashboard

The deployment includes a **"ML Portfolio Metrics"** dashboard auto-provisioned via ConfigMap (`grafana-dashboards` in `k8s/grafana-deployment.yaml`). No manual dashboard creation needed — it appears automatically when Grafana starts.

**Dashboard panels** (10 panels monitoring all 3 ML services):

| Panel | PromQL (example) | Type |
|-------|--------|------|
| Prediction Rate — All Services | `sum(rate(bankchurn_predictions_total[5m]))`, `sum(rate(carvision_requests_total[5m]))`, `sum(rate(telecom_requests_total[5m]))` | Time series |
| Latency P95 — All Services | `histogram_quantile(0.95, sum(rate(<service>_request_duration_seconds_bucket[5m])) by (le))` | Time series |
| Total Requests — BankChurn | `sum(bankchurn_requests_total)` | Stat |
| Total Requests — CarVision | `sum(carvision_requests_total)` | Stat |
| Total Requests — TelecomAI | `sum(telecom_requests_total)` | Stat |
| Targets UP | `count(up == 1)` | Stat |
| Avg Latency — All Services | `rate(<service>_request_duration_seconds_sum[5m]) / rate(..._count[5m])` | Time series |
| Latency Distribution P99/P95/P50 | `histogram_quantile(0.99/0.95/0.50, ...)` per service | Time series |
| BankChurn — Predictions by Risk Level | `bankchurn_predictions_total{risk_level="HIGH/MEDIUM/LOW"}` | Time series |
| Error Rate — All Services | `sum(rate(<service>_requests_total{status=~"5.."}[5m]))` | Time series |

**Prometheus scrape configuration** (`k8s/prometheus-deployment.yaml`) includes jobs for all 3 services:
- `bankchurn-predictor` — scrapes pods with label `app: bankchurn-predictor`
- `carvision-intelligence` — scrapes pods with label `app: carvision-intelligence`
- `telecom-intelligence` — scrapes pods with label `app: telecom-intelligence`

**To customize**: edit the JSON in `k8s/grafana-deployment.yaml` → `grafana-dashboards` ConfigMap → apply → restart Grafana.

### 7.4 Production Validation: Smoke Tests + Load Testing

Professional observability validation uses **two separate tools** following SRE methodology:

| Layer | Tool | When | Purpose |
|-------|------|------|---------|
| **Smoke Tests** | `pytest` + `httpx` | After every deploy (CI gate) | Fast fail — verify services respond correctly |
| **Load Tests** | `Locust` | Manual / scheduled | Sustained traffic → Prometheus/Grafana metrics |

#### Tier 1 — Smoke Tests (pytest + httpx, post-deploy CI gate)

```bash
# Prerequisites: port-forward all services
kubectl port-forward svc/bankchurn-service 8000:80 -n ml-portfolio &
kubectl port-forward svc/carvision-service 8001:80 -n ml-portfolio &
kubectl port-forward svc/telecom-service   8002:80 -n ml-portfolio &

# Run all 14 smoke tests (~10s total)
pytest tests/integration/test_smoke_k8s.py -v

# Fast gate (health only)
pytest tests/integration/test_smoke_k8s.py -v -k "health"
```

Each service has 4–5 tests covering: health check, `/metrics` Prometheus format, prediction response shape, domain validation (probability range, price positive), and 422 on invalid payloads.

#### Tier 2 — Load Tests (Locust, metrics population)

```bash
# Install
pip install locust

# Interactive web UI — open http://localhost:8089
locust -f tests/load/locustfile.py

# Headless — all 3 services, 30 users, 120s, CSV + HTML report
locust -f tests/load/locustfile.py \
       --headless -u 30 -r 5 -t 120s \
       --csv=reports/load_test \
       --html=reports/load_test.html

# Quick metrics population (Grafana)
locust -f tests/load/locustfile.py \
       --headless -u 10 -r 2 -t 60s --only-summary
```

**Locust design**: randomized payloads per request (avoids cache effects, exercises different model branches), weighted tasks (predict 10× vs health 1×), inline SLA assertions with `catch_response=True`.

**SLA thresholds**: Error rate < 1%, P95 < 500ms (BankChurn < 800ms — ensemble model), P99 < 1s.

After load testing, open Grafana (`http://localhost:3000`) → "ML Portfolio Metrics" to see populated real-time metrics.

#### Quick one-shot validation (no Locust required)

```bash
# Smoke + load + Prometheus metrics check (uses stdlib only)
python scripts/load_test_services.py --requests 200 --concurrency 5
```

---

## Phase 8: CI/CD Integration (GitHub Actions → GCP)

### 8.1 Add GitHub Secrets

Add these secrets in your GitHub repo (Settings → Secrets → Actions):

| Secret Name | Value |
|-------------|-------|
| `GCP_PROJECT_ID` | `ml-portfolio-duque-om-202602` |
| `GCP_SA_KEY` | Contents of `~/gcp-key.json` (base64 encoded) |
| `GCP_REGION` | `us-central1` |
| `GKE_CLUSTER_NAME` | `ml-portfolio-gke-production` |

### 8.2 Encode the service account key

```bash
cat ~/gcp-key.json | base64 -w 0 > gcp-key-b64.txt
# Copy the content of gcp-key-b64.txt to GitHub secret GCP_SA_KEY
rm gcp-key-b64.txt  # Clean up
```

### 8.3 CI/CD Workflow

The workflow at `.github/workflows/deploy-gcp.yml` automatically:
1. Detects which services changed (BankChurn, CarVision, TelecomAI)
2. Builds and pushes Docker images to Artifact Registry
3. Deploys to GKE with rolling updates
4. Runs health check smoke tests
5. Posts deployment summary

Trigger options:
- **Automatic**: Push to `main` branch with changes in service directories
- **Manual**: `workflow_dispatch` with service selection (all/bankchurn/carvision/telecom)

---

## Cost Estimation (Monthly)

| Resource | Spec | Estimated Cost |
|----------|------|---------------|
| GKE Standard | 1-5 nodes e2-medium (preemptible) | $25-80 |
| Cloud SQL (Postgres) | db-f1-micro | $10 |
| Artifact Registry | ~5GB images | $2 |
| GCS Buckets | ~100MB models + artifacts | $0.05 |
| Load Balancer | 1 IP + forwarding rules | $18 |
| Cloud Build | Occasional builds | $0-5 |
| **Total** | | **~$55-115/month** |

### Cost Optimization Tips
- Use **preemptible/spot VMs** for non-production (already configured in Terraform)
- Set GKE **autoscaler** min to 1 node during off-hours
- Use `db-f1-micro` for Cloud SQL (sufficient for portfolio demo)
- Set **lifecycle rules** on GCS buckets (auto-archive after 90 days)
- **Free tier**: First 3 months get $300 credit on new GCP accounts
- **Teardown** when not needed for portfolio review — redeploy in ~30 min

---

## Verification Checklist

After deployment, verify everything works:

```bash
# 1. All 6 pods running
kubectl get pods -n ml-portfolio
# Expected: 6 pods (bankchurn, carvision, telecom, mlflow, prometheus, grafana) all Running

# 2. Health checks pass (via kubectl exec)
for DEPLOY in bankchurn-predictor carvision-intelligence telecom-intelligence; do
  echo "Testing ${DEPLOY}..."
  kubectl exec -n ml-portfolio deployment/${DEPLOY} -- curl -s http://localhost:8000/health
  echo ""
done

# 3. Ingress has external IP
kubectl get ingress -n ml-portfolio
# Expected: ADDRESS column shows an IP (may take 5-10 min)

# 4. Predictions work (via port-forward)
kubectl port-forward svc/bankchurn-service 8001:80 -n ml-portfolio &
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"CreditScore":650,"Geography":"France","Gender":"Male","Age":35,"Tenure":5,"Balance":50000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":75000}'

# 5. MLflow UI accessible
kubectl port-forward svc/mlflow-service 5000:5000 -n ml-portfolio &
# Open http://localhost:5000

# 6. Grafana dashboards
kubectl port-forward svc/grafana-service 3000:3000 -n ml-portfolio &
# Open http://localhost:3000 (admin/admin)

# 7. Prometheus targets
kubectl port-forward svc/prometheus-service 9090:9090 -n ml-portfolio &
# Open http://localhost:9090/targets

# 8. Artifact Registry images
gcloud artifacts docker images list \
  ${REGION}-docker.pkg.dev/${PROJECT_ID}/ml-portfolio-images \
  --format="table(package,tags)"

# 9. GCS models + datasets
gsutil ls -r gs://$(terraform -chdir=infra/terraform/gcp output -raw ml_models_bucket)/
gsutil ls -r gs://${PROJECT_ID}-datasets-production/
```

---

## Phase 9: Init Containers — Model & Dataset Download Pattern

### Why Init Containers?

Init containers run **before** the main application container starts. In this portfolio, they download **both the ML model and the dataset** from Google Cloud Storage to shared `emptyDir` volumes. This pattern ensures:

1. **The model and data are available before the API starts** — no race condition
2. **Retry logic** — if the download fails, the init container retries before the app starts
3. **Separation of concerns** — the API container doesn't need GCS credentials or libraries
4. **Hot-swapping** — update the ConfigMap and restart the pod to load a new model/dataset version
5. **Data versioning** — datasets are versioned in GCS with lifecycle policies
6. **SHAP Explainability** — BankChurn uses the downloaded dataset as SHAP background data, enabling real feature contributions in API responses instead of zeros

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│ Pod: bankchurn-predictor                                    │
│                                                            │
│  ┌───────────────────────────┐                              │
│  │ Init: download-model      │                              │
│  │ python:3.11-alpine        │                              │
│  │ pip install gcs SDK       │                              │
│  │ Download model.joblib     │── model-config ConfigMap      │
│  │ Write to /models/         │──┐                            │
│  └───────────────────────────┘  │ emptyDir: models          │
│                                │                            │
│  ┌───────────────────────────┐  │                            │
│  │ Init: download-data       │  │                            │
│  │ python:3.11-alpine        │  │                            │
│  │ pip install gcs SDK       │  │                            │
│  │ Download dataset.csv      │──┼─ dataset-config ConfigMap  │
│  │ Write to /data/           │──┼─┐                          │
│  └───────────────────────────┘  │ │ emptyDir: data            │
│                                │ │                          │
│  ┌───────────────────────────┐  │ │                          │
│  │ Main Container            │  │ │                          │
│  │ bankchurn-api             │  │ │                          │
│  │                           │  │ │                          │
│  │ Mount /app/models/ ◄─────│──┘ │                          │
│  │ Mount /app/data/   ◄─────│────┘                          │
│  │ Load model + serve        │                              │
│  └───────────────────────────┘                              │
└──────────────────────────────────────────────────────────┘
```

### 9.1 Download Script ConfigMap

The download script is stored as a ConfigMap to avoid baking it into a custom Docker image:

```bash
# The script is defined in k8s/download-script-configmap.yaml
kubectl apply -f k8s/download-script-configmap.yaml

# Verify it's created
kubectl get configmap download-script -n ml-portfolio -o yaml
```

The script (`download-model.py`) reads three environment variables:
- `GCS_BUCKET` — the GCS bucket name
- `GCS_MODEL_PATH` — the path within the bucket (e.g., `bankchurn/model.joblib`)
- `LOCAL_MODEL_PATH` — where to save the model inside the container

### 9.2 Model ConfigMaps (Per Service)

Each ML service has its own ConfigMap with the GCS path to its model:

```bash
# Apply all model ConfigMaps
kubectl apply -f k8s/model-configmaps.yaml

# Verify
kubectl get configmap -n ml-portfolio -l component=model-download
# NAME                     DATA   AGE
# bankchurn-model-config   3      Xs
# carvision-model-config   3      Xs
# telecom-model-config     3      Xs
```

### 9.3 Dataset ConfigMaps (Per Service)

Each ML service also has a ConfigMap for its dataset path in GCS:

```bash
# Apply all dataset ConfigMaps
kubectl apply -f k8s/dataset-configmaps.yaml

# Verify
kubectl get configmap -n ml-portfolio -l component=dataset-download
# NAME                       DATA   AGE
# bankchurn-dataset-config   3      Xs
# carvision-dataset-config   3      Xs
# telecom-dataset-config     3      Xs
```

| Service | Dataset | GCS Path | Size |
|---------|---------|----------|------|
| BankChurn | `Churn.csv` | `bankchurn/v1/Churn.csv` | ~1.2 MB |
| CarVision | `vehicles_us.csv` | `carvision/v1/vehicles_us.csv` | ~63 MB |
| TelecomAI | `WA_Fn-UseC_-Telco-Customer-Churn.csv` | `telecom/v1/WA_Fn-UseC_-...csv` | ~977 KB |

### 9.4 Metrics ConfigMap (CarVision)

CarVision has a third init container (`download-metrics`) that downloads evaluation artifacts from GCS for the Streamlit dashboard:

```bash
# Apply metrics ConfigMap
kubectl apply -f k8s/metrics-configmap.yaml

# Verify
kubectl get configmap carvision-metrics-config -n ml-portfolio
```

| Artifact | GCS Path | Purpose |
|----------|----------|--------|
| `metrics_val.json` | `carvision/metrics_val.json` | RMSE, MAE, R², MAPE for Model Metrics tab |
| `model_comparison.json` | `carvision/model_comparison.json` | Model vs baseline comparison |
| `feature_columns.json` | `carvision/feature_columns.json` | Feature list for predictions |

> **Why a separate init container?** Metrics are model artifacts that change with each retrain. Storing them in GCS (not baked in Docker) means Streamlit always shows the latest evaluation results after a rollout restart.

### 9.5 Updating a Model Version

To deploy a new model version **without rebuilding the Docker image**:

```bash
# Option A: Manual upload
gsutil cp new-model.joblib gs://${MODELS_BUCKET}/bankchurn/model.joblib
kubectl rollout restart deployment/bankchurn-predictor -n ml-portfolio

# Option B: Automated via promote_model.py (recommended)
# This validates metrics → registers in MLflow → uploads to GCS
GCS_MODELS_BUCKET=${MODELS_BUCKET} python scripts/promote_model.py \
  --project carvision --promote --upload-gcs
kubectl rollout restart deployment/carvision-intelligence -n ml-portfolio

# Verify the new model is loaded
kubectl logs -n ml-portfolio deployment/carvision-intelligence -c download-model
```

> **Key Advantage**: This is a **config-only operation** — no Docker build needed. The init container downloads the new model on pod startup.

### 9.6 Integration: DVC ↔ MLflow ↔ GCS

The three data/model management tools serve different stages of the ML lifecycle:

```
┌────────────────────────────────────────────────────────────────────┐
│  DEVELOPMENT               TRACKING              PRODUCTION         │
│  ┌─────────────┐          ┌─────────────┐    ┌──────────────┐   │
│  │    DVC      │          │   MLflow    │    │  GCS Buckets  │   │
│  │ (local/CI) │          │  (cluster)  │    │ (production) │   │
│  │            │          │             │    │              │   │
│  │ • Raw CSV  │  train   │ • Metrics   │    │ • Models     │   │
│  │ • .dvc     │────────▶│ • Params    │    │ • Datasets   │   │
│  │ • dvc pull │  logs    │ • Artifacts │    │ • Metrics    │   │
│  └─────────────┘          │ • Registry  │    └─────┬────────┘   │
│                           └──────┬──────┘          │              │
│                                │   promote       │              │
│                                │   --upload-gcs  │              │
│                                └───────────────▶│              │
│                                                 │              │
│                                           init containers    │
│                                           download to pod    │
└────────────────────────────────────────────────────────────────────┘
```

| Tool | Stage | What it Stores | Location |
|------|-------|----------------|----------|
| **DVC** | Development | Raw CSV datasets, `.dvc` metadata | Local + `.dvc-storage/` |
| **MLflow** | Training | Metrics, params, model artifacts, registry | Cluster (`mlflow-server` pod) |
| **GCS** | Production | Models, datasets, metrics for serving | `*-ml-models-production`, `*-datasets-production` |

**Full promotion flow** (`scripts/promote_model.py --promote --upload-gcs`):
1. Load local metrics from `artifacts/metrics_val.json`
2. Validate against thresholds (R² > 0.70, RMSE < 6000, etc.)
3. Register model + metrics in MLflow Model Registry
4. Promote to "Production" stage in MLflow
5. Upload `model.joblib` + `metrics_val.json` + extra artifacts to GCS
6. User runs `kubectl rollout restart` → init containers download fresh artifacts

---

## Phase 10: Workload Identity — Secure GCS Access

### Why Workload Identity?

Instead of mounting a GCP service account key file into pods (insecure), Workload Identity allows Kubernetes service accounts to impersonate GCP service accounts. This means:

- **No keys stored in Kubernetes secrets** — eliminates credential leakage risk
- **Automatic credential rotation** — managed by GCP
- **Granular access control** — each pod gets only the permissions it needs

### 10.1 Configure Workload Identity

```bash
# The K8s service account is defined in k8s/ml-workload-serviceaccount.yaml
kubectl apply -f k8s/ml-workload-serviceaccount.yaml

# Create GCP service account for workloads
gcloud iam service-accounts create ml-portfolio-gke-workload \
  --display-name="ML Portfolio GKE Workload"

# Grant GCS read access to the workload SA
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:ml-portfolio-gke-workload@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# Bind the K8s SA to the GCP SA
gcloud iam service-accounts add-iam-policy-binding \
  ml-portfolio-gke-workload@${PROJECT_ID}.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="serviceAccount:${PROJECT_ID}.svc.id.goog[ml-portfolio/ml-workload]"
```

### 10.2 Verify Workload Identity

```bash
# From inside a pod, verify the identity
kubectl exec -n ml-portfolio deployment/bankchurn-predictor -c bankchurn-api -- \
  curl -s -H "Metadata-Flavor: Google" \
  http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email

# Should return: ml-portfolio-gke-workload@PROJECT_ID.iam.gserviceaccount.com
```

---

## Phase 11: Horizontal Pod Autoscaler (HPA)

### Why HPA?

The HPA automatically scales the number of pod replicas based on CPU and memory utilization. This ensures:

- **Cost efficiency** — 1 replica during low traffic
- **Reliability** — up to 3 replicas during high traffic
- **Automatic** — no manual intervention needed

### 11.1 HPA Configuration

Each ML service has an HPA defined in its deployment YAML:

```yaml
# Example: BankChurn HPA (in k8s/bankchurn-deployment.yaml)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bankchurn-hpa
  namespace: ml-portfolio
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bankchurn-predictor
  minReplicas: 1
  maxReplicas: 3
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 11.2 Verify HPA

```bash
kubectl get hpa -n ml-portfolio
# NAME            REFERENCE                      TARGETS          MINPODS   MAXPODS
# bankchurn-hpa   Deployment/bankchurn-predictor  12%/70%, 34%/80%  1         3
# telecom-hpa     Deployment/telecom-intelligence 8%/75%            1         3
```

### 11.3 Scale-Down Behavior

The HPA has a **stabilization window** of 300 seconds (5 minutes) for scale-down. This prevents flapping (rapid scale-up/scale-down cycles). Scale-up has no stabilization window for fast response.

---

## Phase 12: Pod Anti-Affinity

### Why Anti-Affinity?

Pod anti-affinity ensures that replicas of the same service are spread across different nodes. If one node fails, other replicas continue serving on different nodes.

```yaml
# In bankchurn-deployment.yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - bankchurn-predictor
        topologyKey: kubernetes.io/hostname
```

> **Note**: We use `preferredDuringScheduling` (soft rule) instead of `requiredDuringScheduling` (hard rule) because with `minReplicas: 1`, there may be times when only one node is available.

---

## Advanced Cost Optimization Strategies

### Implemented Optimizations

| Strategy | Savings | Implementation |
|----------|---------|----------------|
| **e2-medium nodes** | ~60% vs n1-standard-2 | `machine_type = "e2-medium"` in Terraform |
| **Single node with autoscaler** | ~66% vs 3-node fixed | `node_count=1, max_node_count=5` |
| **Preemptible/Spot VMs** | ~60-80% vs on-demand | `preemptible = true` in node pool config |
| **db-f1-micro for Cloud SQL** | ~$7/month vs $50+/month | `db_tier = "db-f1-micro"` |
| **emptyDir for monitoring** | Avoids PVC costs | No persistent disks for Prometheus/Grafana |
| **GCS lifecycle rules** | Auto-archive old artifacts | Nearline after 30/90 days (models/datasets) |
| **Minimal disk size (30GB)** | Fits SSD quota, reduces cost | `disk_size_gb = 30` per node |
| **Cloud Build** | No local Docker overhead | Pay per build minute (~$0.003/min) |

### Cost Breakdown: Portfolio Demo vs Production

| Component | Demo (current) | Production |
|-----------|---------------|------------|
| GKE nodes | 1×e2-medium ($25/mo) | 3×n1-standard-2 ($200/mo) |
| Cloud SQL | db-f1-micro ($7/mo) | db-n1-standard-1 ($50/mo) |
| Load Balancer | 1 IP ($18/mo) | Same |
| Storage (GCS) | ~165MB models+datasets ($0.05/mo) | 10GB+ ($2/mo) |
| **Total** | **~$50/mo** | **~$270/mo** |

### When to Teardown

- **Before job applications**: Deploy 1 day before, collect evidence, teardown
- **For interviews**: Deploy 2 hours before scheduled interview, teardown after
- **Continuous**: Keep running only if actively iterating on the portfolio

```bash
# Quick teardown script
kubectl delete namespace ml-portfolio  # Delete workloads (keeps infra)
# OR
terraform -chdir=infra/terraform/gcp destroy -auto-approve  # Full teardown
```

---

## Teardown (When Done Collecting Evidence)

```bash
# Option A: Delete GKE workloads only (keep infra, ~$10/month)
kubectl delete namespace ml-portfolio

# Option B: Full teardown (stop all billing)
cd infra/terraform/gcp
terraform destroy -auto-approve

# Option C: Delete project entirely (nuclear option)
gcloud projects delete $PROJECT_ID
```

---

## Troubleshooting Reference

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| SSD Quota Exceeded | `terraform apply` fails | Reduce `disk_size_gb` to 30 and `node_count` to 1 |
| Pods in `Pending` | `kubectl describe pod` shows PVC issues | Use `standard-rwo` StorageClass with `ReadWriteOnce` |
| Pods in `CrashLoopBackOff` | `kubectl logs <pod> --previous` shows permission errors | Add `securityContext` with correct `runAsUser` and `fsGroup` |
| `ImagePullBackOff` | Image not in Artifact Registry | Build with `gcloud builds submit` or re-push with Docker |
| Ingress no external IP | `kubectl get ingress` shows no ADDRESS | Wait 5-10 min for GCP load balancer provisioning |
| `docker push` hangs | Large layers timeout in WSL | Use `gcloud builds submit` instead of local push |
| `gsutil` `ServerNotFoundError` | Transient DNS issue | Retry the command — usually works on second attempt |
| `OOMKilled` | Pod exceeds memory limits | Increase `limits.memory` in deployment YAML |
| Terraform state lock | Concurrent operations | `terraform force-unlock <LOCK_ID>` |
| `Insufficient cpu` | Nodes at capacity | GKE autoscaler will add nodes; or reduce resource requests |

### Useful Debug Commands

```bash
# Pod logs
kubectl logs -n ml-portfolio <pod-name> --tail=50
kubectl logs -n ml-portfolio <pod-name> --previous  # crashed pod

# Pod details
kubectl describe pod <pod-name> -n ml-portfolio

# Events (sorted by time)
kubectl get events -n ml-portfolio --sort-by='.lastTimestamp'

# Resource usage
kubectl top pods -n ml-portfolio
kubectl top nodes

# Exec into pod
kubectl exec -it -n ml-portfolio <pod-name> -- /bin/bash
```

---

## Deployment Log (Real Execution)

### Timeline

| Phase | Duration | Status | Notes |
|-------|----------|--------|-------|
| Phase 1: GCP Setup | 30 min | ✅ Complete | Project, APIs, service account created |
| Phase 2: Terraform | 45 min | ✅ Complete | Required quota adjustments (SSD, node count) |
| Phase 3: Docker Images | 60 min | ✅ Complete | BankChurn + Telecom via Docker; CarVision via Cloud Build |
| Phase 4: Models+Datasets | 15 min | ✅ Complete | 3 models + 3 datasets uploaded to GCS |
| Phase 5: K8s Deploy | 40 min | ✅ Complete | Required PVC, service type, and security fixes |
| Phase 6: MLflow | 5 min | ✅ Complete | SQLite backend (sufficient for demo) |
| Phase 7: Monitoring | 10 min | ✅ Complete | securityContext fixes for Prometheus/Grafana |
| Phase 8: CI/CD | 15 min | ✅ Complete | GitHub Secrets configured, workflow deployed |
| **Total** | **~3.5 hours** | **✅ Complete** | 6/6 pods Running, Ingress active |

### Final State

```
$ kubectl get pods -n ml-portfolio
NAME                                      READY   STATUS    AGE
bankchurn-predictor-6758c897bd-zttzf      1/1     Running   2m
carvision-intelligence-77f58796cf-7lg2l   2/2     Running   2m
telecom-intelligence-788c44bcc-pxk49      1/1     Running   2m
mlflow-server-6cf9564cd7-qn7rz            1/1     Running   82m
prometheus-dc4689989-qf9gm                1/1     Running   94m
grafana-78486fd569-jtmtj                  1/1     Running   94m
```

### Key Decisions Made During Deployment

1. **Cloud Build over local Docker**: WSL Docker hangs on large layer pushes. Cloud Build completed in 4m37s.
2. **`node_count=1` with autoscaler**: Saves cost, GKE auto-scales when needed.
3. **`emptyDir` over PVC for monitoring**: Avoids PVC binding issues on single-node clusters.
4. **SQLite for MLflow**: Simpler than Cloud SQL proxy for a portfolio demo.
5. **`NodePort` services**: Required for GCE Ingress (native GKE load balancer).
6. **`standard-rwo` StorageClass**: GKE's default for ReadWriteOnce persistent disks.
