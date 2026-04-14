# AWS S3 Storage — ML Portfolio

> All S3 configuration is consolidated in `storage.tf`.
> The previous `s3-artifacts-simple.tf` was removed to avoid naming conflicts and inconsistent encryption.
> For the complete S3 cost strategy, see the [umbrella README](../README.md#cost-estimation).

---

## 🪣 Buckets Created (`storage.tf`)

### 1. ML Models — `ml-portfolio-ml-models-{env}`

| Property | Value |
|---|---|
| Versioning | Enabled (immutable model history) |
| Encryption | `aws:kms` (AWS-managed KMS key) |
| Public Access | Blocked (4-way block) |
| Access Logging | Self-referential (`access-logs/ml-models/` prefix) |
| Lifecycle | Non-current versions → Glacier 90d, expire 365d |
| Usage | Init containers download models via IRSA on pod startup |

### 2. Datasets — `ml-portfolio-datasets-{env}`

| Property | Value |
|---|---|
| Versioning | Enabled |
| Encryption | `aws:kms` |
| Public Access | Blocked |
| Access Logging | Self-referential (`access-logs/datasets/` prefix) |
| Usage | DVC remote `aws-prod`. Training jobs read data from here |

### 3. MLflow Artifacts — `ml-portfolio-mlflow-artifacts-{env}`

| Property | Value |
|---|---|
| Versioning | Enabled |
| Encryption | `aws:kms` |
| Public Access | Blocked |
| Access Logging | Self-referential (`access-logs/mlflow/` prefix) |
| Lifecycle | Non-current versions → Glacier 90d, expire 365d |
| Usage | MLflow stores checkpoints, versioned models, metrics |

> **Architecture note**: AWS uses self-referential logging (each bucket logs to itself with a prefix). GCP uses a dedicated `audit-logs` bucket instead. Both patterns are valid — the dedicated bucket is cleaner for centralized auditing, while self-referential is simpler to set up. A future improvement (Phase 8) would be to add a dedicated access-logs bucket to AWS for parity with GCP.

---

## 🔑 IRSA — IAM Roles for Service Accounts

IRSA allows EKS pods to access S3 without hardcoded credentials. It is the critical piece that connects K8s with S3.

```bash
# Verify IRSA is configured on the ServiceAccount
kubectl describe serviceaccount ml-workload -n ml-portfolio
# Should show:
# Annotations: eks.amazonaws.com/role-arn: arn:aws:iam::{ACCOUNT}:role/ml-portfolio-ml-workload-production

# The IAM role has the following permissions (defined in compute.tf):
# ALLOW s3:GetObject, s3:ListBucket on ml-models bucket (for init containers)
# ALLOW s3:PutObject, s3:GetObject on mlflow-artifacts bucket (for MLflow)
# ALLOW s3:GetObject on datasets bucket (for training jobs)
# DENY s3:DeleteObject on all buckets (protection against accidental deletion)

# Verify access from inside a pod
kubectl exec -it -n ml-portfolio deploy/bankchurn-predictor -- \
  aws s3 ls s3://ml-portfolio-ml-models-production/
# Should list files without credentials error
```

---

## 🔔 S3 Event Notifications → Drift-Triggered Retraining

S3 buckets can trigger automatic retraining when new data is deposited. This connects with [ADR-006](../../../docs/decisions/006-drift-triggered-retraining.md).

```bash
# Configure notification on the datasets bucket
aws s3api put-bucket-notification-configuration \
  --bucket ml-portfolio-datasets-production \
  --notification-configuration '{
    "LambdaFunctionConfigurations": [{
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {"Key": {"FilterRules": [{"Name": "prefix", "Value": "production/"}]}},
      "LambdaFunctionArn": "arn:aws:lambda:{region}:{account}:function:trigger-retrain-bankchurn"
    }]
  }'
```

> Simpler alternative (already implemented via ADR-006): the K8s CronJob queries Prometheus for PSI scores and triggers retraining via the GitHub Actions API. S3 Event Notifications are the next pattern when real-time retraining is needed.

---

## 🚀 CI/CD Integration

```yaml
# .github/workflows/deploy-model.yml (excerpt)
- name: Upload model to S3
  run: |
    aws s3 cp artifacts/model.joblib \
      s3://ml-portfolio-ml-models-production/bankchurn/v${VERSION}/model.joblib \
      --metadata "version=${VERSION},commit=$(git rev-parse HEAD),auc=${AUC}" \
      --sse aws:kms
    
    # Verify the upload succeeded
    aws s3 ls s3://ml-portfolio-ml-models-production/bankchurn/v${VERSION}/
```

---

## 🔗 DVC Integration

See the [umbrella README](../README.md#dvc-integration) for the complete configuration.

```bash
# Pull training data
dvc pull data/raw/

# Push new versions
dvc push
```

---

## 🔐 KMS Encryption

All S3 buckets use `aws:kms` (AWS-managed KMS key). This means:
- AWS handles key rotation automatically (yearly)
- No custom KMS key ARN is exported (aws-managed keys don't require it)
- To upgrade to Customer-Managed Keys (CMK), add a `aws_kms_key` resource and reference it in `storage.tf`

```bash
# Verify encryption on a bucket
aws s3api get-bucket-encryption --bucket ml-portfolio-ml-models-production
# Expected: {"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms"}}]}
```

---

## 🌐 VPC Endpoints for S3 (Future Optimization)

Currently, EKS → S3 traffic goes through NAT Gateway (egress cost ~$0.045/GB). Adding an S3 VPC Endpoint would make this traffic free.

```hcl
# Future improvement for network.tf:
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = module.vpc.vpc_id
  service_name = "com.amazonaws.${var.aws_region}.s3"
  route_table_ids = module.vpc.private_route_table_ids
}
```

> This is a Phase 8 optimization. At current data volumes (<1GB/mo), egress costs are negligible.

---

## 💰 S3 Cost Estimation

| Resource | Dev/Staging | Production |
|---|---|---|
| S3 Standard (active) | ~$0.05 | ~$1.00 |
| S3 Glacier (archived) | — | ~$0.50 |
| KMS requests | ~$0.01 | ~$0.20 |
| PUT/GET requests | ~$0.05 | ~$0.30 |
| Access Logs (90d) | ~$0.01 | ~$0.10 |
| **Total** | **~$0.12/mo** | **~$2.10/mo** |

---

## ✅ Security Checklist

- [x] All buckets use `aws:kms` encryption
- [x] All buckets have 4-way public access block
- [x] All buckets have versioning enabled
- [x] All buckets have access logging
- [x] Lifecycle rules archive to Glacier (90d) and expire (365d)
- [x] No hardcoded credentials in `staging.tfvars`
- [x] Secrets Manager integration for `db_password`
- [ ] VPC Endpoint for S3 (Phase 8)
- [ ] Customer-Managed KMS keys (Phase 8)
- [ ] Dedicated access-logs bucket (Phase 8)