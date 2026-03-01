#!/bin/bash
# =========================================
# ML-MLOps Portfolio - GCP Deployment Evidence Collector
# Run this script to capture terminal evidence for the portfolio
# Usage: bash scripts/collect_evidence.sh > docs/evidence/deployment_evidence.txt
# =========================================

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-ml-portfolio-duque-om-202602}"
REGION="${REGION:-us-central1}"
AR_REPO="${REGION}-docker.pkg.dev/${PROJECT_ID}/ml-portfolio-images"

echo "========================================="
echo "ML-MLOps Portfolio - GCP Deployment Evidence"
echo "Date: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "========================================="

echo ""
echo "=== 1. Cluster Nodes ==="
kubectl get nodes -o wide 2>&1 || echo "ERROR: Cannot reach cluster"

echo ""
echo "=== 2. All Pods ==="
kubectl get pods -n ml-portfolio -o wide 2>&1

echo ""
echo "=== 3. Services & Ingress ==="
kubectl get svc,ingress -n ml-portfolio 2>&1

echo ""
echo "=== 4. Resource Usage ==="
kubectl top pods -n ml-portfolio 2>/dev/null || echo "Metrics server not available yet"

echo ""
echo "=== 5. Health Checks ==="
for DEPLOY in bankchurn-predictor carvision-intelligence nlpinsight-analyzer; do
  echo "--- ${DEPLOY} ---"
  kubectl exec -n ml-portfolio deployment/${DEPLOY} -- curl -s http://localhost:8000/health 2>/dev/null || echo "FAILED"
  echo ""
done

echo ""
echo "=== 6. Artifact Registry Images ==="
gcloud artifacts docker images list "${AR_REPO}" \
  --format="table(package,tags,createTime)" \
  --project="${PROJECT_ID}" 2>&1

echo ""
echo "=== 7. GCS Models ==="
MODELS_BUCKET="${PROJECT_ID}-ml-models-production"
gsutil ls -r "gs://${MODELS_BUCKET}/" 2>&1 || echo "Bucket not accessible"

echo ""
echo "=== 8. Terraform Outputs ==="
if [ -d "infra/terraform/gcp" ]; then
  terraform -chdir=infra/terraform/gcp output 2>/dev/null || echo "Terraform state not available"
else
  echo "Terraform directory not found (run from repo root)"
fi

echo ""
echo "=== 9. Deployments Status ==="
kubectl get deployments -n ml-portfolio -o wide 2>&1

echo ""
echo "=== 10. Events (last 20) ==="
kubectl get events -n ml-portfolio --sort-by='.lastTimestamp' 2>&1 | tail -20

echo ""
echo "========================================="
echo "Evidence collection complete"
echo "========================================="
