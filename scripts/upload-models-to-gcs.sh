#!/usr/bin/env bash
# Upload trained models to GCS bucket for Init Container downloads.
#
# Prerequisites:
#   - gcloud CLI authenticated (gcloud auth login)
#   - gsutil available
#
# Usage:
#   ./scripts/upload-models-to-gcs.sh                    # Upload all 3 models
#   ./scripts/upload-models-to-gcs.sh bankchurn           # Upload only bankchurn
#   ./scripts/upload-models-to-gcs.sh carvision           # Upload only carvision
#   ./scripts/upload-models-to-gcs.sh nlpinsight           # Upload only nlpinsight
#
# After uploading, restart pods to pick up new models:
#   kubectl rollout restart deployment/bankchurn-predictor -n ml-portfolio
#   kubectl rollout restart deployment/carvision-intelligence -n ml-portfolio
#   kubectl rollout restart deployment/nlpinsight-analyzer -n ml-portfolio

set -euo pipefail

BUCKET="ml-portfolio-duque-om-202602-ml-models-production"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

upload_model() {
    local project="$1"
    local local_path="$2"
    local gcs_path="$3"

    if [ ! -e "$local_path" ]; then
        echo "ERROR: Model not found: $local_path"
        echo "  Train first, then re-run this script."
        return 1
    fi

    local size_mb
    size_mb=$(du -sm "$local_path" | cut -f1)
    echo "Uploading $project model ($size_mb MB)..."
    echo "  Local:  $local_path"
    echo "  Remote: gs://$BUCKET/$gcs_path"

    if [ -d "$local_path" ]; then
        gsutil -m cp -r "$local_path/*" "gs://$BUCKET/$gcs_path/"
    else
        gsutil cp "$local_path" "gs://$BUCKET/$gcs_path"
    fi
    echo "  ✅ $project uploaded successfully"
    echo ""
}

TARGET="${1:-all}"

echo "=== ML Portfolio — Upload Models to GCS ==="
echo "Bucket: gs://$BUCKET"
echo ""

case "$TARGET" in
    bankchurn|all)
        upload_model "BankChurn" \
            "$PROJECT_ROOT/BankChurn-Predictor/models/model.joblib" \
            "bankchurn/model.joblib"
        ;;&
    carvision|all)
        upload_model "CarVision" \
            "$PROJECT_ROOT/CarVision-Market-Intelligence/models/model.joblib" \
            "carvision/model.joblib"
        ;;&
    nlpinsight|all)
        upload_model "NLPInsight" \
            "$PROJECT_ROOT/NLPInsight-Analyzer/models" \
            "nlpinsight/model"
        ;;&
    all) ;;
    bankchurn|carvision|nlpinsight) ;;
    *)
        echo "Usage: $0 [bankchurn|carvision|nlpinsight|all]"
        exit 1
        ;;
esac

echo "=== Done ==="
echo ""
echo "Next steps:"
echo "  1. Restart deployments to pick up new models:"
echo "     kubectl rollout restart deployment/bankchurn-predictor -n ml-portfolio"
echo "     kubectl rollout restart deployment/carvision-intelligence -n ml-portfolio"
echo "     kubectl rollout restart deployment/nlpinsight-analyzer -n ml-portfolio"
echo ""
echo "  2. Verify pods are running:"
echo "     kubectl get pods -n ml-portfolio -w"
