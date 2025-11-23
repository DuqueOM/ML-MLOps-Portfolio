# S3 Artifact Store - Simplified Infrastructure Module

## Overview

This module provides a lightweight, production-ready S3 infrastructure for ML model artifact storage and MLflow experiment tracking. It demonstrates Infrastructure as Code (IaC) best practices for MLOps without the complexity of a full EKS/GKE deployment.

## What This Creates

### 1. ML Models Artifact Store
- **Bucket**: `{project_name}-mlops-models-store-{environment}`
- **Versioning**: Enabled (immutable model history)
- **Encryption**: AES256 server-side encryption
- **Public Access**: Blocked (security compliance)
- **Lifecycle**: Old versions archived to Glacier after 90 days, deleted after 365 days

### 2. MLflow Artifacts Store
- **Bucket**: `{project_name}-mlflow-artifacts-{environment}`
- **Versioning**: Enabled
- **Encryption**: AES256 server-side encryption
- **Public Access**: Blocked

## Quick Start

### Prerequisites

```bash
# Install Terraform
brew install terraform  # macOS
# or
sudo apt-get install terraform  # Linux

# Configure AWS credentials
aws configure
```

### Deploy

```bash
cd infra/terraform/aws

# Initialize Terraform (first time only)
terraform init

# Review what will be created
terraform plan

# Apply the infrastructure
terraform apply

# Outputs will show your bucket names
```

## Configuration

The module uses variables from `variables.tf`. To customize:

```hcl
# Example: terraform.tfvars
project_name = "ml-portfolio"
environment  = "production"
aws_region   = "us-east-1"
```

## Integration with CI/CD

Once deployed, configure your GitHub Actions workflow to upload artifacts:

```yaml
# .github/workflows/deploy-model.yml
- name: Upload model to S3
  run: |
    aws s3 cp artifacts/model.pkl \
      s3://ml-portfolio-mlops-models-store-production/models/$(git rev-parse --short HEAD)/model.pkl \
      --metadata "version=$(git describe --tags),commit=$(git rev-parse HEAD)"
```

## Integration with MLflow

Configure MLflow to use the S3 bucket:

```python
# In your MLflow tracking script
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")  # Your MLflow server
mlflow.set_experiment("my-experiment")

# MLflow will automatically use S3 if configured via environment:
# export MLFLOW_S3_ENDPOINT_URL=s3.us-east-1.amazonaws.com
# export MLFLOW_ARTIFACT_ROOT=s3://ml-portfolio-mlflow-artifacts-production
```

## Cost Estimation

### Development Environment
- S3 Storage (10 GB): ~$0.23/month
- PUT/GET requests (10k/month): ~$0.05/month
- **Total**: ~$0.30/month

### Production Environment
- S3 Storage (100 GB): ~$2.30/month
- Glacier Archive (500 GB): ~$2.00/month
- PUT/GET requests (100k/month): ~$0.50/month
- **Total**: ~$5/month

## Security Best Practices

1. **Versioning**: Never lose a model version
2. **Encryption**: At-rest encryption (AES256)
3. **Public Access**: Blocked by default
4. **Lifecycle**: Automatic archiving to reduce costs
5. **IAM**: Use least-privilege policies (not included in this simplified module)

## Advanced: IAM Policy for CI/CD

To allow GitHub Actions to upload artifacts, create an IAM user with this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::ml-portfolio-mlops-models-store-production",
        "arn:aws:s3:::ml-portfolio-mlops-models-store-production/*"
      ]
    }
  ]
}
```

## Cleanup

To destroy the infrastructure:

```bash
terraform destroy
```

⚠️ **Warning**: This will delete all model artifacts. Export important models before destroying.

## Why This Approach?

This simplified module demonstrates:
- ✅ **Infrastructure as Code**: Reproducible, version-controlled infrastructure
- ✅ **Cost-Effective**: S3 is cheaper than full K8s clusters for portfolio projects
- ✅ **Production-Ready**: Includes versioning, encryption, lifecycle management
- ✅ **Interview-Ready**: Shows you understand IaC, security, and cost optimization

For enterprise projects, consider the full `main.tf` module with EKS, RDS, and ECR.
