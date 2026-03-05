# CLI Reference

Each project provides a CLI for training and evaluation.

## BankChurn

```bash
python -m bankchurn.cli train --config configs/config.yaml
python -m bankchurn.cli predict --input data/sample.json
python -m bankchurn.cli evaluate --model models/model.joblib
```

## NLPInsight

```bash
python -m nlpinsight.cli train --config configs/config.yaml
python -m nlpinsight.cli predict --text "Strong quarterly earnings"
```

## Common Options

| Flag | Description |
|------|-------------|
| `--config` | Path to YAML config file |
| `--model` | Path to model artifact |
| `--verbose` | Enable debug logging |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/setup_demo_models.sh` | Generate demo model artifacts |
| `scripts/run_experiments.py` | Run MLflow experiments (9 runs) |
| `scripts/train_production_models.py` | Train all 3 models with MLflow |
| `scripts/benchmark_optimizations.py` | Performance benchmarks |

---

*Last Updated: March 2026*
