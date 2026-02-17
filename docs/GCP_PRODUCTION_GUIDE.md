# GCP Production Deployment Guide

Complete guide to deploy the ML-MLOps Portfolio to Google Cloud Platform.

---

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| GCP Account | Free tier OK | Cloud infrastructure |
| `gcloud` CLI | >= 467.0 | GCP management |
| `terraform` | >= 1.5.0 | Infrastructure as Code |
| `kubectl` | >= 1.28 | Kubernetes management |
| `docker` | >= 24.0 | Container builds |
| `helm` | >= 3.12 | K8s package manager |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    GCP Project                          │
│                                                         │
│  ┌──────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Artifact    │  │  Cloud SQL  │  │  GCS Bucket │     │ 
│  │  Registry    │  │  (Postgres) │  │  (Models)   │     │
│  └──────┬───────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                 │                │            │
│  ┌──────┴─────────────────┴────────────────┴──────┐     │
│  │              GKE Autopilot Cluster             │     │
│  │                                                │     │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────┐       │     │
│  │  │BankChurn │ │CarVision │ │TelecomAI  │       │     │
│  │  │  API     │ │  API     │ │  API      │       │     │
│  │  └────┬─────┘ └─────┬────┘ └──────┬────┘       │     │
│  │       │             │             │            │     │
│  │  ┌────┴─────────────┴─────────────┴─────┐      │     │
│  │  │         Ingress (HTTPS)              │      │     │
│  │  └──────────────────────────────────────┘      │     │
│  │                                                │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐        │     │
│  │  │MLflow    │ │Prometheus│ │ Grafana  │        │     │
│  │  │Server    │ │          │ │          │        │     │
│  │  └──────────┘ └──────────┘ └──────────┘        │     │
│  └────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## Phase 1: GCP Project Setup (30 min)

### 1.1 Create GCP Project

```bash
# Set your project ID (must be globally unique, no underscores)
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
  logging.googleapis.com
```

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
  roles/iam.serviceAccountUser; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="$ROLE"
done

# Create key for CI/CD (store securely!)
gcloud iam service-accounts keys create ~/gcp-key.json \
  --iam-account=$SA_EMAIL
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

# Create terraform.tfvars
cat > terraform.tfvars <<EOF
project_id   = "${PROJECT_ID}"
project_name = "ml-portfolio"
environment  = "production"
region       = "${REGION}"
machine_type = "e2-medium"
node_count   = 2
min_node_count = 1
max_node_count = 5
db_tier      = "db-f1-micro"
db_password  = "$(openssl rand -base64 24)"
EOF
```

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
```

---

## Phase 3: Build & Push Docker Images (15 min)

### 3.1 Configure Artifact Registry

```bash
AR_REPO="${REGION}-docker.pkg.dev/${PROJECT_ID}/ml-portfolio-images"

# Authenticate Docker with Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

### 3.2 Build and Push Images

```bash
cd /path/to/ML-MLOps-Portfolio

# Build and push all 3 projects
for PROJECT in BankChurn-Predictor CarVision-Market-Intelligence TelecomAI-Customer-Intelligence; do
  IMAGE_NAME=$(echo $PROJECT | tr '[:upper:]' '[:lower:]')
  echo "Building ${IMAGE_NAME}..."
  
  docker build -t ${AR_REPO}/${IMAGE_NAME}:latest \
               -t ${AR_REPO}/${IMAGE_NAME}:v1.0.0 \
               ${PROJECT}/
  
  docker push ${AR_REPO}/${IMAGE_NAME}:latest
  docker push ${AR_REPO}/${IMAGE_NAME}:v1.0.0
done
```

---

## Phase 4: Train & Upload Models (10 min)

### 4.1 Train Demo Models Locally

```bash
# Generate demo models
bash scripts/setup_demo_models.sh
```

### 4.2 Upload Models to GCS

```bash
MODELS_BUCKET=$(terraform -chdir=infra/terraform/gcp output -raw ml_models_bucket)

# Upload BankChurn model
gsutil cp BankChurn-Predictor/models/best_model.pkl \
  gs://${MODELS_BUCKET}/bankchurn/best_model.pkl

