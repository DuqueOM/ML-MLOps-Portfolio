# AWS S3 Storage — ML Portfolio

## Overview

All S3 storage is consolidated in `main.tf`. The previous `s3-artifacts-simple.tf` was removed to eliminate bucket naming conflicts and encryption inconsistencies.

## Buckets Created (via `main.tf`)

### 1. ML Models (`ml-portfolio-ml-models-{env}`)
- **Versioning**: Enabled (immutable model history)
- **Encryption**: `aws:kms` (AWS-managed KMS key)
- **Public Access**: Blocked (4-way block)
- **Logging**: Self-referential access logs at `access-logs/ml-models/`
- **Lifecycle**: Non-current versions → Glacier after 90d, expire after 365d

### 2. Datasets (`ml-portfolio-datasets-{env}`)
- **Versioning**: Enabled
- **Encryption**: `aws:kms`
- **Public Access**: Blocked
- **Logging**: Self-referential access logs at `access-logs/datasets/`
- **DVC**: Connected via `.dvc/config` as `aws-prod` remote

### 3. MLflow Artifacts (`ml-portfolio-mlflow-artifacts-{env}`)
- **Versioning**: Enabled
- **Encryption**: `aws:kms`
- **Public Access**: Blocked
- **Logging**: Self-referential access logs at `access-logs/mlflow/`
- **Lifecycle**: Non-current versions → Glacier after 90d, expire after 365d

## Secrets Management

Database passwords are managed via **AWS Secrets Manager** (parity with GCP Secret Manager):

```bash
# Create secret
aws secretsmanager create-secret \
  --name ml-portfolio-mlflow-db-password-production \
  --secret-string "$(openssl rand -base64 24)"

# Terraform reads automatically when db_password = "" in tfvars
```

## Integration with CI/CD

```yaml
# .github/workflows/deploy-model.yml
- name: Upload model to S3
  run: |
    aws s3 cp artifacts/model.joblib \
      s3://ml-portfolio-ml-models-production/bankchurn/v${VERSION}/model.joblib \
      --metadata "version=${VERSION},commit=$(git rev-parse HEAD)"
```

## Integration with DVC

```bash
# Pull training data from S3
dvc pull data/raw/

# Push new data versions
dvc push

# Switch to GCP remote
dvc remote default gcp-prod
dvc push
```

## Cost Estimation

| Resource | Dev | Production |
|----------|-----|------------|
| S3 Standard (10–100 GB) | ~$0.23 | ~$2.30 |
| Glacier Archive | — | ~$2.00 |
| PUT/GET requests | ~$0.05 | ~$0.50 |
| **Total** | **~$0.30/mo** | **~$5/mo** |

## Security Checklist

- [x] Versioning enabled on all buckets
- [x] `aws:kms` encryption (consistent across all buckets)
- [x] Public access blocked (4-way)
- [x] Access logging enabled
- [x] Lifecycle rules for cost management
- [x] Secrets Manager for database passwords (no hardcoded credentials)
- [x] IAM auth enabled on RDS
