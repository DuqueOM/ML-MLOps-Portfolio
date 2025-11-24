# Data Preprocessing (`data/preprocess.py`)

This script handles the initial data cleaning and preparation before the training pipeline begins. It is typically the first stage in the DVC pipeline.

## Purpose
- **Cleaning**: Removes irrelevant columns (e.g., `RowNumber`, `Surname`) defined in the configuration.
- **Validation**: Ensures the input CSV meets the expected schema structure.
- **Formatting**: Saves the processed data in a standardized CSV format ready for training.

## Validation
You can run the preprocessing script manually to verify it works:

```bash
python data/preprocess.py \
    --input data/raw/Churn.csv \
    --output data/processed/train.csv \
    --config configs/config.yaml
```

Verify that `data/processed/train.csv` exists and does not contain the dropped columns.
