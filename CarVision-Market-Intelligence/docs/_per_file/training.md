# Training Pipeline (`src/carvision/training.py`)

## Purpose
This module orchestrates the end-to-end model training process. It handles:
1.  **Data Loading:** Calls `src.carvision.data` to ingest and clean the CSV.
2.  **Splitting:** dividing data into Train/Val/Test sets.
3.  **Pipeline Construction:** creating a Scikit-Learn Pipeline with a ColumnTransformer (Imputation + Scaling) and a Random Forest Regressor.
4.  **Artifact Persistence:** saving the trained model (`model.joblib`) and metadata (`feature_columns.json`) for reproducible inference.

## Validation
To validate this module works correctly, execute the training command:
```bash
python main.py --mode train --config configs/config.yaml
```
**Success Criteria:**
- `artifacts/model.joblib` is created/updated.
- Validation metrics are printed to stdout.
