#!/usr/bin/env bash
# =============================================================================
# Infrastructure Test Suite — Master Runner
# Runs all infrastructure tests: Terraform + Kubernetes + Smoke
# Usage: bash tests/infra/run_all_tests.sh [--skip-smoke]
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKIP_SMOKE=false

for arg in "$@"; do
    case "$arg" in
        --skip-smoke) SKIP_SMOKE=true ;;
    esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

TOTAL_PASS=0
TOTAL_FAIL=0

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   ML-MLOps-Portfolio — Infrastructure Test Suite     ║${NC}"
echo -e "${BLUE}║   Terraform · Kubernetes · Smoke Tests               ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# ---------------------------------------------------------------------------
# 1. Terraform Tests
# ---------------------------------------------------------------------------
echo -e "${BLUE}▶ Running Terraform tests...${NC}"
if bash "${REPO_ROOT}/tests/infra/terraform/test_terraform.sh" all; then
    TOTAL_PASS=$((TOTAL_PASS+1))
else
    TOTAL_FAIL=$((TOTAL_FAIL+1))
fi

# ---------------------------------------------------------------------------
# 2. Kubernetes Tests
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}▶ Running Kubernetes tests...${NC}"
if bash "${REPO_ROOT}/tests/infra/kubernetes/test_kubernetes.sh" all; then
    TOTAL_PASS=$((TOTAL_PASS+1))
else
    TOTAL_FAIL=$((TOTAL_FAIL+1))
fi

# ---------------------------------------------------------------------------
# 3. Smoke Tests (optional, requires running services)
# ---------------------------------------------------------------------------
if [[ "$SKIP_SMOKE" == "false" ]]; then
    echo ""
    echo -e "${BLUE}▶ Running API smoke tests...${NC}"
    if python3 -m pytest "${REPO_ROOT}/tests/infra/smoke/test_smoke_services.py" -v --tb=short 2>&1; then
        TOTAL_PASS=$((TOTAL_PASS+1))
    else
        TOTAL_FAIL=$((TOTAL_FAIL+1))
    fi
else
    echo ""
    echo -e "${BLUE}⏭️  Skipping smoke tests (--skip-smoke)${NC}"
fi

# ---------------------------------------------------------------------------
# Final Summary
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Final Summary                                      ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo -e "  Suites passed: ${GREEN}$TOTAL_PASS${NC}"
echo -e "  Suites failed: ${RED}$TOTAL_FAIL${NC}"
echo ""

if [[ $TOTAL_FAIL -gt 0 ]]; then
    echo -e "${RED}❌ Infrastructure tests failed${NC}"
    exit 1
else
    echo -e "${GREEN}✅ All infrastructure tests passed${NC}"
    exit 0
fi
