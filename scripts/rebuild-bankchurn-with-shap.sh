#!/bin/bash
# Rebuild BankChurn image with SHAP for production explainability
# Uses Cloud Build (no local Docker daemon needed)

set -e

PROJECT_ID="ml-portfolio-duque-om-202602"
REGION="us-central1"
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/ml-portfolio-images"
IMAGE_NAME="bankchurn-predictor"
TAG="v3.0.0"

echo "🔨 Building ${IMAGE_NAME}:${TAG} with SHAP via Cloud Build..."

gcloud builds submit BankChurn-Predictor/ \
  --tag="${REGISTRY}/${IMAGE_NAME}:${TAG}" \
  --project="${PROJECT_ID}" \
  --timeout=20m

echo "✅ Image built and pushed: ${REGISTRY}/${IMAGE_NAME}:${TAG}"
echo ""
echo "Next steps:"
echo "  1. Restart deployment: kubectl rollout restart deployment/bankchurn-predictor -n ml-portfolio"
echo "  2. Verify SHAP: curl -X POST http://136.111.152.72/bankchurn/predict?explain=true -H 'Content-Type: application/json' -d '{...}'"
