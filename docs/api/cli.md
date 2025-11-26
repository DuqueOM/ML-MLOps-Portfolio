# CLI Reference

Command-line interfaces for training, evaluation, and inference across all projects.

---

## BankChurn CLI

The BankChurn project provides a comprehensive CLI for the full ML lifecycle.

### Installation

```bash
cd BankChurn-Predictor
pip install -e ".[dev]"
```

### Commands Overview

| Command | Description |
|---------|-------------|
| `train` | Train a new model |
| `evaluate` | Evaluate model performance |
| `predict` | Make predictions on new data |

### train

Train a new churn prediction model.

```bash
python -m bankchurn.cli train [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--config` | PATH | `configs/config.yaml` | Configuration file path |
| `--output` | PATH | `models/` | Output directory for model |
| `--experiment` | TEXT | `default` | MLflow experiment name |
| `--cv-folds` | INT | `5` | Cross-validation folds |
| `--verbose` | FLAG | `False` | Enable verbose logging |

**Example:**

```bash
# Train with default config
python -m bankchurn.cli train

# Train with custom config and MLflow tracking
python -m bankchurn.cli train \
  --config configs/production.yaml \
  --experiment "production-v2" \
  --cv-folds 10 \
  --verbose
```

**Output:**

```
2025-11-25 12:00:00 - INFO - Loading configuration from configs/config.yaml
2025-11-25 12:00:01 - INFO - Loading training data: data/raw/train.csv
2025-11-25 12:00:02 - INFO - Training with 5-fold cross-validation
2025-11-25 12:00:15 - INFO - CV Results: AUC-ROC=0.844±0.018, F1=0.596±0.031
2025-11-25 12:00:20 - INFO - Training final model on full dataset
2025-11-25 12:00:25 - INFO - Model saved to models/model.pkl
2025-11-25 12:00:25 - INFO - MLflow run ID: abc123def456
```

### evaluate

Evaluate a trained model on test data.

```bash
python -m bankchurn.cli evaluate [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--config` | PATH | `configs/config.yaml` | Configuration file |
| `--model` | PATH | `models/model.pkl` | Model file path |
| `--data` | PATH | `data/raw/test.csv` | Test data path |
| `--output` | PATH | `results/` | Results output directory |

**Example:**

```bash
python -m bankchurn.cli evaluate \
  --model models/model.pkl \
  --data data/raw/test.csv \
  --output results/evaluation/
```

**Output:**

```
=== Model Evaluation Results ===

Metrics:
  AUC-ROC:   0.853
  Accuracy:  0.857
  Precision: 0.692
  Recall:    0.536
  F1 Score:  0.604

Confusion Matrix:
              Predicted
              Neg    Pos
Actual Neg   1496    97
       Pos    189   218

Results saved to: results/evaluation/metrics.json
```

### predict

Make predictions on new data.

```bash
python -m bankchurn.cli predict [OPTIONS]
```

**Options:**

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--input` | PATH | Yes | Input CSV file |
| `--output` | PATH | Yes | Output CSV file |
| `--model` | PATH | No | Model path (default: models/model.pkl) |
| `--threshold` | FLOAT | No | Classification threshold (default: 0.5) |
| `--include-proba` | FLAG | No | Include probabilities |

**Example:**

```bash
python -m bankchurn.cli predict \
  --input data/new_customers.csv \
  --output predictions.csv \
  --include-proba \
  --threshold 0.4
```

**Output CSV:**

```csv
customer_id,prediction,probability,risk_level
1001,0,0.15,low
1002,1,0.72,high
1003,0,0.38,medium
```

---

## CarVision CLI

The CarVision project uses a `main.py` script for training and evaluation.

### Commands

```bash
cd CarVision-Market-Intelligence

# Train model
python main.py train --config configs/config.yaml

# Evaluate model
python main.py evaluate --config configs/config.yaml

# Run market analysis
python main.py analyze --config configs/config.yaml
```

### train

```bash
python main.py train [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--config` | PATH | `configs/config.yaml` | Configuration file |
| `--output` | PATH | `models/` | Output directory |

**Example:**

```bash
python main.py train --config configs/config.yaml
```

### evaluate

```bash
python main.py evaluate [OPTIONS]
```

**Output:**

```
=== CarVision Model Evaluation ===

Regression Metrics:
  R²:   0.766
  RMSE: $4,794.27
  MAE:  $2,370.70
  MAPE: 27.6%

Feature Importance:
  1. model_year:  0.35
  2. odometer:    0.28
  3. condition:   0.15
  4. fuel:        0.12
  5. type:        0.10
```

### analyze

Run market analysis and generate reports.

```bash
python main.py analyze --config configs/config.yaml --output reports/
```

---

## TelecomAI CLI

### Commands

```bash
cd TelecomAI-Customer-Intelligence

# Train model
python main.py train --config configs/config.yaml

# Evaluate model
python main.py evaluate --config configs/config.yaml

# Batch predict
python main.py predict --input data/customers.csv --output predictions.csv
```

### train

```bash
python main.py train [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--config` | PATH | `configs/config.yaml` | Configuration file |
| `--experiment` | TEXT | `telecom-training` | MLflow experiment |

**Example:**

```bash
python main.py train \
  --config configs/config.yaml \
  --experiment production-v1
```

### evaluate

**Output:**

```
=== TelecomAI Model Evaluation ===

Classification Metrics:
  AUC-ROC:   0.840
  Accuracy:  81.2%
  Precision: 81.7%
  Recall:    49.7%
  F1 Score:  0.618
```

---

## Common Options

All CLIs support these common options:

| Option | Description |
|--------|-------------|
| `--help` | Show help message |
| `--version` | Show version |
| `--verbose` / `-v` | Enable verbose output |
| `--quiet` / `-q` | Suppress non-error output |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MLFLOW_TRACKING_URI` | MLflow server URL | `file:./mlruns` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `CONFIG_PATH` | Default config path | `configs/config.yaml` |

**Example:**

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
export LOG_LEVEL=DEBUG
python -m bankchurn.cli train
```

---

## Makefile Shortcuts

Each project includes a Makefile for common operations:

```bash
# BankChurn
make train          # Train model
make evaluate       # Evaluate model
make test           # Run tests
make lint           # Run linters
make clean          # Clean artifacts

# All projects
make all-train      # Train all models
make all-test       # Test all projects
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | File not found |
| 4 | Model loading error |
| 5 | Data validation error |
