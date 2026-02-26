# AWS Production Deployment Guide

Complete guide to deploy the ML-MLOps Portfolio to Amazon Web Services.
This document mirrors the [GCP Production Guide](GCP_PRODUCTION_GUIDE.md) with AWS-specific services and configurations.

> **Deployment Status**: Pending deployment
> **Region**: `us-east-1` | **Cluster**: `ml-portfolio-eks-production`

---

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| AWS Account | Free tier OK (12-month free tier) | Cloud infrastructure |
| `aws` CLI | >= 2.x | AWS management |
| `eksctl` | >= 0.170 | EKS cluster helper |
| `terraform` | >= 1.5.0 | Infrastructure as Code |
| `kubectl` | >= 1.28 | Kubernetes management |
| `docker` | >= 24.0 | Container builds |
| `helm` | >= 3.x | AWS Load Balancer Controller |

> **Note**: Unlike GCP, AWS EKS requires `helm` for the AWS Load Balancer Controller (ALB Ingress).

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                     AWS Account                               │
│                  us-east-1 (N. Virginia)                       │
│                                                               │
│  ┌───────────────┐  ┌──────────────┐  ┌───────────────────┐   │
│  │  ECR          │  │  RDS         │  │  S3 Buckets       │   │
│  │  (Registry)   │  │  (Postgres)  │  │  Models+Datasets  │   │
│  │  3 images     │  │  db.t3.micro │  │  +MLflow artifacts│   │
│  └──────┬────────┘  └──────┬───────┘  └────────┬──────────┘   │
│         │                  │                   │              │
│  ┌──────┴──────────────────┴───────────────────┴─────────┐    │
│  │          EKS Cluster (us-east-1)                      │    │
│  │          3 nodes × t3.large (2 vCPU, 8 GiB)          │    │
│  │                                                       │    │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────┐            │    │
│  │  │BankChurn │  │CarVision │  │TelecomAI  │            │    │
│  │  │  FastAPI  │  │FastAPI+  │  │  FastAPI  │            │    │
│  │  │  :8000   │  │Streamlit │  │  :8000    │            │    │
│  │  │          │  │:8000+8501│  │           │            │    │
│  │  └────┬─────┘  └─────┬────┘  └──────┬────┘            │    │
│  │       │              │              │                 │    │
│  │  ┌────┴──────────────┴──────────────┴──────┐          │    │
│  │  │   ALB (Application Load Balancer)       │          │    │
│  │  │   DNS: k8s-mlportf-XXXXXXX.elb.aws.com │          │    │
│  │  └─────────────────────────────────────────┘          │    │
│  │                                                       │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │    │
│  │  │ MLflow   │  │Prometheus│  │ Grafana  │             │    │
│  │  │ :5000    │  │ :9090    │  │ :3000    │             │    │
│  │  └──────────┘  └──────────┘  └──────────┘             │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌──────────────────────────┐  ┌──────────────────────────┐   │
│  │  VPC: 10.0.0.0/16       │  │  CloudWatch Logs         │   │
│  │  3 public + 3 private   │  │  /aws/eks/ml-portfolio    │   │
│  │  NAT Gateway (single)   │  │  Retention: 30 days      │   │
│  └──────────────────────────┘  └──────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### Key Differences from GCP Architecture

| Component | GCP | AWS |
|-----------|-----|-----|
| K8s cluster | GKE (auto node pools) | EKS (explicit node groups) |
| Container registry | Artifact Registry | ECR |
| Object storage | Cloud Storage (GCS) | S3 |
| Database | Cloud SQL | RDS |
| Load balancer | GCE Ingress (static IP) | ALB (DNS name) |
| IAM for pods | Workload Identity | IRSA |
| VPC | Auto-created by GKE | Explicit (subnets, NAT, IGW) |
| Logs | Cloud Logging | CloudWatch |
| Init container SDK | `google-cloud-storage` | `boto3` |

---

## Phase 1: AWS Account Setup (20 min)

### 1.1 Create IAM User for Deployment

```bash
# Create IAM user (don't use root account)
aws iam create-user --user-name ml-portfolio-deployer

# Create access key
aws iam create-access-key --user-name ml-portfolio-deployer
# Save the AccessKeyId and SecretAccessKey securely!

# Attach required policies
for POLICY in \
  arn:aws:iam::aws:policy/AmazonEKSClusterPolicy \
  arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy \
  arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess \
  arn:aws:iam::aws:policy/AmazonS3FullAccess \
  arn:aws:iam::aws:policy/AmazonRDSFullAccess \
  arn:aws:iam::aws:policy/AmazonVPCFullAccess \
  arn:aws:iam::aws:policy/IAMFullAccess \
  arn:aws:iam::aws:policy/CloudWatchLogsFullAccess; do
  aws iam attach-user-policy \
    --user-name ml-portfolio-deployer \
    --policy-arn "$POLICY"
done
```

