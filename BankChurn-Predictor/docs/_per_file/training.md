# training.py

**Location:** `src/bankchurn/training.py`

## Purpose
This module implements the end-to-end training pipeline for the Churn Prediction model. It handles:
1.  **Data Loading**: Reads CSV data using pandas.
2.  **Splitting**: Performs stratified train/test split *before* any fitting to ensure no data leakage.
3.  **Preprocessing**: Builds a `ColumnTransformer` that scales numerical features and one-hot encodes categorical features.
4.  **Training**: Fits a `VotingClassifier` (Logistic Regression + Random Forest) on the training set.
5.  **Evaluation**: Calculates F1, AUC, and other metrics on the held-out test set.
6.  **Persistence**: Saves the trained pipeline and preprocessor using `joblib`.

## Key Components
-   `ChurnTrainer`: Main class encapsulating the logic.
-   `build_preprocessor`: Dynamic creation of sklearn pipelines based on config.
-   `train`: Orchestrates the fit/transform/predict cycle.

## Validation
To verify this module works correctly, run the integration test:
```bash
pytest tests/test_integration.py
```
Or run a training job directly:
```bash
make train
```
