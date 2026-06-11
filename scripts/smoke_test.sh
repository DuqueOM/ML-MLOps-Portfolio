#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Smoke Test — ML-MLOps Portfolio (Wrapper)
#
# DEPRECATED: This script delegates to the canonical pytest tests.
# Prefer running pytest directly:
#   pytest tests/infra/smoke/test_smoke_services.py -v        # Docker Compose
#   pytest tests/integration/test_smoke_k8s.py -v             # Kubernetes
#
# This wrapper is kept for backward compatibility with existing
# documentation and CI scripts that reference scripts/smoke_test.sh
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

MODE="${1:-docker}"

echo "════════════════════════════════════════════════════════════"
echo "  ML-MLOps Portfolio — Smoke Tests"
echo "  Mode: $MODE"
echo "════════════════════════════════════════════════════════════"

case "$MODE" in
  k8s|kubernetes)
    echo "→ Delegating to: pytest tests/integration/test_smoke_k8s.py"
    cd "$ROOT_DIR"
    python -m pytest tests/integration/test_smoke_k8s.py -v --tb=short "$@" 2>/dev/null || {
      echo ""
      echo "⚠️  pytest not available or tests failed."
      echo "   Install: pip install pytest requests"
      echo "   Or run directly: pytest tests/integration/test_smoke_k8s.py -v"
      exit 1
    }
    ;;
  docker|compose|*)
    echo "→ Delegating to: pytest tests/infra/smoke/test_smoke_services.py"
    cd "$ROOT_DIR"
    python -m pytest tests/infra/smoke/test_smoke_services.py -v --tb=short 2>/dev/null || {
      echo ""
      echo "⚠️  pytest not available or tests failed."
      echo "   Install: pip install pytest requests"
      echo "   Or run directly: pytest tests/infra/smoke/test_smoke_services.py -v"
      exit 1
    }
    ;;
esac

echo ""
echo "✅ Smoke tests completed."