# Upload CarVision model + features
gsutil cp CarVision-Market-Intelligence/artifacts/model.joblib \
  gs://${MODELS_BUCKET}/carvision/model.joblib
gsutil cp CarVision-Market-Intelligence/artifacts/feature_columns.json \
  gs://${MODELS_BUCKET}/carvision/feature_columns.json

# Upload TelecomAI model
gsutil cp TelecomAI-Customer-Intelligence/artifacts/model.joblib \
  gs://${MODELS_BUCKET}/telecom/model.joblib
```

---

## Phase 5: Deploy to Kubernetes (20 min)

### 5.1 Create Namespace and Secrets

```bash
kubectl apply -f k8s/namespace.yaml

# Create secrets for DB
kubectl create secret generic mlflow-db-secret \
  --namespace=ml-portfolio \
  --from-literal=POSTGRES_PASSWORD="$(grep db_password infra/terraform/gcp/terraform.tfvars | cut -d'"' -f2)"

# Create model storage PV/PVC
kubectl apply -f k8s/storage.yaml
```

### 5.2 Update K8s Manifests with Your Image URLs

```bash
AR_REPO="${REGION}-docker.pkg.dev/${PROJECT_ID}/ml-portfolio-images"

# Update image references in deployment files
for FILE in k8s/bankchurn-deployment.yaml k8s/carvision-deployment.yaml k8s/telecom-deployment.yaml; do
  sed -i "s|duqueom/.*:|${AR_REPO}/|g" $FILE
done
```

### 5.3 Deploy Services

```bash
# Deploy all services
kubectl apply -f k8s/bankchurn-deployment.yaml
kubectl apply -f k8s/carvision-deployment.yaml
kubectl apply -f k8s/telecom-deployment.yaml
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
# Check pods
kubectl get pods -n ml-portfolio

# Check services
kubectl get svc -n ml-portfolio

# Get external IP
kubectl get ingress -n ml-portfolio

