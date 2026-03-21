# ADR-012: Security Scanner Findings — Staging vs Production Policy

- **Status**: Accepted
- **Date**: 2026-03-13
- **Authors**: Duque Ortega Mutis

> **TL;DR**: Adopted a tiered remediation policy for tfsec/checkov findings — acknowledge all findings with inline justification in staging, enforce full remediation (CMKs, VPC Flow Logs, access logging) in production. Every finding has a documented rationale, not a blind suppression. This demonstrates security awareness without over-engineering for demo data.

## Problem

Static security scanners (tfsec, checkov) report findings that are valid security recommendations but not all are appropriate for every environment tier. Blindly fixing everything adds cost and complexity; ignoring everything signals lack of security awareness.

## Decision

Adopt a **tiered remediation policy** based on environment:

### Staging (current deployment)
- **Acknowledge all findings** with `#tfsec:ignore` inline comments including justification
- **Use AWS-managed encryption** (SSE-S3, SSE-KMS with AWS-managed keys) instead of customer-managed CMKs
- **Skip cost-adding features** (VPC Flow Logs, S3 access logging, RDS Performance Insights) that don't improve security posture for non-sensitive demo data
- **Restrict but allow** public API access (EKS endpoint restricted to allowed CIDRs, not 0.0.0.0/0)

### Production (documented upgrade path)
- Require customer-managed KMS keys (CMK) for PII/PHI data
- Enable VPC Flow Logs, S3 access logging, CloudWatch CMK encryption
- Enable RDS Performance Insights with CMK
- Restrict EKS public access to VPN/bastion CIDRs only or disable entirely (private-only + VPN)
- Enforce via CI pipeline: `tfsec --minimum-severity HIGH --exclude-ignored`

## Findings Inventory

### GCP (4 findings, all acknowledged)

| ID | Severity | Resource | Justification |
|----|----------|----------|---------------|
| AVD-GCP-0047 | HIGH | GKE Cluster | PodSecurityPolicy deprecated K8s 1.21+; using Pod Security Standards (PSS) via namespace labels |
| AVD-GCP-0048 | HIGH | GKE Node Config | Legacy metadata blocked by GKE Metadata Server (workload_metadata_config) |
| AVD-GCP-0066 | LOW | GCS ml_models | Google-managed encryption; CMEK adds $0.06/10K ops |
| AVD-GCP-0066 | LOW | GCS mlflow_artifacts | Same as above |

### AWS (15 findings, all acknowledged)

| ID | Severity | Resource | Justification |
|----|----------|----------|---------------|
| AVD-AWS-0040 | CRITICAL | EKS Module | Public access restricted to allowed_cidr_blocks; private access enabled |
| AVD-AWS-0104 | CRITICAL | EKS Node SG | Egress required for ECR pulls, S3 downloads, CloudWatch; NAT Gateway only |
| AVD-AWS-0132 | HIGH | S3 Buckets (×5) | Uses aws:kms (AWS-managed); CMK adds $1/key/month |
| AVD-AWS-0178 | MEDIUM | VPC | Flow Logs add ~$0.50/GB; staging uses EKS audit logs |
| AVD-AWS-0089 | MEDIUM | S3 Artifacts (×2) | Access logging adds storage cost for demo data |
| AVD-AWS-0033 | LOW | ECR Repos (×3) | AES256 sufficient for container images; KMS for compliance |
| AVD-AWS-0133 | LOW | RDS MLflow | Performance Insights not needed for minimal staging DB load |
| AVD-AWS-0017 | LOW | CloudWatch Logs | AWS-managed encryption; CMK for audit-required environments |

### Checkov Summary

| Cloud | Passed | Total | Rate | Notes |
|-------|--------|-------|------|-------|
| GCP | 51 | 71 | 72% | Remaining findings overlap with tfsec (CMK, metadata) |
| AWS | 84 | 116 | 72% | Remaining findings overlap with tfsec (CMK, logging, flow logs) |

## Alternatives Considered

1. **Fix everything** — Adds ~$15-25/month in KMS keys, logging storage, and flow logs. Over-engineering for a staging demo with no real user data.
2. **Ignore silently** — Scanners pass but no evidence of security awareness. Poor signal to reviewers.
3. **Suppress globally** — Using `.tfsec.yml` exclude-all hides findings. Loses per-resource traceability.

## Consequences

- Every finding has an inline justification visible in code review
- CI pipeline reports findings as advisory (non-blocking) with context
- Production promotion requires removing `#tfsec:ignore` and implementing full controls
- Reviewers see security awareness + cost-conscious engineering judgment

## Production Checklist (when promoting to production)

```hcl
# 1. Create KMS keys for each service
resource "aws_kms_key" "ml_data" {
  description             = "CMK for ML data encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

# 2. Reference in S3/ECR/CloudWatch/RDS
sse_algorithm     = "aws:kms"
kms_master_key_id = aws_kms_key.ml_data.arn

# 3. Enable VPC Flow Logs
enable_flow_log                      = true
flow_log_destination_type            = "cloud-watch-logs"
flow_log_cloudwatch_log_group_kms_id = aws_kms_key.vpc_logs.arn

# 4. Enable S3 access logging (separate logging bucket)
# 5. Enable RDS Performance Insights with CMK
# 6. Restrict EKS to private-only + VPN bastion
# 7. Run: tfsec --minimum-severity HIGH --exclude-ignored (blocking)
```

## References

- [tfsec ignore syntax](https://aquasecurity.github.io/tfsec/latest/guides/configuration/ignores/)
- [AWS Well-Architected: Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/)
- [GCP Security Best Practices](https://cloud.google.com/security/best-practices)
