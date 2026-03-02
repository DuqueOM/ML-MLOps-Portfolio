#!/bin/bash
# ─────────────────────────────────────────────────────────────
# Demo Integration Tests — Docker Compose (Wrapper)
#
# DEPRECATED: This script delegates to canonical pytest tests.
# Prefer running directly:
#   pytest tests/integration/test_demo.py -v
#
# This wrapper is kept for backward compatibility.
# ─────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "════════════════════════════════════════════════════════════"
echo "  ML-MLOps Portfolio — Docker Compose Integration Tests"
echo "════════════════════════════════════════════════════════════"

cd "$ROOT_DIR"
python -m pytest tests/integration/test_demo.py -v --tb=short "$@" || {
    echo ""
    echo "⚠️  Tests failed or pytest not available."
    echo "   Install: pip install pytest requests"
    echo "   Or run directly: pytest tests/integration/test_demo.py -v"
    exit 1
}

echo ""
echo "✅ Demo integration tests completed."
