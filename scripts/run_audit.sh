#!/usr/bin/env bash
# run_audit.sh - Portfolio Audit Automation Script
# Runs comprehensive code quality, security, and test audits
#
# Usage:
#   ./scripts/run_audit.sh              # Run full audit
#   ./scripts/run_audit.sh --quick      # Run quick checks only (no tests)
#   ./scripts/run_audit.sh --project X  # Run audit for specific project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECTS=("BankChurn-Predictor" "CarVision-Market-Intelligence" "NLPInsight-Analyzer")
REPORTS_DIR="reports/audit"
SPANISH_REPORTS_DIR="Reportes Portafolio"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Parse arguments
QUICK_MODE=false
SPECIFIC_PROJECT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --project)
            SPECIFIC_PROJECT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Header
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         ML-MLOps Portfolio Audit Script                    ║${NC}"
echo -e "${BLUE}║         Timestamp: ${TIMESTAMP}                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

# Create reports directory
mkdir -p "$REPORTS_DIR"
mkdir -p "$SPANISH_REPORTS_DIR"

# Function to run command and capture output
run_check() {
    local name="$1"
    local cmd="$2"
    local output_file="$3"
    
    echo -e "\n${YELLOW}[Running] ${name}...${NC}"
    
    if eval "$cmd" > "$output_file" 2>&1; then
        echo -e "${GREEN}✅ ${name} completed${NC}"
        return 0
    else
        echo -e "${RED}⚠️  ${name} completed with warnings/errors${NC}"
        return 1
    fi
}

# Function to check if tool is installed
check_tool() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed${NC}"
        echo "Install with: pip install $1"
        return 1
    fi
    return 0
}

# Check required tools
echo -e "\n${BLUE}[1/7] Checking required tools...${NC}"
TOOLS=("black" "flake8" "mypy" "bandit" "radon" "pytest" "pip-audit")
MISSING_TOOLS=()

for tool in "${TOOLS[@]}"; do
    if ! check_tool "$tool"; then
        MISSING_TOOLS+=("$tool")
    fi
done

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo -e "${YELLOW}Installing missing tools: ${MISSING_TOOLS[*]}${NC}"
    pip install "${MISSING_TOOLS[@]}" --quiet
fi

echo -e "${GREEN}✅ All tools available${NC}"

# Select projects to audit
if [ -n "$SPECIFIC_PROJECT" ]; then
    PROJECTS=("$SPECIFIC_PROJECT")
fi

# Initialize summary
SUMMARY_FILE="$REPORTS_DIR/audit_summary_${TIMESTAMP}.txt"
echo "ML-MLOps Portfolio Audit Summary" > "$SUMMARY_FILE"
echo "================================" >> "$SUMMARY_FILE"
echo "Timestamp: $TIMESTAMP" >> "$SUMMARY_FILE"
echo "Quick Mode: $QUICK_MODE" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

# ===== BLACK CHECK =====
echo -e "\n${BLUE}[2/7] Running Black formatter check...${NC}"

for project in "${PROJECTS[@]}"; do
    echo -e "  ${YELLOW}Checking ${project}...${NC}"
    if black --check "${project}/src" "${project}/app" 2>/dev/null; then
        echo -e "  ${GREEN}✅ ${project}: Black passing${NC}"
        echo "${project}: Black ✅" >> "$SUMMARY_FILE"
    else
        echo -e "  ${RED}⚠️  ${project}: Files need formatting${NC}"
        echo "${project}: Black ⚠️ (needs formatting)" >> "$SUMMARY_FILE"
    fi
done

# ===== FLAKE8 CHECK =====
echo -e "\n${BLUE}[3/7] Running Flake8 linter...${NC}"

for project in "${PROJECTS[@]}"; do
    OUTPUT_FILE="$REPORTS_DIR/flake8_${project}_${TIMESTAMP}.txt"
    echo -e "  ${YELLOW}Checking ${project}...${NC}"
    
    if flake8 "${project}/src" "${project}/app" --max-line-length=120 --statistics > "$OUTPUT_FILE" 2>&1; then
        echo -e "  ${GREEN}✅ ${project}: Flake8 passing${NC}"
        echo "${project}: Flake8 ✅" >> "$SUMMARY_FILE"
    else
        ERRORS=$(wc -l < "$OUTPUT_FILE")
        echo -e "  ${RED}⚠️  ${project}: ${ERRORS} issues found${NC}"
        echo "${project}: Flake8 ⚠️ (${ERRORS} issues)" >> "$SUMMARY_FILE"
    fi
done

# ===== MYPY CHECK =====
echo -e "\n${BLUE}[4/7] Running mypy type checker...${NC}"

for project in "${PROJECTS[@]}"; do
    OUTPUT_FILE="$REPORTS_DIR/mypy_${project}_${TIMESTAMP}.txt"
    echo -e "  ${YELLOW}Checking ${project}...${NC}"
    
    if mypy "${project}/src" --ignore-missing-imports > "$OUTPUT_FILE" 2>&1; then
        echo -e "  ${GREEN}✅ ${project}: mypy passing${NC}"
        echo "${project}: mypy ✅" >> "$SUMMARY_FILE"
    else
        ERRORS=$(grep -c "error:" "$OUTPUT_FILE" 2>/dev/null || echo "0")
        echo -e "  ${YELLOW}⚠️  ${project}: ${ERRORS} type errors${NC}"
        echo "${project}: mypy ⚠️ (${ERRORS} errors)" >> "$SUMMARY_FILE"
    fi