### 1.2 Configure AWS CLI

```bash
# Configure with the deployer credentials
aws configure --profile ml-portfolio
# AWS Access Key ID: [from step 1.1]
# AWS Secret Access Key: [from step 1.1]
# Default region name: us-east-1
# Default output format: json

# Set as default profile
export AWS_PROFILE=ml-portfolio

# Verify
aws sts get-caller-identity
# {
#     "UserId": "AIXXXXXXXXXXXXXXXXXX",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/ml-portfolio-deployer"
# }
```

### 1.3 Create Terraform State Backend

```bash
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION="us-east-1"

# Create S3 bucket for Terraform state
aws s3api create-bucket \
  --bucket ml-portfolio-terraform-state \
  --region $AWS_REGION

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ml-portfolio-terraform-state \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket ml-portfolio-terraform-state \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $AWS_REGION
```

> **Key Difference from GCP**: GCP uses a GCS bucket for state; AWS uses S3 + DynamoDB for state locking (GCS has built-in locking).

---

## Phase 2: Infrastructure with Terraform (30 min)

### 2.1 Configure Terraform Variables

```bash
cd infra/terraform/aws

# Create terraform.tfvars from example
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
cat > terraform.tfvars <<EOF
project_name = "ml-portfolio"
environment  = "production"
aws_region   = "us-east-1"

vpc_cidr             = "10.0.0.0/16"
private_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
public_subnet_cidrs  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

db_instance_class = "db.t3.micro"
db_username       = "mlflow"
db_password       = "$(openssl rand -base64 24)"
EOF
```

### 2.2 Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Review the plan
terraform plan -out=tfplan

# Apply (creates ~25-30 resources: VPC, subnets, NAT, EKS, RDS, S3, ECR, etc.)
terraform apply tfplan

# Save outputs
terraform output -json > ../../terraform-outputs-aws.json
```

> **Expected duration**: `terraform apply` takes **15-20 minutes** (EKS cluster creation is the slowest part).

### 2.3 Configure kubectl for EKS

```bash
EKS_CLUSTER=$(terraform output -raw eks_cluster_name)

aws eks update-kubeconfig \
  --region $AWS_REGION \
  --name $EKS_CLUSTER

# Verify connection
kubectl get nodes
# NAME                              STATUS   ROLES    AGE   VERSION
# ip-10-0-1-xx.ec2.internal        Ready    <none>   Xm    v1.28.x
# ip-10-0-2-xx.ec2.internal        Ready    <none>   Xm    v1.28.x
# ip-10-0-3-xx.ec2.internal        Ready    <none>   Xm    v1.28.x
```

### 2.4 Install AWS Load Balancer Controller

Unlike GCP (which has GCE Ingress built-in), AWS requires the Load Balancer Controller for ALB Ingress:

```bash
# Add the EKS Helm chart repo
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# Install the controller
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=$EKS_CLUSTER \
  --set serviceAccount.create=true \
  --set serviceAccount.name=aws-load-balancer-controller

# Verify
kubectl get deployment -n kube-system aws-load-balancer-controller
# NAME                           READY   UP-TO-DATE   AVAILABLE
# aws-load-balancer-controller   2/2     2            2
```

### 2.5 Problems Encountered & Solutions

| Problem | Root Cause | Solution |
|---------|-----------|----------|
| `terraform apply` timeout on EKS | EKS cluster creation takes ~15 min | Increase timeout, be patient |
| NAT Gateway costs | Single NAT = ~$32/month | Use `single_nat_gateway = true` for non-production |
| Node group `CREATE_FAILED` | Insufficient EC2 capacity | Change instance type or AZ |
| `eksctl` conflicts with Terraform | Both trying to manage the same resources | Use ONLY Terraform for EKS management |

---

## Phase 3: Build & Push Docker Images to ECR (15-30 min)

### 3.1 Authenticate Docker with ECR

```bash
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $ECR_REGISTRY
```

### 3.2 Build and Push Images

```bash
cd /path/to/ML-MLOps-Portfolio

SERVICES=(
  "BankChurn-Predictor:ml-portfolio/bankchurn-predictor"
  "CarVision-Market-Intelligence:ml-portfolio/carvision-intelligence"
  "TelecomAI-Customer-Intelligence:ml-portfolio/telecom-intelligence"
)

for ENTRY in "${SERVICES[@]}"; do
  CONTEXT="${ENTRY%%:*}"
  IMAGE="${ENTRY##*:}"
  echo "Building ${IMAGE}..."

  DOCKER_BUILDKIT=1 docker build \
    -t ${ECR_REGISTRY}/${IMAGE}:latest \
    -t ${ECR_REGISTRY}/${IMAGE}:v1.0.0 \
    ${CONTEXT}/

  docker push ${ECR_REGISTRY}/${IMAGE}:latest
  docker push ${ECR_REGISTRY}/${IMAGE}:v1.0.0
