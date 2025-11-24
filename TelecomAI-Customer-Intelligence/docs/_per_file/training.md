# Training Module (`src/telecom/training.py`)

## Purpose
Handles the creation and training of the machine learning model.
It uses a `sklearn.pipeline.Pipeline` to chain the preprocessor (imputation + scaling) with the classifier. This unified object is what gets saved, ensuring consistency.

## Validation
Execute:
```bash
python main.py --mode train
```
**Success Criteria:**
- Logs show "Starting training...".
- `artifacts/model.joblib` file is updated.
- Logs output final accuracy score.