done

# ===== RADON COMPLEXITY =====
echo -e "\n${BLUE}[5/7] Running Radon complexity analysis...${NC}"

for project in "${PROJECTS[@]}"; do
    OUTPUT_FILE="$REPORTS_DIR/radon_${project}_${TIMESTAMP}.txt"
    echo -e "  ${YELLOW}Analyzing ${project}...${NC}"
    
    radon cc "${project}/src" -s -a > "$OUTPUT_FILE" 2>&1
    COMPLEXITY=$(tail -1 "$OUTPUT_FILE" | grep -oP "Average complexity: \K[A-F]" || echo "?")
    
    echo -e "  ${GREEN}✅ ${project}: Average complexity ${COMPLEXITY}${NC}"
    echo "${project}: Complexity ${COMPLEXITY}" >> "$SUMMARY_FILE"
done

# ===== SECURITY SCANS =====
echo -e "\n${BLUE}[6/7] Running security scans...${NC}"

# Bandit
echo -e "  ${YELLOW}Running Bandit SAST...${NC}"
for project in "${PROJECTS[@]}"; do
    OUTPUT_FILE="$REPORTS_DIR/bandit_${project}_${TIMESTAMP}.json"
    bandit -r "${project}/src" -f json -o "$OUTPUT_FILE" -ll 2>/dev/null || true
    
    HIGH=$(jq '.metrics._totals["SEVERITY.HIGH"] // 0' "$OUTPUT_FILE" 2>/dev/null || echo "0")
    MEDIUM=$(jq '.metrics._totals["SEVERITY.MEDIUM"] // 0' "$OUTPUT_FILE" 2>/dev/null || echo "0")
    
    if [ "$HIGH" -eq 0 ] && [ "$MEDIUM" -eq 0 ]; then
        echo -e "  ${GREEN}✅ ${project}: Bandit clean${NC}"
        echo "${project}: Bandit ✅" >> "$SUMMARY_FILE"
    else
        echo -e "  ${RED}⚠️  ${project}: HIGH=${HIGH}, MEDIUM=${MEDIUM}${NC}"
        echo "${project}: Bandit ⚠️ (H:${HIGH}, M:${MEDIUM})" >> "$SUMMARY_FILE"
    fi
done

# pip-audit
echo -e "  ${YELLOW}Running pip-audit...${NC}"
PIP_AUDIT_FILE="$REPORTS_DIR/pip_audit_${TIMESTAMP}.json"
if pip-audit --format=json > "$PIP_AUDIT_FILE" 2>&1; then
    echo -e "  ${GREEN}✅ pip-audit: No vulnerabilities found${NC}"
    echo "pip-audit: ✅ No vulnerabilities" >> "$SUMMARY_FILE"
else
    VULNS=$(jq 'length' "$PIP_AUDIT_FILE" 2>/dev/null || echo "?")
    echo -e "  ${RED}⚠️  pip-audit: ${VULNS} vulnerabilities found${NC}"
    echo "pip-audit: ⚠️ ${VULNS} vulnerabilities" >> "$SUMMARY_FILE"
fi

# ===== TESTS (skip in quick mode) =====
if [ "$QUICK_MODE" = false ]; then
    echo -e "\n${BLUE}[7/7] Running tests with coverage...${NC}"
    
    for project in "${PROJECTS[@]}"; do
        OUTPUT_FILE="$REPORTS_DIR/pytest_${project}_${TIMESTAMP}.txt"
        echo -e "  ${YELLOW}Testing ${project}...${NC}"
        
        pushd "$project" > /dev/null
        
        if pytest tests/ -q --tb=no -m "not slow" --cov=src --cov-report=term-missing > "../$OUTPUT_FILE" 2>&1; then
            COVERAGE=$(grep -oP "TOTAL\s+\d+\s+\d+\s+\K\d+" "../$OUTPUT_FILE" || echo "?")
            PASSED=$(grep -oP "\d+(?= passed)" "../$OUTPUT_FILE" || echo "?")
            echo -e "  ${GREEN}✅ ${project}: ${PASSED} tests, ${COVERAGE}% coverage${NC}"
            echo "${project}: Tests ✅ (${PASSED} passed, ${COVERAGE}%)" >> "../$SUMMARY_FILE"
        else
            echo -e "  ${RED}⚠️  ${project}: Some tests failed${NC}"
            echo "${project}: Tests ⚠️" >> "../$SUMMARY_FILE"
        fi
        
        popd > /dev/null
    done
else
    echo -e "\n${YELLOW}[7/7] Skipping tests (quick mode)${NC}"
    echo "Tests: Skipped (quick mode)" >> "$SUMMARY_FILE"
fi

# ===== FINAL SUMMARY =====
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    AUDIT SUMMARY                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

echo ""
cat "$SUMMARY_FILE"

echo -e "\n${GREEN}Reports saved to: ${REPORTS_DIR}/${NC}"
echo -e "${GREEN}Summary file: ${SUMMARY_FILE}${NC}"

# Exit with error if any critical issues
if grep -q "⚠️" "$SUMMARY_FILE"; then
    echo -e "\n${YELLOW}Some checks had warnings. Review the reports for details.${NC}"
    exit 0  # Don't fail, just warn
else
    echo -e "\n${GREEN}All checks passed! 🎉${NC}"
    exit 0
fi