done
```

### 3.3 Verify Images in ECR

```bash
# List all repositories
aws ecr describe-repositories --output table

# List images in a specific repo
aws ecr list-images --repository-name ml-portfolio/bankchurn-predictor --output table
```

### 3.4 Problems Encountered & Solutions

| Problem | Root Cause | Solution |
|---------|-----------|----------|
| `no basic auth credentials` | ECR login expired (12h token) | Re-run `aws ecr get-login-password` |
| `name unknown: The repository does not exist` | ECR repo not created by Terraform | Check `terraform output ecr_repositories` |
| Push timeout on large images | Slow upload from local machine | Use smaller base images or AWS CodeBuild |

---

## Phase 4: Upload Models + Datasets to S3 (15 min)

### 4.1 Train Demo Models Locally

```bash
# Generate demo models (same as GCP)
bash scripts/setup_demo_models.sh
```

### 4.2 Upload Models to S3

```bash
MODELS_BUCKET=$(terraform -chdir=infra/terraform/aws output -raw ml_models_bucket)

# Upload BankChurn model
aws s3 cp BankChurn-Predictor/models/model.joblib \
  s3://${MODELS_BUCKET}/bankchurn/model.joblib

# Upload CarVision model
aws s3 cp CarVision-Market-Intelligence/models/model.joblib \
  s3://${MODELS_BUCKET}/carvision/model.joblib

# Upload TelecomAI model
aws s3 cp TelecomAI-Customer-Intelligence/models/model.joblib \
  s3://${MODELS_BUCKET}/telecom/model.joblib

# Verify uploads
aws s3 ls s3://${MODELS_BUCKET}/ --recursive --human-readable
```

> **Key Difference from GCP**: Uses `aws s3 cp` instead of `gsutil cp`. S3 versioning is already enabled by Terraform.

### 4.3 Upload Datasets to S3

Datasets are stored in a separate S3 bucket with versioning, lifecycle policies, and strict naming conventions.

```bash
DATASETS_BUCKET="ml-portfolio-datasets-production"

# Create datasets bucket with versioning
aws s3 mb s3://${DATASETS_BUCKET} --region ${AWS_REGION}
aws s3api put-bucket-versioning --bucket ${DATASETS_BUCKET} \
  --versioning-configuration Status=Enabled

# Set lifecycle policy (transition to Glacier after 90 days)
cat > /tmp/lifecycle.json <<EOF
{
  "Rules": [{
    "ID": "ArchiveOldDatasets",
    "Status": "Enabled",
    "Transitions": [{"Days": 90, "StorageClass": "GLACIER"}],
    "Filter": {"Prefix": ""}
  }]
}
EOF
aws s3api put-bucket-lifecycle-configuration --bucket ${DATASETS_BUCKET} \
  --lifecycle-configuration file:///tmp/lifecycle.json

# Upload BankChurn dataset
aws s3 cp BankChurn-Predictor/data/raw/Churn.csv \
  s3://${DATASETS_BUCKET}/bankchurn/v1/Churn.csv

# Upload CarVision dataset
aws s3 cp CarVision-Market-Intelligence/data/raw/vehicles_us.csv \
  s3://${DATASETS_BUCKET}/carvision/v1/vehicles_us.csv

# Upload TelecomAI dataset
aws s3 cp TelecomAI-Customer-Intelligence/data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv \
  s3://${DATASETS_BUCKET}/telecom/v1/WA_Fn-UseC_-Telco-Customer-Churn.csv

# Verify uploads
aws s3 ls s3://${DATASETS_BUCKET}/ --recursive --human-readable
```

> **Naming Convention**: `s3://ml-portfolio-datasets-production/{service}/v{version}/{filename}`
> **Security**: Only the `ml-portfolio-eks-workload-role` IAM role has `s3:GetObject` access.

---

## Phase 5: Deploy to Kubernetes (20 min)

### 5.1 Create Namespace and Secrets

```bash
kubectl apply -f k8s/namespace.yaml

# Create secrets for DB (MLflow backend)
DB_ENDPOINT=$(terraform -chdir=infra/terraform/aws output -raw mlflow_db_endpoint)
DB_PASSWORD=$(grep db_password infra/terraform/aws/terraform.tfvars | cut -d'"' -f2)

kubectl create secret generic mlflow-db-secret \
  --namespace=ml-portfolio \
  --from-literal=POSTGRES_PASSWORD="$DB_PASSWORD" \
  --from-literal=DB_HOST="$DB_ENDPOINT"

# Create storage resources
kubectl apply -f k8s/storage.yaml
```

### 5.2 Update K8s Manifests with ECR URLs

