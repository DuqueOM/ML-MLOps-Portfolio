# Reproducibility Guide

Step-by-step instructions to reproduce model training, evaluation, and serving for all projects.

---

## Prerequisites

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.11 | 3.12 |
| RAM | 8 GB | 16 GB |
| Disk | 20 GB | 50 GB |
| Docker | 20.10+ | Latest |

### Clone Repository

```bash
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio
```

---

## BankChurn Predictor

### Step 1: Environment Setup

```bash
cd BankChurn-Predictor

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -e ".[dev]"
```

### Step 2: Verify Data

```bash
# Check data exists
ls -la data/raw/

# Expected files:
# - train.csv (8,000 rows)
# - test.csv (2,000 rows)
```

### Step 3: Train Model

```bash
# Train with default configuration
python -m bankchurn.cli train --config configs/config.yaml

# Or with MLflow tracking
export MLFLOW_TRACKING_URI=http://localhost:5000
python -m bankchurn.cli train \
  --config configs/config.yaml \
  --experiment "bankchurn-reproduction"
```

**Expected Output:**

```
Loading configuration from configs/config.yaml
Loading training data: data/raw/train.csv
Training with 5-fold cross-validation
CV Results: AUC-ROC=0.844±0.018, F1=0.596±0.031
Training final model on full dataset
Model saved to models/model.pkl
```

### Step 4: Evaluate Model

```bash
python -m bankchurn.cli evaluate \
  --model models/model.pkl \
  --data data/raw/test.csv
```

**Expected Metrics:**

| Metric | Expected Value | Tolerance |
|--------|----------------|-----------|
| AUC-ROC | 0.853 | ±0.02 |
| Accuracy | 0.857 | ±0.02 |
| F1 Score | 0.604 | ±0.03 |

### Step 5: Run Tests

```bash
pytest tests/ -v --cov=src/bankchurn
```

**Expected Coverage:** ≥78%

---

## CarVision Market Intelligence

### Step 1: Environment Setup

```bash
cd CarVision-Market-Intelligence

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Step 2: Prepare Data

```bash
# Data should be in data/raw/vehicles.csv
# If missing, download from DVC
dvc pull data/raw/vehicles.csv
```

### Step 3: Train Model

```bash
python main.py train --config configs/config.yaml
```

**Expected Output:**

```
Loading data from data/raw/vehicles.csv
Applying filters: price=[1000, 500000], year>=1990
Records after filtering: ~51,000
Training RandomForestRegressor...
Model saved to models/model_v1.0.0.pkl
```

### Step 4: Evaluate Model

```bash
python main.py evaluate --config configs/config.yaml
```

**Expected Metrics:**

| Metric | Expected Value | Tolerance |
|--------|----------------|-----------|
| R² | 0.766 | ±0.02 |
| RMSE | $4,794 | ±$500 |
| MAPE | 27.6% | ±2% |

### Step 5: Run Tests

```bash
pytest tests/ -v --cov=src/carvision
```

**Expected Coverage:** ≥96%

---

## TelecomAI Customer Intelligence

### Step 1: Environment Setup

```bash
cd TelecomAI-Customer-Intelligence

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Step 2: Train Model

```bash
python main.py train --config configs/config.yaml
```

### Step 3: Evaluate Model

```bash
python main.py evaluate --config configs/config.yaml
```

**Expected Metrics:**

| Metric | Expected Value | Tolerance |
|--------|----------------|-----------|
| AUC-ROC | 0.840 | ±0.02 |
| Accuracy | 0.812 | ±0.02 |
| F1 Score | 0.618 | ±0.03 |

### Step 4: Run Tests

```bash
pytest tests/ -v --cov=src/telecom
```

**Expected Coverage:** ≥96%

---

## Full Stack Reproduction

### Using Docker Compose

```bash
# From repository root
cd ML-MLOps-Portfolio

# Generate demo models
bash scripts/setup_demo_models.sh

# Build and start all services
docker-compose -f docker-compose.demo.yml up -d --build

# Verify all services
docker-compose -f docker-compose.demo.yml ps
```

### Using Makefile

```bash
# Train all models
make all-train

# Test all projects
make all-test

# Build Docker images
make docker-build
```

---

## Random Seed Configuration

All random operations use fixed seeds for reproducibility:

| Component | Seed | Location |
|-----------|------|----------|
| Train/Test Split | 42 | `configs/config.yaml` |
| Cross-Validation | 42 | `configs/config.yaml` |
| Model Training | 42 | Model hyperparameters |
| NumPy | 42 | Set at runtime |

### Setting Seeds Programmatically

```python
import numpy as np
import random

SEED = 42

np.random.seed(SEED)
random.seed(SEED)

# For scikit-learn
model = RandomForestClassifier(random_state=SEED)
```

---

## Data Versioning with DVC

### Pull Data

```bash
# Configure remote (if not already done)
dvc remote add -d storage s3://your-bucket/dvc-storage

# Pull all data
dvc pull
```

### Track Data Changes

```bash
# After modifying data
dvc add data/raw/train.csv
git add data/raw/train.csv.dvc
git commit -m "chore: update training data"
dvc push
```

---

## MLflow Experiment Tracking

### Start MLflow Server

```bash
docker-compose -f docker-compose.mlflow.yml up -d
```

### View Experiments

Open http://localhost:5000

### Compare Runs

```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")

# List experiments
experiments = mlflow.search_experiments()

# Get runs for an experiment
runs = mlflow.search_runs(experiment_ids=["898454169632142870"])
print(runs[["run_id", "metrics.roc_auc", "metrics.f1_score"]])
```

---

## Troubleshooting Reproduction

### Different Metrics

If your metrics differ from expected:

1. **Check Python version**: Different Python versions may produce slight variations
2. **Verify dependencies**: `pip freeze > current.txt && diff requirements.txt current.txt`
3. **Confirm data**: `md5sum data/raw/train.csv` should match expected hash
4. **Check random seeds**: Ensure all seeds are set correctly

### Memory Issues

```bash
# Reduce batch size in config
training:
  batch_size: 1000  # Reduce if OOM
```

### Slow Training

```bash
# Enable parallelism
model:
  n_jobs: -1  # Use all cores
```

---

## Verification Checklist

Before claiming reproduction success:

- [ ] All unit tests pass (`pytest tests/ -v`)
- [ ] Coverage meets threshold
- [ ] Model metrics within tolerance
- [ ] API health checks pass
- [ ] Integration tests pass (`scripts/run_demo_tests.sh`)

---

## Support

If you cannot reproduce results:

1. Open a GitHub Issue with:
   - Python version
   - OS version
   - `pip freeze` output
   - Full error log
2. Tag with `reproducibility` label
