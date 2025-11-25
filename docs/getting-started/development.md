# Development Setup

Complete guide for setting up a local development environment.

## Prerequisites

- Python 3.11 or 3.12
- Git
- Docker and Docker Compose
- Make (optional but recommended)

## Initial Setup

```bash
# Clone and enter repository
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

## Project-Specific Setup

### BankChurn Predictor

```bash
cd BankChurn-Predictor
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

### CarVision Market Intelligence

```bash
cd CarVision-Market-Intelligence
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

### TelecomAI Customer Intelligence

```bash
cd TelecomAI-Customer-Intelligence
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

## Running Tests

```bash
# All tests
pytest tests/ -v --cov=src

# With coverage report
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

## Code Quality

```bash
# Format code
black .
isort .

# Lint
flake8 .

# Type check
mypy src/
```

## Local Services

```bash
# Start MLflow
docker-compose -f docker-compose.mlflow.yml up -d

# Start full demo stack
docker-compose -f docker-compose.demo.yml up -d --build
```
