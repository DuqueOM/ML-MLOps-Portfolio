#!/usr/bin/env bash
# Run CI checks for all projects in the portfolio
# Usage: ./run_all_checks.sh

set -euo pipefail

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$REPO_ROOT/check_results"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Running CI Checks for All Projects${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Create results directory
mkdir -p "$RESULTS_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SUMMARY_FILE="$RESULTS_DIR/summary_${TIMESTAMP}.txt"

# List of projects
PROJECTS=(
    "BankChurn-Predictor"
    "CarVision-Market-Intelligence"
    "Chicago-Mobility-Analytics"
    "Gaming-Market-Intelligence"
    "GoldRecovery-Process-Optimizer"
    "OilWell-Location-Optimizer"
    "TelecomAI-Customer-Intelligence"
)

# Arrays to track results
declare -a PASSED_PROJECTS
declare -a FAILED_PROJECTS

# Run checks for each project
for project in "${PROJECTS[@]}"; do
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Checking: $project${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    
    if "$REPO_ROOT/ci_checks.sh" "$project"; then
        PASSED_PROJECTS+=("$project")
        echo -e "${GREEN}✓ $project: PASSED${NC}\n"
    else
        FAILED_PROJECTS+=("$project")
        echo -e "${RED}✗ $project: FAILED${NC}\n"
    fi
done

# Generate summary
{
    echo "CI Checks Summary - $(date)"
    echo "======================================"
    echo ""
    echo "Passed Projects (${#PASSED_PROJECTS[@]}):"
    for project in "${PASSED_PROJECTS[@]}"; do
        echo "  ✓ $project"
    done
    echo ""
    echo "Failed Projects (${#FAILED_PROJECTS[@]}):"
    for project in "${FAILED_PROJECTS[@]}"; do
        echo "  ✗ $project"
    done
    echo ""
    echo "Success Rate: $(awk "BEGIN {printf \"%.1f\", (${#PASSED_PROJECTS[@]}/${#PROJECTS[@]})*100}")%"
} | tee "$SUMMARY_FILE"

echo ""
echo "Summary saved to: $SUMMARY_FILE"
echo "Individual reports in: $RESULTS_DIR"

# Exit with failure if any project failed
if [ ${#FAILED_PROJECTS[@]} -eq 0 ]; then
    echo -e "${GREEN}All projects passed!${NC}"
    exit 0
else
    echo -e "${RED}Some projects failed. Review individual reports.${NC}"
    exit 1
fi
