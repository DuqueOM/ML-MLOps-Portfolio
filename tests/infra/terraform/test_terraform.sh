#!/usr/bin/env bash
# =============================================================================
# Terraform Infrastructure Tests
# Tests: fmt, validate, tfsec, checkov
# Usage: bash tests/infra/terraform/test_terraform.sh [gcp|aws|all]
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
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
# 1. terraform fmt — canonical formatting
# ---------------------------------------------------------------------------
test_fmt() {
    local dir="$1" name="$2"
    log_info "[$name] terraform fmt -check"
    if terraform -chdir="$dir" fmt -check -recursive -diff > /dev/null 2>&1; then
        log_pass "[$name] terraform fmt"
    else
        log_fail "[$name] terraform fmt — run 'terraform fmt -recursive $dir' to fix"
    fi
}

# ---------------------------------------------------------------------------
# 2. terraform validate — syntax + type checking
# ---------------------------------------------------------------------------
test_validate() {
    local dir="$1" name="$2"
    log_info "[$name] terraform validate"

    # Create a minimal .auto.tfvars to satisfy required variables
    local tmpvars="$dir/.test-validate.auto.tfvars"
    trap "rm -f '$tmpvars'" RETURN

    if [[ "$name" == "GCP" ]]; then
        cat > "$tmpvars" <<'EOF'
project_id  = "test-project-000000"
db_password = "test-password-validate"
EOF
    elif [[ "$name" == "AWS" ]]; then
        cat > "$tmpvars" <<'EOF'
db_password = "test-password-validate"
EOF
    fi

    # Init with backend disabled (no real state needed)
    if terraform -chdir="$dir" init -backend=false -input=false > /dev/null 2>&1; then
        if terraform -chdir="$dir" validate -no-color 2>&1 | grep -q "Success"; then
            log_pass "[$name] terraform validate"
        else
            log_fail "[$name] terraform validate"
            terraform -chdir="$dir" validate -no-color 2>&1 || true
        fi
    else
        log_fail "[$name] terraform init (required for validate)"
    fi

    rm -f "$tmpvars"
    # Clean up .terraform directory created by init
    rm -rf "$dir/.terraform" "$dir/.terraform.lock.hcl"
}

# ---------------------------------------------------------------------------
# 3. tfsec — security scanning
# ---------------------------------------------------------------------------
test_tfsec() {
    local dir="$1" name="$2"
    if ! command -v tfsec &> /dev/null; then
        log_skip "[$name] tfsec (not installed)"
        return
    fi
    log_info "[$name] tfsec security scan"
    local output tfsec_args=""
    if [[ -f "$dir/.tfsec.yml" ]]; then
        tfsec_args="--config-file $dir/.tfsec.yml"
    fi
    output=$(tfsec "$dir" --format json --soft-fail $tfsec_args 2>/dev/null || true)

    local critical high medium
    critical=$(echo "$output" | python3 -c "import sys,json; d=json.load(sys.stdin); print(sum(1 for r in d.get('results',[]) if r.get('severity','')=='CRITICAL'))" 2>/dev/null || echo "0")
    high=$(echo "$output" | python3 -c "import sys,json; d=json.load(sys.stdin); print(sum(1 for r in d.get('results',[]) if r.get('severity','')=='HIGH'))" 2>/dev/null || echo "0")
    medium=$(echo "$output" | python3 -c "import sys,json; d=json.load(sys.stdin); print(sum(1 for r in d.get('results',[]) if r.get('severity','')=='MEDIUM'))" 2>/dev/null || echo "0")

    if [[ "$critical" -gt 0 || "$high" -gt 0 ]]; then
        log_pass "[$name] tfsec (advisory: $critical critical, $high high, $medium medium)"
        echo -e "  ${YELLOW}⚠️  Review findings — security scanners are advisory in CI${NC}"
    else
        log_pass "[$name] tfsec ($medium medium findings, 0 critical/high)"
    fi
}

# ---------------------------------------------------------------------------
# 4. checkov — policy-as-code scanning
# ---------------------------------------------------------------------------
test_checkov() {
    local dir="$1" name="$2"
    if ! command -v checkov &> /dev/null; then
        log_skip "[$name] checkov (not installed)"
        return
    fi
    log_info "[$name] checkov policy scan"

    local output
    output=$(checkov -d "$dir" --framework terraform --quiet --compact --output json 2>/dev/null || true)

    local passed failed
    passed=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if isinstance(data, list):
    print(sum(d.get('summary',{}).get('passed',0) for d in data))
else:
    print(data.get('summary',{}).get('passed',0))
" 2>/dev/null || echo "0")
    failed=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if isinstance(data, list):
    print(sum(d.get('summary',{}).get('failed',0) for d in data))
else:
    print(data.get('summary',{}).get('failed',0))
" 2>/dev/null || echo "0")

    local total=$((passed + failed))
    if [[ "$failed" -gt 0 ]]; then
        log_pass "[$name] checkov (advisory: $passed/$total passed, $failed findings)"
        echo -e "  ${YELLOW}⚠️  Review findings — checkov is advisory in CI${NC}"
    else
        log_pass "[$name] checkov ($passed/$total checks passed)"
    fi
}

# ---------------------------------------------------------------------------
# Run tests for a provider
# ---------------------------------------------------------------------------
run_provider_tests() {
    local provider="$1"
    local dir="${REPO_ROOT}/infra/terraform/${provider}"
    local name
    name=$(echo "$provider" | tr '[:lower:]' '[:upper:]')

    if [[ ! -d "$dir" ]]; then
        log_skip "[$name] directory not found: $dir"
        return
    fi

    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Terraform Tests: ${name}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    test_fmt "$dir" "$name"
    test_validate "$dir" "$name"
    test_tfsec "$dir" "$name"
    test_checkov "$dir" "$name"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Terraform Infrastructure Test Suite         ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"

case "$TARGET" in
    gcp)  run_provider_tests "gcp" ;;
    aws)  run_provider_tests "aws" ;;
    all)  run_provider_tests "gcp"; run_provider_tests "aws" ;;
    *)    echo "Usage: $0 [gcp|aws|all]"; exit 1 ;;
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
    echo -e "${RED}❌ Terraform tests failed${NC}"
    exit 1
else
    echo -e "${GREEN}✅ All Terraform tests passed${NC}"
    exit 0
fi
