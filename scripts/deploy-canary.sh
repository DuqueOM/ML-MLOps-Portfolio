#!/usr/bin/env bash
# deploy-canary.sh — Canary deployment using Argo Rollouts
#
# Deploys a new model version via progressive canary rollout with
# Prometheus-based automated analysis. Auto-rollback on error rate >5%
# or p95 latency >500ms.
#
# Prerequisites:
#   - kubectl configured for target cluster (GKE or EKS)
#   - Argo Rollouts controller installed
#   - Prometheus running in ml-portfolio namespace
#   - New Docker image already pushed to registry
#
# Usage:
#   ./scripts/deploy-canary.sh bankchurn v3.2.0
#   ./scripts/deploy-canary.sh nlpinsight v3.2.0
#   ./scripts/deploy-canary.sh chicagotaxi v1.0.0
#   ./scripts/deploy-canary.sh all v3.2.0
#
# Monitoring:
#   kubectl argo rollouts get rollout <name> -n ml-portfolio --watch

set -euo pipefail

# --- Configuration ---
NAMESPACE="ml-portfolio"
REGISTRY="us-central1-docker.pkg.dev/ml-portfolio-duque-om-202602/ml-portfolio-images"
ROLLOUTS_DIR="k8s/argo-rollouts"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*" >&2; }
ok()   { echo -e "${GREEN}[OK]${NC}    $*"; }

# --- Validation ---
check_prerequisites() {
    log "Checking prerequisites..."

    if ! command -v kubectl &>/dev/null; then
        err "kubectl not found. Install: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi

    if ! kubectl get ns "$NAMESPACE" &>/dev/null; then
        err "Namespace '$NAMESPACE' not found. Is kubectl configured for the right cluster?"
        exit 1
    fi

    # Check Argo Rollouts CRD
    if ! kubectl get crd rollouts.argoproj.io &>/dev/null; then
        warn "Argo Rollouts CRD not found. Installing..."
        kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
        kubectl wait --for=condition=available deployment/argo-rollouts -n argo-rollouts --timeout=120s
        ok "Argo Rollouts installed"
    else
        ok "Argo Rollouts CRD found"
    fi

    # Check Argo Rollouts kubectl plugin
    if ! kubectl argo rollouts version &>/dev/null 2>&1; then
        warn "Argo Rollouts kubectl plugin not found."
        warn "Install: curl -LO https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-linux-amd64"
        warn "Continuing without plugin (rollout status via kubectl only)..."
    fi

    # Check Prometheus
    if kubectl get svc prometheus-service -n "$NAMESPACE" &>/dev/null; then
        ok "Prometheus service found"
    else
        warn "Prometheus not found — analysis templates will fail. Deploy Prometheus first."
    fi

    ok "Prerequisites check passed"
}

# --- Image Update ---
update_image() {
    local service="$1"
    local version="$2"
    local image

    case "$service" in
        bankchurn)
            image="${REGISTRY}/bankchurn-predictor:${version}"
            ;;
        nlpinsight)
            image="${REGISTRY}/nlpinsight-analyzer:${version}"
            ;;
        chicagotaxi)
            image="${REGISTRY}/chicagotaxi-pipeline:${version}"
            ;;
        *)
            err "Unknown service: $service"
            exit 1
            ;;
    esac

    log "Image: $image"
    echo "$image"
}

