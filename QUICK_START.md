# 🚀 Quick Start - ML/MLOps Portfolio

This guide provides the fastest way to run the portfolio projects locally using Docker.

## ⚡ One-Line Demo (Recommended)

To spin up the entire stack (3 APIs + Streamlit Dashboard + MLflow):

```bash
make docker-demo
```

This command will:
1. Build optimized Docker images for all 3 projects.
2. Start the MLflow Tracking Server.
3. Launch all APIs and the Dashboard.
4. Run automated smoke tests to verify everything is working.

**Access Points:**
- **BankChurn API**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **CarVision Dashboard**: [http://localhost:8501](http://localhost:8501)
- **CarVision API**: [http://localhost:8002/docs](http://localhost:8002/docs)
- **TelecomAI API**: [http://localhost:8003/docs](http://localhost:8003/docs)
- **MLflow UI**: [http://localhost:5000](http://localhost:5000)

---

## 🛠️ Manual Setup

If you prefer to run specific commands or develop locally:

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Make

### 2. Installation
```bash
# Install dependencies for all projects
make install
```

### 3. Running Tests
```bash
# Run unit and integration tests
make test
```

### 4. Local Development
Refer to the **[Operations Runbook](docs/OPERATIONS_PORTFOLIO.md)** for detailed instructions on:
- Retraining models locally
- Debugging services
- Managing dependencies

---

## 📊 Validation

### Integration Tests
To run the Python-based integration tests:
```bash
# Ensure demo stack is running
docker-compose -f docker-compose.demo.yml up -d

# Run integration tests
pytest tests/integration/test_demo.py -v

# Tear down
docker-compose -f docker-compose.demo.yml down
```

### Legacy Shell Script (Alternative)
```bash
bash scripts/run_demo_tests.sh
```

**Note**: The Python tests (`test_demo.py`) are more comprehensive and include proper health checks, prediction validation, and response schema verification.