```bash
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Update ACCOUNT_ID placeholder in AWS overlay manifests
for FILE in k8s/overlays/aws/*-deployment-aws.yaml; do
  sed -i "s|ACCOUNT_ID|${AWS_ACCOUNT_ID}|g" "$FILE"
done

# Update service account ARN
sed -i "s|ACCOUNT_ID|${AWS_ACCOUNT_ID}|g" k8s/overlays/aws/serviceaccount-aws.yaml
```

### 5.3 Deploy AWS Overlay

```bash
# Apply AWS-specific resources
kubectl apply -f k8s/overlays/aws/serviceaccount-aws.yaml
kubectl apply -f k8s/overlays/aws/download-script-aws.yaml
kubectl apply -f k8s/overlays/aws/model-configmaps-aws.yaml
kubectl apply -f k8s/overlays/aws/dataset-configmaps-aws.yaml
kubectl apply -f k8s/overlays/aws/metrics-configmap-aws.yaml

# Or use Kustomize to apply everything at once:
# kubectl apply -k k8s/overlays/aws/

# Deploy ML services (AWS versions with ECR images + S3 init containers)
kubectl apply -f k8s/overlays/aws/bankchurn-deployment-aws.yaml
kubectl apply -f k8s/overlays/aws/carvision-deployment-aws.yaml
kubectl apply -f k8s/overlays/aws/telecom-deployment-aws.yaml

# Deploy monitoring stack (shared manifests — cloud-agnostic)
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/grafana-deployment.yaml

# Deploy ALB Ingress
kubectl apply -f k8s/overlays/aws/ingress-aws.yaml

# Wait for rollout
kubectl rollout status deployment/bankchurn-predictor -n ml-portfolio --timeout=300s
kubectl rollout status deployment/carvision-intelligence -n ml-portfolio --timeout=300s
kubectl rollout status deployment/telecom-intelligence -n ml-portfolio --timeout=300s
```

### 5.4 Verify Deployment

```bash
# Check all pods are Running
kubectl get pods -n ml-portfolio -o wide
# Expected: 6 pods Running on EC2 nodes

# Check services
kubectl get svc -n ml-portfolio

# Get ALB DNS (may take 3-5 min for ALB provisioning)
kubectl get ingress -n ml-portfolio
# NAME                    CLASS   HOSTS   ADDRESS                                          PORTS
# ml-portfolio-ingress    alb     *       k8s-mlportf-XXXXXXXXXX.us-east-1.elb.amazonaws.com   80

# Test health via port-forward
kubectl port-forward svc/bankchurn-service 8001:80 -n ml-portfolio &
curl -s http://localhost:8001/health | python3 -m json.tool
```

### 5.5 Problems Encountered & Solutions

| Problem | Root Cause | Solution |
|---------|-----------|----------|
| Init container `CrashLoopBackOff` | `boto3` not installed | Verify init container command includes `pip install boto3` |
| ALB not provisioned | AWS LB Controller not installed | Install via Helm (Phase 2.4) |
| `AccessDenied` on S3 | IRSA not configured | Configure IAM role for service account |
| Pods `Pending` — insufficient resources | Node group too small | Increase `desired_size` or use larger instance type |
| `ImagePullBackOff` from ECR | ECR auth expired or wrong region | Re-authenticate: `aws ecr get-login-password` |

> **Key EKS Differences from GKE**:
> - ALB Ingress requires the AWS Load Balancer Controller (Helm install)
> - Node names are EC2 private IPs (`ip-10-0-1-xx.ec2.internal`)
> - IRSA replaces Workload Identity for pod-level IAM
> - Security Groups must allow traffic between nodes and pods

---

## Phase 6: MLflow Server on EKS (10 min)

### 6.1 Deploy MLflow with RDS Backend

```bash
ARTIFACTS_BUCKET=$(terraform -chdir=infra/terraform/aws output -raw mlflow_artifacts_bucket)
DB_ENDPOINT=$(terraform -chdir=infra/terraform/aws output -raw mlflow_db_endpoint)

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
      serviceAccountName: ml-workload
      containers:
      - name: mlflow
        image: ghcr.io/mlflow/mlflow:v2.9.2
        ports:
        - containerPort: 5000
        command: ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000",
                  "--backend-store-uri", "postgresql://mlflow:\${DB_PASSWORD}@${DB_ENDPOINT}/mlflow",
                  "--default-artifact-root", "s3://${ARTIFACTS_BUCKET}/artifacts"]
        env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mlflow-db-secret
              key: POSTGRES_PASSWORD
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
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

> **Key Difference from GCP**: MLflow uses RDS PostgreSQL (managed) instead of SQLite. Artifacts go to S3 instead of GCS. This is a production-grade setup.

### 6.2 Access MLflow UI

```bash
kubectl port-forward svc/mlflow-service 5000:5000 -n ml-portfolio &
# Open http://localhost:5000
```

---

## Phase 7: Monitoring Stack (10 min)

### 7.1 Prometheus + Grafana

```bash
# Deploy monitoring (same manifests as GCP — Prometheus and Grafana are cloud-agnostic)
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/grafana-deployment.yaml
```

### 7.2 Access Dashboards

```bash
# Grafana (credentials in secret grafana-credentials: admin / MLPortfolio2026!)
kubectl port-forward svc/grafana-service 3000:3000 -n ml-portfolio &
# Open http://localhost:3000

