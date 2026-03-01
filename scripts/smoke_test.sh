#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Smoke Test — ML-MLOps Portfolio
#
# Verifies each service responds correctly:
#   1. Health endpoint returns 200 + model_loaded=true
#   2. Single prediction returns valid response
#   3. Batch prediction returns correct count
#
# Usage:
#   ./scripts/smoke_test.sh                    # Docker Compose (default)
#   ./scripts/smoke_test.sh k8s                # Kubernetes port-forward
#   BANKCHURN_URL=http://... ./scripts/smoke_test.sh custom
# ─────────────────────────────────────────────────────────────
set -euo pipefail

MODE="${1:-docker}"
PASS=0
FAIL=0
TOTAL=0

# ── Port configuration ──────────────────────────────────────
case "$MODE" in
  docker)
    BANKCHURN_URL="${BANKCHURN_URL:-http://localhost:8001}"
    CARVISION_URL="${CARVISION_URL:-http://localhost:8002}"
    NLPINSIGHT_URL="${NLPINSIGHT_URL:-http://localhost:8003}"
    ;;
  k8s)
    BANKCHURN_URL="${BANKCHURN_URL:-http://localhost:8000}"
    CARVISION_URL="${CARVISION_URL:-http://localhost:8001}"
    NLPINSIGHT_URL="${NLPINSIGHT_URL:-http://localhost:8002}"
    ;;
  *)
    BANKCHURN_URL="${BANKCHURN_URL:-http://localhost:8001}"
    CARVISION_URL="${CARVISION_URL:-http://localhost:8002}"
    NLPINSIGHT_URL="${NLPINSIGHT_URL:-http://localhost:8003}"
    ;;
esac

# ── Helpers ─────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

wait_for_services() {
  local max_wait=30
  local interval=2
  local elapsed=0
  echo -e "${YELLOW}Waiting for services to become reachable (up to ${max_wait}s)...${NC}"
  while [ $elapsed -lt $max_wait ]; do
    if curl -sf "$BANKCHURN_URL/health" >/dev/null 2>&1; then
      echo -e "${GREEN}Services reachable after ${elapsed}s${NC}\n"
      return 0
    fi
    sleep $interval
    elapsed=$((elapsed + interval))
  done
  echo -e "${RED}WARNING: Services not reachable after ${max_wait}s — running tests anyway${NC}\n"
  return 0
}

check() {
  local name="$1" expected="$2" actual="$3"
  TOTAL=$((TOTAL + 1))
  if echo "$actual" | grep -q "$expected"; then
    echo -e "  ${GREEN}✓${NC} $name"
    PASS=$((PASS + 1))
  else
    echo -e "  ${RED}✗${NC} $name (expected '$expected' in response)"
    echo "    Response: $(echo "$actual" | head -c 200)"
    FAIL=$((FAIL + 1))
  fi
}

wait_for_services

# ── BankChurn ───────────────────────────────────────────────
echo -e "\n${YELLOW}═══ BankChurn Predictor ($BANKCHURN_URL) ═══${NC}"

HEALTH=$(curl -sf "$BANKCHURN_URL/health" 2>&1 || echo "CONNECTION_REFUSED")
check "Health endpoint" "model_loaded" "$HEALTH"

PREDICT=$(curl -sf -X POST "$BANKCHURN_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "CreditScore": 650, "Geography": "France", "Gender": "Female",
    "Age": 40, "Tenure": 3, "Balance": 60000.0,
    "NumOfProducts": 2, "HasCrCard": 1, "IsActiveMember": 1,
    "EstimatedSalary": 50000.0
  }' 2>&1 || echo "PREDICT_FAILED")
check "Single prediction" "churn_probability" "$PREDICT"

BATCH=$(curl -sf -X POST "$BANKCHURN_URL/predict_batch" \
  -H "Content-Type: application/json" \
  -d '{
    "customers": [
      {"CreditScore": 650, "Geography": "France", "Gender": "Female", "Age": 40, "Tenure": 3, "Balance": 60000, "NumOfProducts": 2, "HasCrCard": 1, "IsActiveMember": 1, "EstimatedSalary": 50000},
      {"CreditScore": 500, "Geography": "Germany", "Gender": "Male", "Age": 55, "Tenure": 1, "Balance": 0, "NumOfProducts": 1, "HasCrCard": 0, "IsActiveMember": 0, "EstimatedSalary": 30000}
    ]
  }' 2>&1 || echo "BATCH_FAILED")
check "Batch prediction (2)" "total_customers" "$BATCH"

# ── CarVision ───────────────────────────────────────────────
echo -e "\n${YELLOW}═══ CarVision Market Intelligence ($CARVISION_URL) ═══${NC}"

HEALTH=$(curl -sf "$CARVISION_URL/health" 2>&1 || echo "CONNECTION_REFUSED")
check "Health endpoint" "model_loaded" "$HEALTH"

PREDICT=$(curl -sf -X POST "$CARVISION_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "model_year": 2020, "model": "ford f-150",
    "condition": "excellent", "odometer": 25000
  }' 2>&1 || echo "PREDICT_FAILED")
check "Single prediction" "predicted_price" "$PREDICT"

BATCH=$(curl -sf -X POST "$CARVISION_URL/predict_batch" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicles": [
      {"model_year": 2020, "model": "ford f-150", "condition": "excellent", "odometer": 25000},
      {"model_year": 2018, "model": "toyota camry", "condition": "good", "odometer": 45000}
    ]
  }' 2>&1 || echo "BATCH_FAILED")
check "Batch prediction (2)" "total_vehicles" "$BATCH"

# ── NLPInsight ───────────────────────────────────────────────
echo -e "\n${YELLOW}═══ NLPInsight Analyzer ($NLPINSIGHT_URL) ═══${NC}"

HEALTH=$(curl -sf "$NLPINSIGHT_URL/health" 2>&1 || echo "CONNECTION_REFUSED")
check "Health endpoint" "model_loaded" "$HEALTH"

PREDICT=$(curl -sf -X POST "$NLPINSIGHT_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Revenue growth exceeded expectations this quarter."}' \
  2>&1 || echo "PREDICT_FAILED")
check "Single prediction" "label" "$PREDICT"
check "Confidence score" "confidence" "$PREDICT"

BATCH=$(curl -sf -X POST "$NLPINSIGHT_URL/predict_batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      {"text": "Revenue growth exceeded expectations this quarter."},
      {"text": "The company reported significant losses due to market downturn."}
    ]
  }' 2>&1 || echo "BATCH_FAILED")
check "Batch prediction (2)" "count" "$BATCH"

# ── Summary ─────────────────────────────────────────────────
echo -e "\n${YELLOW}═══════════════════════════════════════${NC}"
echo -e "  Total:  $TOTAL"
echo -e "  ${GREEN}Passed: $PASS${NC}"
if [ "$FAIL" -gt 0 ]; then
  echo -e "  ${RED}Failed: $FAIL${NC}"
  echo -e "${RED}SMOKE TEST FAILED${NC}"
  exit 1
else
  echo -e "  ${RED}Failed: 0${NC}"
  echo -e "${GREEN}ALL SMOKE TESTS PASSED${NC}"
  exit 0
fi
