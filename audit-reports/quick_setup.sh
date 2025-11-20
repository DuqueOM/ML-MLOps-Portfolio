#!/usr/bin/env bash
# Quick Setup Script - Sets up a project for development
# Usage: ./quick_setup.sh [project_name]
# Example: ./quick_setup.sh BankChurn-Predictor

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT="${1:-BankChurn-Predictor}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Quick Setup: $PROJECT${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Navigate to project
cd "$REPO_ROOT/$PROJECT" || {
    echo -e "${RED}ERROR: Project not found: $PROJECT${NC}"
    exit 1
}

# Step 1: Check Python version
echo -e "${YELLOW}Step 1: Checking Python version${NC}"
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Found Python $PYTHON_VERSION"

# Check if version is 3.10+
MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]; }; then
    echo -e "${RED}ERROR: Python 3.10+ required, found $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python version OK${NC}\n"

# Step 2: Create virtual environment (if not exists)
echo -e "${YELLOW}Step 2: Setting up virtual environment${NC}"
if [ ! -d ".venv" ]; then
    python -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
source .venv/bin/activate || {
    echo -e "${RED}ERROR: Failed to activate virtual environment${NC}"
    exit 1
}
echo -e "${GREEN}✓ Virtual environment activated${NC}\n"

# Step 3: Upgrade pip
echo -e "${YELLOW}Step 3: Upgrading pip${NC}"
pip install --upgrade pip -q
echo -e "${GREEN}✓ pip upgraded${NC}\n"

# Step 4: Install dependencies
echo -e "${YELLOW}Step 4: Installing dependencies${NC}"
if [ -f "requirements-core.txt" ]; then
    echo "Installing from requirements-core.txt..."
    pip install -r requirements-core.txt
    echo -e "${GREEN}✓ Core dependencies installed${NC}"
elif [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt (this may take a while)..."
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}ERROR: No requirements file found${NC}"
    exit 1
fi
echo ""

# Step 5: Install development dependencies
echo -e "${YELLOW}Step 5: Installing development dependencies${NC}"
pip install pytest pytest-cov black flake8 mypy -q
echo -e "${GREEN}✓ Dev dependencies installed${NC}\n"

# Step 6: Verify installation
echo -e "${YELLOW}Step 6: Verifying installation${NC}"
python -c "import pandas, numpy, sklearn; print('Core libraries OK')" || {
    echo -e "${RED}ERROR: Failed to import core libraries${NC}"
    exit 1
}
echo -e "${GREEN}✓ Installation verified${NC}\n"

# Step 7: Check if data exists
echo -e "${YELLOW}Step 7: Checking data files${NC}"
if [ -f "data/raw/Churn.csv" ] || [ -d "data" ]; then
    echo -e "${GREEN}✓ Data directory found${NC}"
else
    echo -e "${YELLOW}⚠ No data directory - you may need to download data${NC}"
fi
echo ""

# Step 8: Run quick test
echo -e "${YELLOW}Step 8: Running quick test${NC}"
if [ -d "tests" ]; then
    pytest tests/ -v --tb=short -k "not slow" -x || {
        echo -e "${YELLOW}⚠ Some tests failed (this is OK for initial setup)${NC}"
    }
    echo -e "${GREEN}✓ Test suite executable${NC}"
else
    echo -e "${YELLOW}No tests directory found${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${GREEN}Next steps:${NC}"
echo "1. Activate the virtual environment:"
echo "   ${YELLOW}source .venv/bin/activate${NC}"
echo ""
echo "2. Train a model:"
echo "   ${YELLOW}python main.py --mode train --config configs/config.yaml --seed 42${NC}"
echo ""
echo "3. Start the API:"
echo "   ${YELLOW}uvicorn app.fastapi_app:app --reload${NC}"
echo ""
echo "4. Run tests:"
echo "   ${YELLOW}pytest --cov=. --cov-report=term-missing${NC}"
echo ""
echo "5. Check code quality:"
echo "   ${YELLOW}../ci_checks.sh $PROJECT${NC}"
echo ""

echo -e "${GREEN}Happy coding! 🚀${NC}"
