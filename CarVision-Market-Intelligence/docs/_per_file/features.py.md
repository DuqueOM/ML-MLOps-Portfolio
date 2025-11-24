# Feature Engineering (`src/carvision/features.py`)

**Location:** `src/carvision/features.py`

## Purpose
Defines the `FeatureEngineer` class, a custom scikit-learn transformer that encapsulates all feature engineering logic. By creating a dedicated transformer, we ensure that the exact same transformations (e.g., calculating `vehicle_age` from `model_year`) are applied consistently during both training and inference.

## Key Transformations
-   **Vehicle Age**: Computes `current_year - model_year`.
-   **Brand Extraction**: Extracts manufacturer from the `model` text field (e.g., "ford f-150" -> "ford").
-   **Price per Mile**: (Training only) Calculates price efficiency logic. Note: This feature must be dropped before model input to prevent leakage.

## Usage
This class is designed to be the first step in a scikit-learn Pipeline.

```python
from src.carvision.features import FeatureEngineer
pipeline = Pipeline([
    ('features', FeatureEngineer(current_year=2024)),
    ('model', RandomForestRegressor())
])
```

## Validation
Run the unit tests dedicated to feature engineering consistency:
```bash
pytest tests/test_features.py
```
