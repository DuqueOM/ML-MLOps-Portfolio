# Training Pipeline (`src/bankchurn/training.py`)

The `training.py` module implements the core machine learning pipeline for the BankChurn Predictor. It follows a modular object-oriented design centered around the `ChurnTrainer` class.

## Key Components
- **ChurnTrainer**: The main class orchestration the training process. It handles data loading, feature engineering, model fitting, and persistence.
- **Pipeline Construction**: It builds a `scikit-learn` Pipeline that includes:
  - **Preprocessing**: `ColumnTransformer` for scaling numerical features (`StandardScaler`) and encoding categorical features (`OneHotEncoder`).
  - **Imputation**: Handling missing values with `SimpleImputer`.
  - **Classifier**: A `VotingClassifier` (Ensemble) or `ResampleClassifier` (for imbalance).

## Validation
To validate the training logic locally, you can run the training command via the Makefile:

```bash
make train
```

Or execute the module directly (ensure you are in the project root):

```bash
python -m src.bankchurn.cli train --config configs/config.yaml --input data/raw/Churn.csv
```

Verify that `models/best_model.pkl` is generated upon completion.
