# prediction.py

**Location:** `src/bankchurn/prediction.py`

## Purpose
This module provides the inference logic for the trained model. It is designed to be used by both the CLI (batch prediction) and the API (real-time prediction).

It ensures that:
1.  The model and preprocessor are loaded correctly from disk.
2.  Input data (DataFrame) is transformed using the *fitted* preprocessor.
3.  Predictions are generated (probability and class).
4.  Risk levels (LOW, MEDIUM, HIGH) are assigned based on probability thresholds.

## Key Components
-   `ChurnPredictor`: Class for loading artifacts and running inference.
-   `predict`: Core method taking a DataFrame and returning predictions with metadata.
-   `predict_batch`: Wrapper for reading/writing CSVs for bulk processing.

## Validation
To test prediction capabilities:
```bash
# Unit/Integration test
pytest tests/test_integration.py

# CLI test
make predict
```