# --- Deploy ---
deploy_canary() {
    local service="$1"
    local version="$2"

    log "=== Deploying $service canary (version $version) ==="

    # Step 1: Apply analysis templates (shared)
    log "Applying analysis templates..."
    kubectl apply -f "${ROLLOUTS_DIR}/analysis-templates.yaml" -n "$NAMESPACE"

    # Step 2: Get the rollout manifest
    local rollout_file="${ROLLOUTS_DIR}/${service}-rollout.yaml"
    if [ "$service" = "bankchurn" ]; then
        rollout_file="${ROLLOUTS_DIR}/bankchurn-rollout.yaml"
    elif [ "$service" = "nlpinsight" ]; then
        rollout_file="${ROLLOUTS_DIR}/nlpinsight-rollout.yaml"
    fi

    if [ ! -f "$rollout_file" ]; then
        err "Rollout manifest not found: $rollout_file"
        exit 1
    fi

    # Step 3: Apply the Rollout (replaces Deployment)
    log "Applying rollout manifest: $rollout_file"
    kubectl apply -f "$rollout_file" -n "$NAMESPACE"

    # Step 4: Update image to trigger canary
    local image
    image=$(update_image "$service" "$version")
    local rollout_name
    case "$service" in
        bankchurn)  rollout_name="bankchurn-predictor" ;;
        nlpinsight) rollout_name="nlpinsight-analyzer" ;;
        chicagotaxi) rollout_name="chicagotaxi-pipeline" ;;
    esac

    log "Setting image to trigger canary rollout..."
    kubectl argo rollouts set image "$rollout_name" \
        "${service}-api=${image}" \
        -n "$NAMESPACE" 2>/dev/null || \
    kubectl set image "rollout/${rollout_name}" \
        "${service}-api=${image}" \
        -n "$NAMESPACE"

    ok "Canary rollout triggered for $service"

    # Step 5: Monitor
    log "Monitoring rollout progress..."
    log "Run: kubectl argo rollouts get rollout $rollout_name -n $NAMESPACE --watch"

    if kubectl argo rollouts version &>/dev/null 2>&1; then
        kubectl argo rollouts get rollout "$rollout_name" -n "$NAMESPACE" || true
    else
        kubectl get rollout "$rollout_name" -n "$NAMESPACE" -o wide || true
    fi
}

# --- Rollback ---
rollback() {
    local service="$1"
    local rollout_name

    case "$service" in
        bankchurn)  rollout_name="bankchurn-predictor" ;;
        nlpinsight) rollout_name="nlpinsight-analyzer" ;;
        chicagotaxi) rollout_name="chicagotaxi-pipeline" ;;
        *)          err "Unknown service: $service"; exit 1 ;;
    esac

    warn "Rolling back $service..."
    kubectl argo rollouts undo "$rollout_name" -n "$NAMESPACE" 2>/dev/null || \
    kubectl rollout undo "rollout/${rollout_name}" -n "$NAMESPACE"
    ok "Rollback triggered for $service"
}

# --- Promote ---
promote() {
    local service="$1"
    local rollout_name

    case "$service" in
        bankchurn)  rollout_name="bankchurn-predictor" ;;
        nlpinsight) rollout_name="nlpinsight-analyzer" ;;
        chicagotaxi) rollout_name="chicagotaxi-pipeline" ;;
        *)          err "Unknown service: $service"; exit 1 ;;
    esac

    log "Promoting $service to full traffic..."
    kubectl argo rollouts promote "$rollout_name" -n "$NAMESPACE"
    ok "Promotion triggered for $service"
}

# --- Status ---
status() {
    local service="$1"
    local rollout_name

    case "$service" in
        bankchurn)  rollout_name="bankchurn-predictor" ;;
        nlpinsight) rollout_name="nlpinsight-analyzer" ;;
        chicagotaxi) rollout_name="chicagotaxi-pipeline" ;;
        *)          err "Unknown service: $service"; exit 1 ;;
    esac

    kubectl argo rollouts get rollout "$rollout_name" -n "$NAMESPACE"
}

# --- Main ---
usage() {
    echo "Usage: $0 <service|all> <version> [--rollback|--promote|--status]"
    echo ""
    echo "Services: bankchurn, nlpinsight, chicagotaxi, all"
    echo ""
    echo "Examples:"
    echo "  $0 bankchurn v3.2.0           # Start canary deployment"
    echo "  $0 bankchurn --status          # Check rollout status"
    echo "  $0 bankchurn --promote         # Force promote to 100%"
    echo "  $0 bankchurn --rollback        # Force rollback"
    echo "  $0 all v3.2.0                  # Deploy all services"
    exit 1
}

main() {
    if [ $# -lt 2 ]; then
        usage
    fi

    local service="$1"
    local action="$2"

    check_prerequisites

    local services=()
    if [ "$service" = "all" ]; then
        services=(bankchurn nlpinsight chicagotaxi)
    else
        services=("$service")
    fi

    for svc in "${services[@]}"; do
        case "$action" in
            --rollback) rollback "$svc" ;;
            --promote)  promote "$svc" ;;
            --status)   status "$svc" ;;
            *)          deploy_canary "$svc" "$action" ;;
        esac
    done

    echo ""
    ok "Done. Monitor with: kubectl argo rollouts dashboard"
}

main "$@"
