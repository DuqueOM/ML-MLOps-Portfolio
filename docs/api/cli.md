# CLI Reference

Command-line interfaces for training and evaluation.

## BankChurn CLI

```bash
# Train model
python -m bankchurn.cli train --config configs/config.yaml

# Evaluate model
python -m bankchurn.cli evaluate --config configs/config.yaml

# Make predictions
python -m bankchurn.cli predict --input data.csv --output predictions.csv
```

<!-- [PLACEHOLDER: Add complete CLI documentation] -->