# Test health endpoints (replace IP)
EXTERNAL_IP=$(kubectl get ingress ml-portfolio-ingress -n ml-portfolio -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://${EXTERNAL_IP}/bankchurn/health
curl http://${EXTERNAL_IP}/carvision/health
curl http://${EXTERNAL_IP}/telecom/health
```

---

## Phase 6: MLflow Server on GKE (15 min)

### 6.1 Deploy MLflow with Cloud SQL Backend

```bash
DB_CONNECTION=$(terraform -chdir=infra/terraform/gcp output -raw mlflow_db_connection_name)
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
        env:
        - name: MLFLOW_BACKEND_STORE_URI
          value: "postgresql://mlflow:\$(POSTGRES_PASSWORD)@127.0.0.1:5432/mlflow"
        - name: MLFLOW_DEFAULT_ARTIFACT_ROOT
          value: "gs://${ARTIFACTS_BUCKET}/artifacts"
        envFrom:
        - secretRef:
            name: mlflow-db-secret
        command: ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000"]
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      - name: cloud-sql-proxy
        image: gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.8.0
        args: ["--structured-logs", "${DB_CONNECTION}"]
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
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

---

## Phase 7: Monitoring Stack (10 min)

### 7.1 Prometheus + Grafana

```bash
# Apply Prometheus config
kubectl create configmap prometheus-config \
  --namespace=ml-portfolio \
  --from-file=prometheus.yml=infra/prometheus-config.yaml

# Apply Prometheus rules
kubectl create configmap prometheus-rules \
  --namespace=ml-portfolio \
  --from-file=rules.yml=infra/prometheus-rules.yaml

# Deploy monitoring
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/grafana-deployment.yaml

# Import Grafana dashboards
GRAFANA_POD=$(kubectl get pods -n ml-portfolio -l app=grafana -o jsonpath='{.items[0].metadata.name}')
kubectl cp infra/grafana/dashboards/ml-portfolio-dashboard.json \
  ml-portfolio/${GRAFANA_POD}:/var/lib/grafana/dashboards/
```

---

## Phase 8: CI/CD Integration (GitHub Actions → GCP)

### 8.1 Add GitHub Secrets

Add these secrets in your GitHub repo (Settings → Secrets → Actions):

| Secret Name | Value |
|-------------|-------|
| `GCP_PROJECT_ID` | Your project ID |
| `GCP_SA_KEY` | Contents of `~/gcp-key.json` (base64 encoded) |
| `GCP_REGION` | `us-central1` |
| `GKE_CLUSTER_NAME` | From terraform output |

### 8.2 Encode the service account key

```bash
cat ~/gcp-key.json | base64 -w 0 > gcp-key-b64.txt
# Copy the content of gcp-key-b64.txt to GitHub secret GCP_SA_KEY
```

---

## Cost Estimation (Monthly)

| Resource | Spec | Estimated Cost |
|----------|------|---------------|
| GKE Autopilot | 2-5 nodes e2-medium | $50-120 |
| Cloud SQL (Postgres) | db-f1-micro | $10 |
| Artifact Registry | ~2GB images | $1 |
| GCS Buckets | ~500MB models | $0.02 |
| Load Balancer | 1 IP + forwarding | $18 |
| **Total** | | **~$80-150/month** |

### Cost Optimization Tips
- Use **preemptible/spot VMs** for non-production (already configured in Terraform)
- Set GKE **autoscaler** min to 1 node during off-hours
- Use `db-f1-micro` for Cloud SQL (sufficient for portfolio demo)
- Set **lifecycle rules** on GCS buckets (auto-archive after 90 days)
- **Free tier**: First 3 months get $300 credit on new GCP accounts

---

## Verification Checklist

After deployment, verify everything works:

```bash
# 1. All pods running
kubectl get pods -n ml-portfolio | grep -c Running

# 2. Health checks pass
for svc in bankchurn carvision telecom; do
  echo "Testing $svc..."
  curl -s http://${EXTERNAL_IP}/${svc}/health | python3 -m json.tool
done

# 3. Predictions work
curl -X POST http://${EXTERNAL_IP}/bankchurn/predict \
  -H "Content-Type: application/json" \
  -d '{"CreditScore":650,"Geography":"France","Gender":"Male","Age":35,"Tenure":5,"Balance":50000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":75000}'

curl -X POST http://${EXTERNAL_IP}/carvision/predict \
  -H "Content-Type: application/json" \
  -d '{"model_year":2020,"model":"civic","condition":"good","cylinders":4,"fuel":"gas","odometer":30000,"transmission":"automatic","drive":"fwd","type":"sedan","paint_color":"white"}'

curl -X POST http://${EXTERNAL_IP}/telecom/predict \
  -H "Content-Type: application/json" \
  -d '{"calls":55.0,"minutes":300.0,"messages":45.0,"mb_used":15000.0}'

# 4. MLflow UI accessible
kubectl port-forward svc/mlflow-service 5000:5000 -n ml-portfolio &
open http://localhost:5000

# 5. Grafana dashboards
kubectl port-forward svc/grafana 3000:3000 -n ml-portfolio &
open http://localhost:3000  # admin/admin

# 6. Prometheus targets up
kubectl port-forward svc/prometheus 9090:9090 -n ml-portfolio &
open http://localhost:9090/targets
```

---

## Teardown (When Done Collecting Evidence)

```bash
# Option A: Delete GKE workloads only (keep infra)
kubectl delete -f k8s/ --all

# Option B: Full teardown
cd infra/terraform/gcp
terraform destroy

# Delete project entirely (nuclear option)
gcloud projects delete $PROJECT_ID
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Pods in CrashLoopBackOff | `kubectl logs <pod> -n ml-portfolio --previous` |
| ImagePullBackOff | Check Artifact Registry auth: `gcloud auth configure-docker` |
| Cloud SQL connection refused | Verify Cloud SQL Proxy sidecar is running |
| Ingress no external IP | Wait 5-10 min for GCP load balancer provisioning |
| OOMKilled | Increase memory limits in deployment YAML |
| Terraform state lock | `terraform force-unlock <LOCK_ID>` |
