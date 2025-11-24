# Prediction Logic (`src/bankchurn/prediction.py`)

The `prediction.py` module encapsulates the inference logic, ensuring that the model is used consistently in both batch scripts and the real-time API.

## Key Components
- **ChurnPredictor**: Wraps the trained scikit-learn pipeline. It provides a simplified interface for making predictions on pandas DataFrames.
- **Artifact Loading**: Includes robust logic to load the full pipeline (`best_model.pkl`) or legacy separated artifacts if necessary.
- **Output Formatting**: Returns predictions including binary class (`prediction`) and probability scores (`probability`).

## Validation
To validate the prediction logic, you can run a manual prediction via the CLI:

```bash
python -m src.bankchurn.cli predict \
    --model models/best_model.pkl \
    --input data/raw/Churn.csv \
    --output predictions.csv
```

Check that `predictions.csv` contains the expected columns and reasonable values.
