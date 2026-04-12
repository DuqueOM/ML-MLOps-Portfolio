# GCP Terraform Configuration

Infrastructure as Code for ML Portfolio deployment on Google Cloud Platform.

## Security: Managing Secrets

**⚠️ CRITICAL**: Never commit `terraform.tfvars` with real passwords to git.

### Option 1: GCP Secret Manager (Recommended for Production)

```bash
# 1. Create secret in GCP Secret Manager
gcloud secrets create mlflow-db-password \
  --data-file=<(openssl rand -base64 24) \
  --replication-policy="automatic"

# 2. Grant Terraform service account access
gcloud secrets add-iam-policy-binding mlflow-db-password \
  --member="serviceAccount:terraform@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# 3. Update main.tf to read from Secret Manager (see main.tf data block)

# 4. Run terraform without db_password in tfvars
terraform plan  # Will read from Secret Manager
```

### Option 2: Environment Variable (Recommended for Local Dev)

```bash
# Generate secure password
export TF_VAR_db_password="$(openssl rand -base64 24)"

# Run terraform (will use env var)
terraform plan
terraform apply
```

### Option 3: Local terraform.tfvars (Gitignored)

```bash
# Copy example
cp terraform.tfvars.example terraform.tfvars

# Edit with real values (file is gitignored)
nano terraform.tfvars

# Run terraform
terraform plan
```

## Rotating Compromised Passwords

If a password was accidentally committed:

```bash
# 1. Generate new password
NEW_PASSWORD=$(openssl rand -base64 24)

# 2. Update Cloud SQL instance
gcloud sql users set-password mlflow \
  --instance=ml-portfolio-mlflow-db-production \
  --password="$NEW_PASSWORD"

# 3. Update Secret Manager (if using)
echo -n "$NEW_PASSWORD" | gcloud secrets versions add mlflow-db-password --data-file=-

# 4. Update K8s secret (if MLflow connects from GKE)
kubectl create secret generic mlflow-db-secret \
  --from-literal=password="$NEW_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

# 5. Restart affected pods
kubectl rollout restart deployment/mlflow-server -n ml-portfolio
```

## Deployment

```bash
# Initialize
terraform init

# Plan changes
terraform plan -var-file=terraform.tfvars

# Apply
terraform apply -var-file=terraform.tfvars

# View outputs
terraform output
```

## Resources Created

- **GKE Cluster**: `ml-portfolio-gke-production` (Workload Identity, network policy, private nodes)
- **Cloud SQL** (PostgreSQL 15): `ml-portfolio-mlflow-db-production` (SSL required, audit flags)
- **Cloud Storage**:
  - `ml-models` — lifecycle (NEARLINE 90d, delete 365d), access logging
  - `mlflow-artifacts` — lifecycle (NEARLINE 90d, delete 365d), access logging
  - `audit-logs` — dedicated logging target (auto-delete 90d)
  - All buckets: `public_access_prevention = enforced`, uniform access
- **Artifact Registry**: Docker images for 3 ML services
- **VPC Network**: Custom network with private subnets, VPC flow logs
- **IAM**: Bucket-level least-privilege (objectViewer for models, objectAdmin for mlflow only)

See `main.tf` for complete resource definitions.
