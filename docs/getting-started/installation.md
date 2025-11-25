# Installation Guide

Detailed installation instructions for development and production environments.

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.11 | 3.12 |
| RAM | 4 GB | 8 GB |
| Disk | 10 GB | 20 GB |
| Docker | 20.10+ | Latest |

## Installation Methods

### Method 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio

# Start all services
docker-compose -f docker-compose.demo.yml up -d --build
```

### Method 2: Local Python

```bash
# Clone repository
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install project (example: BankChurn)
cd BankChurn-Predictor
pip install -e ".[dev]"
```

### Method 3: Development Setup

See [Development Setup](development.md) for full developer environment configuration.

## Verification

```bash
# Check Docker services
docker-compose -f docker-compose.demo.yml ps

# Run integration tests
bash scripts/run_demo_tests.sh
```

## Troubleshooting

See [Troubleshooting Guide](../operations/troubleshooting.md) for common issues.
