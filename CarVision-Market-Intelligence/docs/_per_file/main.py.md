# Main CLI Entrypoint (`main.py`)

**Location:** `main.py`

## Purpose
This script serves as the central command-line interface (CLI) for the CarVision application. It unifies all major workflows—training, evaluation, prediction, analysis, and reporting—into a single entry point, ensuring consistent configuration handling and logging.

## Workflows
-   **Train**: Runs the full training pipeline (`clean` -> `engineer` -> `train`).
-   **Evaluate**: Assessing model performance against test data using CV and Bootstrap.
-   **Predict**: Generating price predictions for new data (batch or single).
-   **Analysis**: Generating market insights and executive summaries.
-   **Report**: creating HTML/PDF reports of market analysis.

## Usage
The script is typically invoked via `make` commands, but can be run directly:

```bash
# Training
python main.py --mode train --config configs/config.yaml

# Prediction
python main.py --mode predict --payload '{"model": "ford f-150", "year": 2015, ...}'

# Analysis
python main.py --mode analysis --input data/raw/vehicles_us.csv
```

## Validation
To verify the CLI handles arguments correctly without running a full job:
```bash
python main.py --help
```
Ensure all modes are listed and help text is displayed.
