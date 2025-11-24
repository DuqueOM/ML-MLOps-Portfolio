import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split

# Ensure src is in path
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.bankchurn.config import BankChurnConfig, DataConfig, MLflowConfig, ModelConfig  # noqa: E402
from src.bankchurn.training import ChurnTrainer  # noqa: E402


def test_leakage_prevention():
    """Ensure preprocessor is NOT fitted on test data."""
    # Setup config
    config = BankChurnConfig(
        data=DataConfig(
            target_column="target", numerical_features=["feat1"], categorical_features=["cat1"], drop_columns=[]
        ),
        model=ModelConfig(test_size=0.5, random_state=42),
        mlflow=MLflowConfig(enabled=False),
    )

    # Create synthetic data with an outlier
    # 10 samples. 9 are 0.0, 1 is 1000.0.
    # We need to ensure the outlier is in TEST set.
    # With random_state=42, let's check where it goes.

    df = pd.DataFrame(
        {
            "feat1": [0.0] * 9 + [1000.0],
            "cat1": ["a"] * 10,
            "target": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1],  # Balanced target to allow stratify
        }
    )

    # Verify split manually
    X = df.drop(columns=["target"])
    y = df["target"]
    X_train, X_test, _, _ = train_test_split(X, y, test_size=0.5, random_state=42, stratify=y)

    # Check where the outlier (1000.0) is.
    outlier_in_train = 1000.0 in X_train["feat1"].values

    print(f"Outlier in train: {outlier_in_train}")

    # If outlier is in train, we can't test leakage easily (mean will be high anyway).
    # We need to find a seed or data arrangement where outlier is in TEST.
    # If random_state=42 puts outlier in train, let's try flipping the data order?
    # Actually, if outlier is in train, leakage or not, mean is high.
    # If outlier is in test, NO leakage -> mean is low (0.0). Leakage -> mean is high (~100).

    if outlier_in_train:
        # Skip or force a different seed?
        # Let's try to construct data such that we know the split.
        # Or simpler: Just verify that the scaler mean corresponds to X_train mean, NOT global mean.
        pass

    trainer = ChurnTrainer(config, random_state=42)
    model, metrics = trainer.train(df, df["target"], use_cv=False)

    scaler = trainer.preprocessor_.named_transformers_["num"]["scaler"]
    scaler_mean = scaler.mean_[0]

    # Calculate expected mean from the ACTUAL train split used by trainer
    # (Trainer uses same random_state=42 and stratify)
    expected_mean = X_train["feat1"].mean()
    global_mean = df["feat1"].mean()

    print(f"Scaler mean: {scaler_mean}")
    print(f"Expected (Train) mean: {expected_mean}")
    print(f"Global mean: {global_mean}")

    # Assert scaler matches TRAIN mean
    np.testing.assert_almost_equal(scaler_mean, expected_mean, decimal=5, err_msg="Scaler mean should match Train mean")

    # Assert scaler does NOT match Global mean (unless they accidentally coincide)
    if expected_mean != global_mean:
        assert scaler_mean != global_mean, "Scaler mean matches global mean - Leakage detected!"
    else:
        pytest.skip("Train mean accidentally equals Global mean, cannot detect leakage.")


def test_src_import_works():
    """Verify src modules are importable."""
    # This should work now that __init__.py is fixed
    from src.bankchurn import ChurnPredictor

    assert ChurnPredictor is not None


def test_cli_structure():
    """Verify CLI structure."""
    from src.bankchurn.cli import create_parser

    parser = create_parser()
    args = parser.parse_args(["train", "--config", "config.yaml", "--input", "data.csv"])
    assert args.command == "train"


def test_fastapi_app_import():
    """Verify FastAPI app can be imported."""
    from app.fastapi_app import app

    assert app is not None
