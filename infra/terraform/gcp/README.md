# GCP Terraform Configuration — ML Portfolio

> GKE + Cloud SQL + GCS + Artifact Registry infrastructure for the 3 ML services.
> Workload Identity enabled. Secret Manager for credentials. See the [umbrella README](../README.md) for full context.
>
> Architecture decisions explaining these infrastructure choices:
> - [ADR-016](../../../docs/decisions/016-gcp-aws-performance-parity.md): Why e2-medium and not c2-standard-4
> - [ADR-017](../../../docs/decisions/017-custom-vs-managed-ml-platforms.md): Why custom GKE and not Vertex AI as primary

---

## 📋 Resources Created

| Resource | GCP Name | Key Configuration |
|---|---|---|
| GKE Cluster | `ml-portfolio-gke-{env}` | Workload Identity, network policy, auto-upgrade, private nodes |
| Node Pool | `ml-services-pool` | e2-medium × N (min=1, max=5 with autoscaling) |
| Cloud SQL | `ml-portfolio-mlflow-db-{env}` | PostgreSQL 15, SSL required, audit flags, IAM auth |
| GCS ml-models | `{project}-ml-models-{env}` | NEARLINE 90d, delete 365d, access logging |
| GCS mlflow-artifacts | `{project}-mlflow-artifacts-{env}` | NEARLINE 90d, delete 365d, access logging |
| GCS audit-logs | `{project}-audit-logs-{env}` | Logging target, auto-delete 90d |
| Artifact Registry | `{region}-docker.pkg.dev/{project}/ml-portfolio-images` | bankchurn, nlpinsight, chicagotaxi |
| Service Account | `ml-portfolio-gke-workload@{project}.iam.gserviceaccount.com` | Workload Identity binding |
| Secret Manager | `mlflow-db-password` | DB password, auto-rotation documented below |

---

## 🔐 Secrets Management

**⚠️ CRITICAL**: Never commit `terraform.tfvars` with real passwords to git.

### Option 1: GCP Secret Manager (Recommended for Production)

```bash
# 1. Create the secret
gcloud secrets create mlflow-db-password \
  --data-file=<(openssl rand -base64 24) \
  --replication-policy="automatic"

# 2. Grant access to the Terraform SA
gcloud secrets add-iam-policy-binding mlflow-db-password \
  --member="serviceAccount:terraform@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# 3. Run terraform without db_password in tfvars (reads from Secret Manager)
terraform plan
```

### Option 2: Environment Variable (Recommended for Local Dev)

```bash
export TF_VAR_db_password="$(openssl rand -base64 24)"
terraform plan
terraform apply
```

### Option 3: Local terraform.tfvars (Gitignored)

```bash
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
terraform plan
```

---

## 🔑 Workload Identity

Workload Identity allows GKE pods to access GCP APIs (GCS, Artifact Registry, Secret Manager) using GCP identities without hardcoded credentials.

```bash
# Verify Workload Identity is active on the cluster
gcloud container clusters describe ml-portfolio-gke-production \
  --region=us-central1 \
  --format="value(workloadIdentityConfig.workloadPool)"
# Expected output: {project_id}.svc.id.goog

# Verify the K8s ServiceAccount binding
kubectl describe serviceaccount ml-workload -n ml-portfolio | grep "Annotations"
# Expected output:
# Annotations: iam.gke.io/gcp-service-account: ml-portfolio-gke-workload@{project}.iam.gserviceaccount.com

# Verify that pods can access GCS
kubectl exec -it -n ml-portfolio deploy/bankchurn-predictor -- \
  gsutil ls gs://ml-portfolio-ml-models-production/
# Should list models without credentials error

# The SA (ml-portfolio-gke-workload) has the following permissions (defined in iam.tf):
# - storage.objectViewer on ml-models bucket
# - storage.objectAdmin on mlflow-artifacts bucket
# - cloudsql.client for Cloud SQL access
```

---

## 🏗️ Staging vs Production Differences

