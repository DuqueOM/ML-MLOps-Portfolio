# DVC Pipeline (`dvc.yaml`)

The `dvc.yaml` file defines the data science pipeline stages, ensuring reproducibility and enabling smart caching of intermediate results.

## Stages
- **preprocess**: Cleans the raw data (`data/raw/Churn.csv`) and produces `data/processed/train.csv`. Dependencies: `data/preprocess.py`.
- **train**: Trains the model using the processed data and configuration. Outputs `models/best_model.pkl` and metrics. Dependencies: `src/bankchurn/training.py`.
- **evaluate**: Evaluates the trained model on a test set or cross-validation, updating `results/metrics.json`.

## Validation
To execute the full pipeline ensuring all dependencies are satisfied:

```bash
dvc repro
```

DVC will check md5 hashes and only run stages that have changed.
