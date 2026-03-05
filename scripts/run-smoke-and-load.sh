#!/bin/bash
# ─────────────────────────────────────────────────────────────
# Smoke + Load Test — K8s Port-Forward (Wrapper)
#
# DEPRECATED: This script delegates to canonical pytest/locust tests.
# Prefer running directly:
#   pytest tests/integration/test_smoke_k8s.py -v     # Smoke
#   locust -f tests/load/locustfile.py --headless      # Load
#
# This wrapper is kept for backward compatibility.
# ─────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "════════════════════════════════════════════════════════════"
echo "  ML-MLOps Portfolio — K8s Smoke + Load Tests"
echo "════════════════════════════════════════════════════════════"

# Step 1: Set up port-forwards
echo ""
echo "=== Setting up port-forwards ==="
pkill -9 -f "kubectl port-forward" 2>/dev/null || true
sleep 1

kubectl port-forward svc/bankchurn-service 8000:80 -n ml-portfolio &
# Step 2: Smoke tests via pytest
echo ""
echo "=== Running Smoke Tests (pytest) ==="
cd "$ROOT_DIR"
python -m pytest tests/integration/test_smoke_k8s.py -v --tb=short || {
    echo "⚠️  Smoke tests failed. Cleaning up port-forwards..."
    pkill -9 -f "kubectl port-forward" 2>/dev/null || true
    exit 1
}

# Step 3: Load tests via Locust
echo ""
echo "=== Running Load Tests (Locust) ==="
if command -v locust &>/dev/null; then
    locust -f tests/load/locustfile.py \
        --headless \
        --users 10 \
        --spawn-rate 2 \
        --run-time 30s \
        --host http://localhost \
        --csv reports/load-test 2>&1 | tail -20
else
    echo "⚠️  Locust not installed. Install: pip install locust"
    echo "   Or run manually: locust -f tests/load/locustfile.py"
fi

# Cleanup
echo ""
echo "=== Cleaning up port-forwards ==="
pkill -9 -f "kubectl port-forward" 2>/dev/null || true

echo ""
echo "✅ Smoke + Load tests completed."