# Prometheus
kubectl port-forward svc/prometheus-service 9090:9090 -n ml-portfolio &
# Open http://localhost:9090/targets
```

> **Note**: Prometheus and Grafana use `emptyDir` volumes (same as GCP).
> The monitoring stack is 100% cloud-agnostic — identical configs on GKE and EKS.

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

> **Note**: Both the dashboard JSON and Prometheus config are in the base `k8s/` directory, shared between GCP and AWS overlays. The monitoring stack is 100% cloud-agnostic.

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

Each service has 4–5 tests: health, `/metrics` Prometheus format, prediction shape, domain validation, 422 on invalid payloads.

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

**Locust design**: randomized payloads per request, weighted tasks (predict 10× vs health 1×), inline SLA assertions with `catch_response=True`.

**SLA thresholds**: Error rate < 1%, P95 < 500ms (BankChurn < 800ms), P99 < 1s.

> **Note**: Both tools are cloud-agnostic — identical procedure on GKE and EKS. The `locustfile.py` uses K8s port-forward ports (8000/8001/8002) by default.

#### Quick one-shot validation (no Locust required)

```bash
# Smoke + load + Prometheus metrics check (uses stdlib only)
python scripts/load_test_services.py --requests 200 --concurrency 5
```

---

## Phase 8: CI/CD Integration (GitHub Actions → AWS)

### 8.1 Add GitHub Secrets

Add these secrets in your GitHub repo (Settings → Secrets → Actions):

| Secret Name | Value |
|-------------|-------|
| `AWS_ACCESS_KEY_ID` | Access key from Phase 1.1 |
| `AWS_SECRET_ACCESS_KEY` | Secret key from Phase 1.1 |
| `AWS_ACCOUNT_ID` | Your 12-digit AWS account ID |
| `AWS_REGION` | `us-east-1` |
| `EKS_CLUSTER_NAME` | `ml-portfolio-eks-production` |

### 8.2 CI/CD Workflow

The workflow at `.github/workflows/deploy-aws.yml` automatically:
1. Detects which services changed (BankChurn, CarVision, TelecomAI)
2. Authenticates with AWS using `aws-actions/configure-aws-credentials`
3. Logs into ECR using `aws-actions/amazon-ecr-login`
4. Builds and pushes Docker images to ECR
5. Updates kubeconfig for EKS
6. Applies AWS K8s overlay manifests
7. Runs health check smoke tests
8. Posts deployment summary

Trigger options:
- **Automatic**: Push to `main` branch with changes in service directories
- **Manual**: `workflow_dispatch` with service selection (all/bankchurn/carvision/telecom)

---

## Phase 9: Init Containers — S3 Model & Dataset Download Pattern

Each pod runs init containers before the main application starts:
1. **download-model** — downloads the ML model from S3
2. **download-data** — downloads the dataset from S3 (also used as SHAP background data for BankChurn feature contributions)
3. **download-metrics** (CarVision only) — downloads evaluation artifacts from S3 for Streamlit

### Architecture (AWS Version)

```
┌──────────────────────────────────────────────────────────┐
│ Pod: bankchurn-predictor (EKS)                            │
│                                                          │
│  ┌───────────────────────────┐                            │
│  │ Init: download-model      │                            │
│  │ python:3.11-alpine        │                            │
│  │ pip install boto3         │                            │
│  │ Download model.joblib     │── model-config ConfigMap    │
│  │ Write to /models/         │──┐                          │
│  └───────────────────────────┘  │ emptyDir: models          │
│                                │                          │
│  ┌───────────────────────────┐  │                          │
│  │ Init: download-data       │  │                          │
│  │ python:3.11-alpine        │  │                          │
│  │ pip install boto3         │  │                          │
│  │ Download dataset.csv      │──┼─ dataset-config ConfigMap│
│  │ Write to /data/           │──┼─┐                        │
│  └───────────────────────────┘  │ │ emptyDir: data          │
│                                │ │                        │
│  ┌───────────────────────────┐  │ │                        │
│  │ Main Container            │  │ │                        │
│  │ bankchurn-api             │  │ │                        │
│  │                           │  │ │                        │
│  │ Mount /app/models/ ◄─────│──┘ │                        │
│  │ Mount /app/data/   ◄─────│────┘                        │
│  │ Load model + serve        │                            │
│  └───────────────────────────┘                            │
└──────────────────────────────────────────────────────────┘
```

### Dataset ConfigMaps (AWS)

Each service has a dataset-specific ConfigMap in `k8s/overlays/aws/dataset-configmaps-aws.yaml`:

| Service | S3 Bucket | S3 Path | Local Path |
|---------|-----------|---------|------------|
| BankChurn | `ml-portfolio-datasets-production` | `bankchurn/v1/Churn.csv` | `/data/raw/Churn.csv` |
| CarVision | `ml-portfolio-datasets-production` | `carvision/v1/vehicles_us.csv` | `/data/raw/vehicles_us.csv` |
| TelecomAI | `ml-portfolio-datasets-production` | `telecom/v1/WA_Fn-UseC_-...csv` | `/data/raw/WA_Fn-UseC_-...csv` |

### Key Differences from GCP Init Container

| Aspect | GCP | AWS |
|--------|-----|-----|
| SDK | `google-cloud-storage==2.18.2` | `boto3==1.34.0` |
| Env vars | `GCS_BUCKET`, `GCS_MODEL_PATH` | `S3_BUCKET`, `S3_MODEL_PATH` |
| Download | `storage.Client().bucket().blob().download_to_filename()` | `boto3.client("s3").download_file()` |
| Auth | Workload Identity (auto) | IRSA (auto) |
| Init containers per pod | 2–3 (model + data + metrics) | 2–3 (model + data + metrics) |
| Dataset bucket | `{project}-datasets-production` | `ml-portfolio-datasets-production` |

### Metrics ConfigMap (CarVision — AWS)

CarVision has a third init container that downloads evaluation artifacts for the Streamlit dashboard:

```bash
# Apply metrics ConfigMap
kubectl apply -f k8s/overlays/aws/metrics-configmap-aws.yaml
```

| Artifact | S3 Path | Purpose |
|----------|---------|--------|
| `metrics_val.json` | `carvision/metrics_val.json` | RMSE, MAE, R², MAPE for Model Metrics tab |
| `model_comparison.json` | `carvision/model_comparison.json` | Model vs baseline comparison |
| `feature_columns.json` | `carvision/feature_columns.json` | Feature list for predictions |

### Updating a Model Version (AWS)

```bash
# Option A: Manual upload
aws s3 cp new-model.joblib s3://${MODELS_BUCKET}/bankchurn/model.joblib
kubectl rollout restart deployment/bankchurn-predictor -n ml-portfolio

