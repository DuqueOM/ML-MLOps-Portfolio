#!/usr/bin/env bash
# Create GCP service account and permissions for Vertex AI endpoint deployment.
#
# Usage:
#   export GCP_PROJECT=ml-portfolio-duque-om-202602
#   bash scripts/vertex_ai/setup-service-account.sh
#
# This creates:
#   - Service account: vertex-ai-deployer@<project>.iam.gserviceaccount.com
#   - Roles: Vertex AI User, Storage Object Viewer, AI Platform Admin

set -euo pipefail

PROJECT="${GCP_PROJECT:-ml-portfolio-duque-om-202602}"
SA_NAME="vertex-ai-deployer"
SA_EMAIL="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"

echo "🔧 Creating Vertex AI service account: ${SA_EMAIL}"

# Check if SA already exists
if gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT}" &>/dev/null; then
    echo "✅ Service account ${SA_EMAIL} already exists."
else
    gcloud iam service-accounts create "${SA_NAME}" \
        --project="${PROJECT}" \
        --display-name="Vertex AI Deployer for ML Portfolio" \
        --description="Service account for deploying ML models to Vertex AI endpoints"
    echo "✅ Service account created: ${SA_EMAIL}"
fi

echo "📎 Granting IAM roles..."

# Vertex AI User — deploy models, create endpoints
gcloud projects add-iam-policy-binding "${PROJECT}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/aiplatform.user" \
    --quiet

# Storage Object Viewer — read model artifacts from GCS
gcloud projects add-iam-policy-binding "${PROJECT}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.objectViewer" \
    --quiet

# AI Platform Admin — manage models and endpoints
gcloud projects add-iam-policy-binding "${PROJECT}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/aiplatform.admin" \
    --quiet

echo ""
echo "✅ Service account configured!"
echo "   Email: ${SA_EMAIL}"
echo "   Roles: aiplatform.user, storage.objectViewer, aiplatform.admin"
echo ""
echo "💡 For local development, use Application Default Credentials:"
echo "   gcloud auth application-default login"
echo ""
echo "💡 For CI/CD, create a key:"
echo "   gcloud iam service-accounts keys create vertex-ai-key.json \\"
echo "     --iam-account=${SA_EMAIL}"
echo "   export GOOGLE_APPLICATION_CREDENTIALS=vertex-ai-key.json"
