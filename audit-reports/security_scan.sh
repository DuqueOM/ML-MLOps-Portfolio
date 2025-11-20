#!/usr/bin/env bash
# Security Scan Script - Checks for security vulnerabilities
# Usage: ./security_scan.sh

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$REPO_ROOT/check_results"
mkdir -p "$RESULTS_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SECURITY_REPORT="$RESULTS_DIR/security_scan_${TIMESTAMP}.txt"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Security Scan${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Redirect to file and console
exec > >(tee -a "$SECURITY_REPORT")
exec 2>&1

echo "Security Scan Report"
echo "Date: $(date)"
echo "Repository: $REPO_ROOT"
echo ""

ISSUES_FOUND=0

# 1. Check for hardcoded secrets
echo -e "${YELLOW}1. Scanning for hardcoded secrets...${NC}"
echo "Searching for: password, secret, api_key, token, credential"
echo ""

SECRETS=$(grep -r -i "password\|secret\|api_key\|token\|credential" \
    --include="*.py" \
    --include="*.yaml" \
    --include="*.yml" \
    --include="*.json" \
    --include="*.env" \
    --exclude-dir=".git" \
    --exclude-dir=".venv" \
    --exclude-dir="venv" \
    --exclude-dir="__pycache__" \
    --exclude="*.txt" \
    . || true)

if [ -n "$SECRETS" ]; then
    echo -e "${RED}⚠ Potential secrets found:${NC}"
    echo "$SECRETS"
    ((ISSUES_FOUND++))
    echo ""
else
    echo -e "${GREEN}✓ No obvious secrets found${NC}"
    echo ""
fi

# 2. Check for .env files in git
echo -e "${YELLOW}2. Checking for .env files in repository...${NC}"
ENV_FILES=$(find . -name ".env" -not -path "./.git/*" -not -path "./.venv/*" -not -path "./venv/*" || true)

if [ -n "$ENV_FILES" ]; then
    echo -e "${RED}⚠ .env files found (should not be in git):${NC}"
    echo "$ENV_FILES"
    ((ISSUES_FOUND++))
    echo ""
else
    echo -e "${GREEN}✓ No .env files tracked in git${NC}"
    echo ""
fi

# 3. Check specific vulnerable files
echo -e "${YELLOW}3. Checking known vulnerable patterns...${NC}"

# Check docker-compose for hardcoded passwords
if grep -q "PASSWORD.*:" infra/docker-compose-mlflow.yml 2>/dev/null; then
    if ! grep -q "PASSWORD.*\${" infra/docker-compose-mlflow.yml 2>/dev/null; then
        echo -e "${RED}⚠ CRITICAL: Hardcoded passwords in infra/docker-compose-mlflow.yml${NC}"
        grep -n "PASSWORD" infra/docker-compose-mlflow.yml
        ((ISSUES_FOUND++))
        echo ""
    else
        echo -e "${GREEN}✓ docker-compose uses environment variables${NC}"
        echo ""
    fi
fi

# 4. Check for common security anti-patterns
echo -e "${YELLOW}4. Checking for security anti-patterns...${NC}"

# SQL injection patterns
echo "Checking for potential SQL injection:"
SQL_INJECT=$(grep -rn "execute.*%s\|execute.*format\|execute.*+" --include="*.py" . || true)
if [ -n "$SQL_INJECT" ]; then
    echo -e "${YELLOW}⚠ Potential SQL injection patterns found:${NC}"
    echo "$SQL_INJECT"
    ((ISSUES_FOUND++))
else
    echo -e "${GREEN}✓ No obvious SQL injection patterns${NC}"
fi
echo ""

# eval() usage
echo "Checking for eval() usage:"
EVAL_USAGE=$(grep -rn "eval(" --include="*.py" --exclude-dir=tests . || true)
if [ -n "$EVAL_USAGE" ]; then
    echo -e "${YELLOW}⚠ eval() usage found (security risk):${NC}"
    echo "$EVAL_USAGE"
    ((ISSUES_FOUND++))
else
    echo -e "${GREEN}✓ No eval() usage found${NC}"
fi
echo ""

# 5. Run bandit if available
echo -e "${YELLOW}5. Running bandit security scanner...${NC}"
if command -v bandit &> /dev/null; then
    bandit -r . -ll -i \
        --exclude ".venv,venv,__pycache__,.pytest_cache,.git" \
        -f txt \
        || echo "Bandit found issues (see above)"
    echo ""
else
    echo -e "${YELLOW}⚠ Bandit not installed. Install with: pip install bandit${NC}"
    echo ""
fi

# 6. Check dependencies for known vulnerabilities (if pip-audit available)
echo -e "${YELLOW}6. Checking dependencies for vulnerabilities...${NC}"
if command -v pip-audit &> /dev/null; then
    for project in BankChurn-Predictor CarVision-Market-Intelligence; do
        if [ -f "$project/requirements.txt" ]; then
            echo "Scanning $project/requirements.txt..."
            pip-audit -r "$project/requirements.txt" || echo "Vulnerabilities found in $project"
            echo ""
        fi
    done
else
    echo -e "${YELLOW}⚠ pip-audit not installed. Install with: pip install pip-audit${NC}"
    echo ""
fi

# 7. Check file permissions
echo -e "${YELLOW}7. Checking sensitive file permissions...${NC}"
EXECUTABLE_CONFIGS=$(find . -name "*.yaml" -o -name "*.yml" -o -name "*.json" | xargs ls -l | grep "rwx" || true)
if [ -n "$EXECUTABLE_CONFIGS" ]; then
    echo -e "${YELLOW}⚠ Config files with execute permissions:${NC}"
    echo "$EXECUTABLE_CONFIGS"
    ((ISSUES_FOUND++))
else
    echo -e "${GREEN}✓ Config file permissions OK${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Security Scan Summary${NC}"
echo -e "${BLUE}========================================${NC}\n"

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ No critical security issues found${NC}"
    echo ""
    echo "Recommendations:"
    echo "  - Keep dependencies updated (use Dependabot)"
    echo "  - Run 'pip-audit' regularly"
    echo "  - Add 'bandit' to pre-commit hooks"
    echo "  - Review and rotate any exposed credentials"
else
    echo -e "${RED}⚠ Found $ISSUES_FOUND potential security issues${NC}"
    echo ""
    echo "Action items:"
    echo "  1. Review findings above"
    echo "  2. Apply security patches from fixes/ directory"
    echo "  3. Rotate any exposed credentials"
    echo "  4. Update .gitignore to prevent future leaks"
fi

echo ""
echo "Report saved to: $SECURITY_REPORT"

# Exit code
if [ $ISSUES_FOUND -gt 0 ]; then
    exit 1
else
    exit 0
fi