# Option B: Automated via promote_model.py (recommended)
# Validates metrics → registers in MLflow → uploads to S3/GCS
GCS_MODELS_BUCKET=${MODELS_BUCKET} python scripts/promote_model.py \
  --project carvision --promote --upload-gcs
kubectl rollout restart deployment/carvision-intelligence -n ml-portfolio
```

### Integration: DVC ↔ MLflow ↔ S3

| Tool | Stage | What it Stores | Location |
|------|-------|----------------|----------|
| **DVC** | Development | Raw CSV datasets, `.dvc` metadata | Local + `.dvc-storage/` |
| **MLflow** | Training | Metrics, params, model artifacts, registry | Cluster (`mlflow-server` pod) |
| **S3** | Production | Models, datasets, metrics for serving | `*-ml-models-production`, `*-datasets-production` |

**Full promotion flow** (`scripts/promote_model.py --promote --upload-gcs`):
1. Load local metrics → validate against thresholds
2. Register model + metrics in MLflow Model Registry
3. Upload `model.joblib` + metrics artifacts to S3
4. `kubectl rollout restart` → init containers download fresh artifacts

---

## Phase 10: IRSA — Secure S3 Access

### Why IRSA?

IRSA (IAM Roles for Service Accounts) is the AWS equivalent of GCP's Workload Identity. It allows EKS pods to assume IAM roles without access keys.

### 10.1 Configure IRSA

```bash
# Create IAM policy for S3 read access
cat > /tmp/s3-read-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::ml-portfolio-ml-models-production",
        "arn:aws:s3:::ml-portfolio-ml-models-production/*",
        "arn:aws:s3:::ml-portfolio-datasets-production",
        "arn:aws:s3:::ml-portfolio-datasets-production/*",
        "arn:aws:s3:::ml-portfolio-mlflow-artifacts-production",
        "arn:aws:s3:::ml-portfolio-mlflow-artifacts-production/*"
      ]
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name ml-portfolio-s3-read \
  --policy-document file:///tmp/s3-read-policy.json

# Create IAM role with OIDC trust
OIDC_PROVIDER=$(aws eks describe-cluster --name $EKS_CLUSTER \
  --query "cluster.identity.oidc.issuer" --output text | sed 's|https://||')

cat > /tmp/trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/${OIDC_PROVIDER}"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "${OIDC_PROVIDER}:sub": "system:serviceaccount:ml-portfolio:ml-workload"
        }
      }
    }
  ]
}
EOF

