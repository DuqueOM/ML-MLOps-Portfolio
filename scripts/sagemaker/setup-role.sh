#!/usr/bin/env bash
# Create IAM role for SageMaker endpoint execution.
#
# Usage:
#   export AWS_PROFILE=ml-portfolio
#   bash scripts/sagemaker/setup-role.sh
#
# This creates:
#   - SageMakerExecutionRole with:
#     - SageMaker full access
#     - S3 read access to model bucket
#     - CloudWatch Logs for endpoint logging

set -euo pipefail

ROLE_NAME="SageMakerExecutionRole"
S3_BUCKET="ml-portfolio-ml-models-production"
REGION="${AWS_REGION:-us-east-1}"

echo "🔧 Creating SageMaker execution role: ${ROLE_NAME}"

# Trust policy — allows SageMaker to assume this role
TRUST_POLICY=$(cat <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "sagemaker.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
)

# Check if role already exists
if aws iam get-role --role-name "${ROLE_NAME}" &>/dev/null; then
    echo "✅ Role ${ROLE_NAME} already exists:"
    aws iam get-role --role-name "${ROLE_NAME}" --query 'Role.Arn' --output text
    exit 0
fi

# Create role
aws iam create-role \
    --role-name "${ROLE_NAME}" \
    --assume-role-policy-document "${TRUST_POLICY}" \
    --description "Execution role for ML Portfolio SageMaker endpoints" \
    --tags Key=Project,Value=ML-MLOps-Portfolio Key=ManagedBy,Value=script

echo "📎 Attaching managed policies..."

# SageMaker full access (includes ECR pull for containers)
aws iam attach-role-policy \
    --role-name "${ROLE_NAME}" \
    --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

# S3 read access for model artifacts
S3_POLICY=$(cat <<EOF
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
        "arn:aws:s3:::${S3_BUCKET}",
        "arn:aws:s3:::${S3_BUCKET}/*"
      ]
    }
  ]
}
EOF
)

aws iam put-role-policy \
    --role-name "${ROLE_NAME}" \
    --policy-name "S3ModelAccess" \
    --policy-document "${S3_POLICY}"

# CloudWatch Logs
aws iam attach-role-policy \
    --role-name "${ROLE_NAME}" \
    --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess

ROLE_ARN=$(aws iam get-role --role-name "${ROLE_NAME}" --query 'Role.Arn' --output text)

echo ""
echo "✅ Role created successfully!"
echo "   Name: ${ROLE_NAME}"
echo "   ARN:  ${ROLE_ARN}"
echo ""
echo "⏳ Wait ~10 seconds for IAM propagation before deploying endpoint."
