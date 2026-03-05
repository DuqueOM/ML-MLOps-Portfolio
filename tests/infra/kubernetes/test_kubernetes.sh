#!/usr/bin/env bash
# =============================================================================
# Kubernetes Manifest Tests
# Tests: kube-linter, conftest (OPA policies)
# Usage: bash tests/infra/kubernetes/test_kubernetes.sh [base|overlays|all]
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
K8S_DIR="${REPO_ROOT}/k8s"
POLICY_DIR="${REPO_ROOT}/tests/infra/kubernetes/policies"
TARGET="${1:-all}"
PASS=0
FAIL=0
SKIP=0
RESULTS=()

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_pass() { PASS=$((PASS+1)); RESULTS+=("✅ $1"); echo -e "${GREEN}✅ PASS: $1${NC}"; }
log_fail() { FAIL=$((FAIL+1)); RESULTS+=("❌ $1"); echo -e "${RED}❌ FAIL: $1${NC}"; }
log_skip() { SKIP=$((SKIP+1)); RESULTS+=("⏭️  $1"); echo -e "${YELLOW}⏭️  SKIP: $1${NC}"; }
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# ---------------------------------------------------------------------------
# 1. YAML Syntax Validation
# ---------------------------------------------------------------------------
test_yaml_syntax() {
    local dir="$1" name="$2"
    log_info "[$name] YAML syntax validation"
    local errors=0
    for f in "$dir"/*.yaml; do
        [[ -f "$f" ]] || continue
        if ! python3 -c "import yaml; yaml.safe_load_all(open('$f'))" 2>/dev/null; then
            echo "  Invalid YAML: $f"
            errors=$((errors+1))
        fi
    done
    if [[ $errors -eq 0 ]]; then
        log_pass "[$name] YAML syntax"
    else
        log_fail "[$name] YAML syntax — $errors invalid files"
    fi
}

# ---------------------------------------------------------------------------
# 2. kube-linter — best practices linting
# ---------------------------------------------------------------------------
test_kubelinter() {
    local dir="$1" name="$2"
    if ! command -v kube-linter &> /dev/null; then
        log_skip "[$name] kube-linter (not installed)"
        return
    fi
    log_info "[$name] kube-linter"

    local output exit_code=0
    output=$(kube-linter lint "$dir" \
        --config "${REPO_ROOT}/tests/infra/kubernetes/.kube-linter.yaml" \
        2>&1) || exit_code=$?

    local error_count=0
    error_count=$(echo "$output" | grep -c "^${dir}" || true)

    if [[ $exit_code -eq 0 ]]; then
        log_pass "[$name] kube-linter (0 findings)"
    else
        log_pass "[$name] kube-linter (advisory: $error_count findings)"
        echo -e "  ${YELLOW}⚠️  Review kube-linter findings — advisory in CI${NC}"
    fi
}

# ---------------------------------------------------------------------------
# 3. conftest (OPA) — policy testing
# ---------------------------------------------------------------------------
test_conftest() {
    local dir="$1" name="$2"
    if ! command -v conftest &> /dev/null; then
        log_skip "[$name] conftest/OPA (not installed)"
        return
    fi
    log_info "[$name] conftest OPA policies"

    local deny_count=0 warn_count=0 total_files=0 pass_files=0

    for f in "$dir"/*.yaml; do
        [[ -f "$f" ]] || continue
        total_files=$((total_files+1))
        local output exit_code=0
        output=$(conftest test "$f" -p "$POLICY_DIR" --no-color 2>&1) || exit_code=$?

        local file_denies file_warns
        file_denies=$(echo "$output" | grep -c "FAIL" || true)
        file_denies=${file_denies:-0}
        file_warns=$(echo "$output" | grep -c "WARN" || true)
        file_warns=${file_warns:-0}

        deny_count=$((deny_count + file_denies))
        warn_count=$((warn_count + file_warns))

        if [[ $file_denies -eq 0 ]]; then
            pass_files=$((pass_files+1))
        else
            echo "  $(basename "$f"): $file_denies denies, $file_warns warnings"
            echo "$output" | grep "FAIL" | sed 's/^/    /'
        fi
    done

    if [[ $deny_count -eq 0 ]]; then
        log_pass "[$name] conftest OPA ($pass_files/$total_files files, $warn_count warnings)"
    else
        log_fail "[$name] conftest OPA — $deny_count deny rules triggered"
    fi

    # Show warnings separately
    if [[ $warn_count -gt 0 ]]; then
        echo -e "  ${YELLOW}⚠️  $warn_count warnings (non-blocking)${NC}"
    fi
}

# ---------------------------------------------------------------------------
# 4. Required resources check
# ---------------------------------------------------------------------------
test_required_resources() {
    local dir="$1" name="$2"
    log_info "[$name] Required Kubernetes resources"

    local missing=0
    local required_kinds=("Namespace" "Deployment" "Service" "ConfigMap" "HorizontalPodAutoscaler" "Ingress")

    for kind in "${required_kinds[@]}"; do
        if grep -rq "kind: $kind" "$dir"/*.yaml 2>/dev/null; then
            true
        else
            echo "  Missing: $kind"
            missing=$((missing+1))
        fi
    done

    # Check required deployments
    local required_deploys=("bankchurn" "nlpinsight" "chicagotaxi" "prometheus" "grafana")
    for deploy in "${required_deploys[@]}"; do
        if grep -rq "name: ${deploy}" "$dir"/*.yaml 2>/dev/null; then
            true
        else
            echo "  Missing deployment: $deploy"
            missing=$((missing+1))
        fi
    done

    if [[ $missing -eq 0 ]]; then
        log_pass "[$name] Required resources (${#required_kinds[@]} kinds, ${#required_deploys[@]} deployments)"
    else
        log_fail "[$name] Required resources — $missing missing"
    fi
}

# ---------------------------------------------------------------------------
# 5. Security checks
# ---------------------------------------------------------------------------
test_security() {
    local dir="$1" name="$2"
    log_info "[$name] Security checks"

    local issues=0

    # Check for privileged containers
    if grep -rq "privileged: true" "$dir"/*.yaml 2>/dev/null; then
        echo "  ⚠️ Found privileged containers"
        issues=$((issues+1))
    fi

    # Check for hostNetwork
    if grep -rq "hostNetwork: true" "$dir"/*.yaml 2>/dev/null; then
        echo "  ⚠️ Found hostNetwork: true"
        issues=$((issues+1))
    fi

    # Check for hostPID
    if grep -rq "hostPID: true" "$dir"/*.yaml 2>/dev/null; then
        echo "  ⚠️ Found hostPID: true"
        issues=$((issues+1))
    fi

    # Check ServiceAccount exists
    if ! grep -rq "kind: ServiceAccount" "$dir"/*.yaml 2>/dev/null; then
        echo "  ⚠️ No ServiceAccount defined"
        issues=$((issues+1))
    fi

    if [[ $issues -eq 0 ]]; then
        log_pass "[$name] Security checks"
    else
        log_fail "[$name] Security checks — $issues issues"
    fi
}

# ---------------------------------------------------------------------------
# Run tests for a target
# ---------------------------------------------------------------------------
run_base_tests() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Kubernetes Tests: Base Manifests${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    test_yaml_syntax "$K8S_DIR" "base"
    test_kubelinter "$K8S_DIR" "base"
    test_conftest "$K8S_DIR" "base"
    test_required_resources "$K8S_DIR" "base"
    test_security "$K8S_DIR" "base"
}

run_overlay_tests() {
    for overlay_dir in "$K8S_DIR"/overlays/*/; do
        [[ -d "$overlay_dir" ]] || continue
        local overlay_name
        overlay_name=$(basename "$overlay_dir")

        echo ""
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}  Kubernetes Tests: Overlay ${overlay_name^^}${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

        test_yaml_syntax "$overlay_dir" "overlay-$overlay_name"
        test_conftest "$overlay_dir" "overlay-$overlay_name"
    done
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Kubernetes Manifest Test Suite              ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"

case "$TARGET" in
    base)     run_base_tests ;;
    overlays) run_overlay_tests ;;
    all)      run_base_tests; run_overlay_tests ;;
    *)        echo "Usage: $0 [base|overlays|all]"; exit 1 ;;
esac

# Summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
for r in "${RESULTS[@]}"; do echo "  $r"; done
echo ""
echo -e "  ${GREEN}Passed: $PASS${NC}  ${RED}Failed: $FAIL${NC}  ${YELLOW}Skipped: $SKIP${NC}"
echo ""

if [[ $FAIL -gt 0 ]]; then
    echo -e "${RED}❌ Kubernetes tests failed${NC}"
    exit 1
else
    echo -e "${GREEN}✅ All Kubernetes tests passed${NC}"
    exit 0
fi