aws iam create-role \
  --role-name ml-portfolio-eks-workload-role \
  --assume-role-policy-document file:///tmp/trust-policy.json

aws iam attach-role-policy \
  --role-name ml-portfolio-eks-workload-role \
  --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/ml-portfolio-s3-read

# Update the K8s service account with the role ARN
kubectl annotate serviceaccount ml-workload -n ml-portfolio \
  eks.amazonaws.com/role-arn=arn:aws:iam::${AWS_ACCOUNT_ID}:role/ml-portfolio-eks-workload-role \
  --overwrite
```

### 10.2 Verify IRSA

```bash
# From inside a pod, verify AWS identity
kubectl exec -n ml-portfolio deployment/bankchurn-predictor -c bankchurn-api -- \
  env | grep AWS
# AWS_ROLE_ARN=arn:aws:iam::XXXXXXXXXXXX:role/ml-portfolio-eks-workload-role
# AWS_WEB_IDENTITY_TOKEN_FILE=/var/run/secrets/eks.amazonaws.com/serviceaccount/token
```

---

## Phase 11: Horizontal Pod Autoscaler (HPA)

Same configuration as GCP — HPA is a Kubernetes-native feature (cloud-agnostic). All 3 ML services have standardized HPA with dual metrics (CPU + memory) and explicit behavior policies. AWS overlays in `k8s/overlays/aws/` mirror GCP configs exactly.

**Resource calibration** (identical to GCP — model sizes are the same):

| Service | Request | Limit | CPU Target | Memory Target | Replicas |
|---------|---------|-------|-----------|--------------|----------|
| BankChurn (ensemble) | 448Mi / 250m | 1Gi / 1000m | 70% | 80% | 1–3 |
| CarVision (API) | 640Mi / 250m | 1Gi / 1000m | 70% | 80% | 1–3 |
| CarVision (Streamlit) | 256Mi / 100m | 512Mi / 500m | — | — | sidecar |
| TelecomAI | 384Mi / 200m | 768Mi / 800m | 75% | 80% | 1–3 |

**Behavior**: scaleDown 300s stabilization (max -50%/min), scaleUp 60s stabilization (max 100% or +2 pods).

```bash
# Verify HPAs
kubectl get hpa -n ml-portfolio
# NAME             REFERENCE                         TARGETS                        MINPODS  MAXPODS  REPLICAS
# bankchurn-hpa    Deployment/bankchurn-predictor     cpu: 2%/70%, memory: 67%/80%   1        3        1
# carvision-hpa    Deployment/carvision-intelligence  cpu: 2%/70%, memory: 24%/80%   1        3        1
# telecom-hpa      Deployment/telecom-intelligence    cpu: 2%/75%, memory: 37%/80%   1        3        1
```

> **Note**: The Kubernetes Metrics Server must be installed on EKS for HPA to work. It's included in the EKS managed node groups by default.

---

## Cost Estimation (Monthly)

| Resource | Spec | Estimated Cost |
|----------|------|---------------|
| EKS Control Plane | Managed | $73 |
| EC2 Nodes (3× t3.large) | On-demand | $180 |
| RDS (db.t3.micro) | Postgres 15 | $15 |
| NAT Gateway | Single AZ | $32 |
| ALB | 1 LB + rules | $22 |
| S3 (models+datasets) | ~165MB | $0.05 |
| ECR | ~5GB images | $0.50 |
| CloudWatch | 30-day retention | $0-5 |
| **Total** | | **~$322/month** |

### Cost Optimization — Demo Mode

| Optimization | Savings | Implementation |
|-------------|---------|----------------|
| **t3.large spot instances** | ~60-70% on EC2 | `capacity_type = "SPOT"` in node group |
| **Reduce to 2 nodes** | ~33% on EC2 | `desired_size = 2` |
| **Single NAT Gateway** | Already configured | `single_nat_gateway = true` |
| **db.t3.micro** | Smallest RDS available | Already configured |
| **ECR lifecycle** | Auto-expire old images | 10 tagged, 7-day untagged (in Terraform) |
| **S3 Glacier lifecycle** | Old models/datasets to Glacier | 90-day transition (models + datasets) |
| **CloudWatch 30-day retention** | Auto-expire logs | Already configured |
| **Deploy and teardown** | Pay only for demo hours | Terraform destroy after evidence collection |

### Demo Cost (5 hours)

```
EKS Control Plane:  $73/720h × 5h  = $0.51
EC2 (3× t3.large):  $0.0832/h × 3 × 5h = $1.25
RDS (db.t3.micro):  $0.017/h × 5h  = $0.09
NAT Gateway:        $0.045/h × 5h  = $0.23
ALB:                $0.0225/h × 5h = $0.11
────────────────────────────────────────
Total (~5 hours):   ~$2.19
```

---

## Verification Checklist

```bash
# 1. All 6 pods running
kubectl get pods -n ml-portfolio
# Expected: 6 pods Running on EC2 nodes

