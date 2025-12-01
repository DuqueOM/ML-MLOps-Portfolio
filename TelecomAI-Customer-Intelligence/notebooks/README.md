# TelecomAI Notebooks

This directory contains Jupyter notebooks for exploration, analysis, and demonstration.

## Available Notebooks

| Notebook | Description |
|----------|-------------|
| `demo.ipynb` | End-to-end demo: load data, train/load model, predict, visualize |

## Planned Notebooks

| Notebook | Description | Status |
|----------|-------------|--------|
| `EDA.ipynb` | Exploratory Data Analysis of telecom user data | Planned |
| `explainability.ipynb` | SHAP/feature importance analysis | Planned |

## Usage

```bash
# Activate virtual environment
source .venv/bin/activate

# Start Jupyter
jupyter notebook notebooks/
```

## Note

Training and evaluation should be done via the CLI (`main.py`) or Makefile targets for reproducibility. Notebooks are for exploration and presentation only.
