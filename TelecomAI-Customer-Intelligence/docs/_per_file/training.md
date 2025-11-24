# src/telecom/training.py

## Purpose
Orchestrates the model training pipeline. It handles data loading, splitting, preprocessing (feature scaling/imputation), model fitting, and artifact serialization.

## Key Features
- **Unified Pipeline:** Wraps the `ColumnTransformer` (preprocessor) and the Classifier into a single Scikit-Learn `Pipeline` object. This ensures that raw data sent to the model during inference is processed exactly the same way as training data.
- **Config Driven:** All hyperparameters (split ratio, model params, seeds) are injected via the `Config` object.
- **Reproducibility:** Sets random seeds for both splitting and model initialization.

## Validation
Run a full training cycle using the CLI:
```bash
python main.py --mode train --config configs/config.yaml
# Verify artifacts/model.joblib is created
```