# 2. Health checks pass
for SVC in bankchurn-service carvision-service telecom-service; do
  echo "Testing ${SVC}..."
  kubectl port-forward svc/${SVC} 8080:80 -n ml-portfolio &
  sleep 2
  curl -s http://localhost:8080/health | python3 -m json.tool
  kill %1 2>/dev/null
done

# 3. ALB has DNS
kubectl get ingress -n ml-portfolio
# Expected: ADDRESS column shows ALB DNS name

# 4. Predictions work
kubectl port-forward svc/bankchurn-service 8001:80 -n ml-portfolio &
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"CreditScore":650,"Geography":"France","Gender":"Male","Age":35,"Tenure":5,"Balance":50000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":75000}'

# 5. MLflow UI
kubectl port-forward svc/mlflow-service 5000:5000 -n ml-portfolio &
# Open http://localhost:5000

# 6. Grafana
kubectl port-forward svc/grafana-service 3000:3000 -n ml-portfolio &
# Open http://localhost:3000

# 7. Prometheus targets
kubectl port-forward svc/prometheus-service 9090:9090 -n ml-portfolio &
# Open http://localhost:9090/targets

# 8. ECR images
aws ecr describe-repositories --output table

# 9. S3 models + datasets
aws s3 ls s3://${MODELS_BUCKET}/ --recursive --human-readable
aws s3 ls s3://ml-portfolio-datasets-production/ --recursive --human-readable
```

---

## Teardown (When Done Collecting Evidence)

```bash
# Option A: Delete EKS workloads only (keep infra)
kubectl delete namespace ml-portfolio

# Option B: Full teardown (stop all billing)
cd infra/terraform/aws
terraform destroy -auto-approve

# Option C: Delete specific expensive resources first
aws rds delete-db-instance --db-instance-identifier ml-portfolio-mlflow-db-production --skip-final-snapshot
# Then full teardown with Terraform
```

> **Important**: Always teardown after collecting evidence. AWS costs ~$2-3 per 5-hour session.
> The same infrastructure can be recreated with `terraform apply` in ~20 minutes.

---

## Troubleshooting Reference

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| EKS nodes not joining | Nodes in `NotReady` state | Check security groups, IAM role |
| ALB not provisioned | No ADDRESS in Ingress | Install AWS LB Controller (Phase 2.4) |
| S3 `AccessDenied` | Init container fails | Configure IRSA (Phase 10) |
| ECR `unauthorized` | `docker push` fails | Re-run `aws ecr get-login-password` |
| RDS connection refused | MLflow can't connect | Check security group allows 5432 from EKS |
| NAT Gateway costs | $32/month even idle | Use `single_nat_gateway = true` |
| `Insufficient cpu` | Pods Pending | Increase node group size or instance type |

### Useful Debug Commands

```bash
# Pod logs
kubectl logs -n ml-portfolio <pod-name> --tail=50
kubectl logs -n ml-portfolio <pod-name> -c download-model  # model init container
kubectl logs -n ml-portfolio <pod-name> -c download-data   # dataset init container

# Pod details
kubectl describe pod <pod-name> -n ml-portfolio

# Events
kubectl get events -n ml-portfolio --sort-by='.lastTimestamp'

# Resource usage
kubectl top pods -n ml-portfolio
kubectl top nodes

# AWS-specific
aws eks describe-cluster --name $EKS_CLUSTER --query cluster.status
aws ec2 describe-instances --filters "Name=tag:eks:cluster-name,Values=$EKS_CLUSTER" --query "Reservations[].Instances[].{ID:InstanceId,State:State.Name,Type:InstanceType}"
```

---

## Deployment Log (Execution Template)

### Timeline

| Phase | Est. Duration | Status | Notes |
|-------|--------------|--------|-------|
| Phase 1: AWS Setup | 20 min | Pending | IAM user, CLI config, state backend |
| Phase 2: Terraform | 30 min | Pending | VPC, EKS, RDS, S3, ECR |
| Phase 3: Docker Images | 15-30 min | Pending | Build and push to ECR |
| Phase 4: Model Upload | 10 min | Pending | 3 models to S3 |
| Phase 5: K8s Deploy | 20 min | Pending | AWS overlay manifests |
| Phase 6: MLflow | 10 min | Pending | RDS PostgreSQL backend |
| Phase 7: Monitoring | 10 min | Pending | Same Prometheus/Grafana stack |
| Phase 8: CI/CD | 15 min | Pending | GitHub Secrets + workflow |
| Phase 9: Init Containers | Already in manifests | Pending | S3 model download |
| Phase 10: IRSA | 10 min | Pending | IAM role for pods |
| **Total** | **~2.5 hours** | **Pending** | 6/6 pods + ALB + monitoring |