| Aspect | `terraform.tfvars` (prod) | `staging.tfvars` |
|---|---|---|
| Node size | `e2-medium` | `e2-small` |
| Min nodes | 1 | 1 |
| Max nodes | 5 | 2 |
| Cloud SQL tier | `db-f1-micro` | `db-f1-micro` |
| SQL backups | Enabled | Disabled |
| Preemptible VMs | No | Yes (60-70% cheaper) |
| Artifact Registry | 3 repos | 3 repos (shared) |
| GCS retention | 365 days | 90 days |
| Budget alert | $100/mo | $50/mo |

```bash
# Deploy to staging
terraform plan -var-file=staging.tfvars
terraform apply -var-file=staging.tfvars

# Destroy staging at end of day (FinOps)
terraform destroy -var-file=staging.tfvars
```

---

## 🚀 Deployment

```bash
# Initialize (GCS backend must already exist)
gsutil mb -l us-central1 gs://ml-portfolio-terraform-state/
terraform init

# Plan and apply
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars

# View all outputs
terraform output
```

---

## ✅ Post-Deploy Verification

```bash
# 1. Cluster accessible
gcloud container clusters get-credentials ml-portfolio-gke-production --region us-central1
kubectl get nodes
# Expected: 1-4 nodes in Ready state

# 2. Namespaces created
kubectl get namespaces | grep ml-portfolio
# Expected: ml-portfolio  Active

# 3. Cloud SQL accessible from inside the cluster
kubectl run psql-test --rm -it --image=postgres:15 --restart=Never \
  --command -- psql "host=$(terraform output -raw mlflow_db_connection_name) \
  dbname=mlflow user=mlflow sslmode=require"
# Expected: psql prompt

# 4. GCS accessible from pods
kubectl exec -it -n ml-portfolio deploy/bankchurn-predictor -- \
  gsutil ls gs://$(terraform output -raw ml_models_bucket)/
# Expected: file listing

# 5. Artifact Registry accessible for push
gcloud auth configure-docker us-central1-docker.pkg.dev
docker pull us-central1-docker.pkg.dev/${PROJECT_ID}/ml-portfolio-images/bankchurn:latest
# Expected: image downloaded
```

---

## 🔁 Rotating Compromised Credentials

If a password was accidentally committed:

```bash
# 1. Generate new password
NEW_PASSWORD=$(openssl rand -base64 24)

# 2. Update Cloud SQL
gcloud sql users set-password mlflow \
  --instance=ml-portfolio-mlflow-db-production \
  --password="$NEW_PASSWORD"

# 3. Update Secret Manager
echo -n "$NEW_PASSWORD" | gcloud secrets versions add mlflow-db-password --data-file=-

# 4. Update the K8s secret (if MLflow connects from GKE)
kubectl create secret generic mlflow-db-secret \
  --from-literal=password="$NEW_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

# 5. Restart affected pods
kubectl rollout restart deployment/mlflow-server -n ml-portfolio

# 6. Verify MLflow connects correctly
kubectl logs -n ml-portfolio -l app=mlflow-server --tail=20
# Look for: "Connected to database successfully"
```

---

## 🤖 Vertex AI Integration (ADR-017)

As a complement to custom serving on GKE, BankChurn can also be deployed to Vertex AI to demonstrate managed platform capabilities. See [ADR-017](../../../docs/decisions/017-custom-vs-managed-ml-platforms.md).

```bash
# Vertex AI scripts use the same SA and GCS bucket from this infra
# scripts/vertex_ai/deploy_endpoint.py

# Verify SA is available for Vertex AI
gcloud iam service-accounts describe \
  ml-portfolio-gke-workload@${PROJECT_ID}.iam.gserviceaccount.com
# Note: roles/aiplatform.user is required for Vertex AI but not yet in iam.tf (Phase 8)

# The model is uploaded from the same GCS bucket
gsutil ls gs://$(terraform output -raw ml_models_bucket)/vertex-ai/bankchurn/
# Expected: model.joblib and metadata
```

---

## 📚 GCP References

- [GKE Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
- [Cloud SQL IAM Authentication](https://cloud.google.com/sql/docs/postgres/iam-authentication)
- [GCS Lifecycle Management](https://cloud.google.com/storage/docs/lifecycle)
- [Secret Manager Best Practices](https://cloud.google.com/secret-manager/docs/best-practices)
- [Artifact Registry Auth](https://cloud.google.com/artifact-registry/docs/docker/authentication)