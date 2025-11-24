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

import joblib
from sklearn.pipeline import Pipeline

from src.bankchurn.config import (  # noqa: E402
    BankChurnConfig,
    DataConfig,
    MLflowConfig,
    ModelConfig,
    RandomForestConfig,
)
from src.bankchurn.evaluation import ModelEvaluator
from src.bankchurn.prediction import ChurnPredictor
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


@pytest.fixture
def sample_data():
    """Create synthetic data for testing."""
    n_samples = 100
    data = pd.DataFrame(
        {
            "CreditScore": np.random.randint(300, 850, n_samples),
            "Geography": np.random.choice(["France", "Spain", "Germany"], n_samples),
            "Gender": np.random.choice(["Male", "Female"], n_samples),
            "Age": np.random.randint(18, 90, n_samples),
            "Tenure": np.random.randint(0, 10, n_samples),
            "Balance": np.random.uniform(0, 200000, n_samples),
            "NumOfProducts": np.random.randint(1, 4, n_samples),
            "HasCrCard": np.random.randint(0, 2, n_samples),
            "IsActiveMember": np.random.randint(0, 2, n_samples),
            "EstimatedSalary": np.random.uniform(0, 200000, n_samples),
            "Exited": np.random.randint(0, 2, n_samples),
        }
    )
    return data


@pytest.fixture
def sample_config():
    """Create a sample config."""
    config = BankChurnConfig(
        model=ModelConfig(
            type="ensemble",
            test_size=0.2,
            cv_folds=2,
            resampling_strategy="none",
            random_forest=RandomForestConfig(n_jobs=1),
        ),
        data=DataConfig(
            target_column="Exited",
            categorical_features=["Geography", "Gender"],
            numerical_features=[
                "CreditScore",
                "Age",
                "Tenure",
                "Balance",
                "NumOfProducts",
                "HasCrCard",
                "IsActiveMember",
                "EstimatedSalary",
            ],
            drop_columns=[],
        ),
        mlflow=MLflowConfig(enabled=False),
    )
    return config


def test_full_pipeline_flow(sample_data, sample_config, tmp_path):
    """Test complete flow: Train -> Save -> Load (New Format) -> Predict."""

    # 1. Train
    trainer = ChurnTrainer(sample_config)
    X, y = trainer.prepare_features(sample_data)

    # Run training
    model, metrics = trainer.train(X, y, use_cv=False)

    assert model is not None
    assert "train_f1" in metrics

    # 2. Save
    model_path = tmp_path / "model.pkl"
    # We pass None for preprocessor_path to indicate we don't care about separate file
    trainer.save_model(model_path, None)

    assert model_path.exists()

    # Verify it's a pipeline
    loaded_obj = joblib.load(model_path)
    assert isinstance(loaded_obj, Pipeline)
    assert "preprocessor" in loaded_obj.named_steps
    assert "classifier" in loaded_obj.named_steps

    # 3. Load using Predictor
    predictor = ChurnPredictor.from_files(model_path, None)

    # 4. Predict
    predictions = predictor.predict(X, include_proba=True)
    assert len(predictions) == len(X)
    assert "prediction" in predictions.columns
    assert "probability" in predictions.columns

    # 5. Load using Evaluator
    evaluator = ModelEvaluator.from_files(model_path, None)
    eval_metrics = evaluator.evaluate(X, y)
    assert "accuracy" in eval_metrics


def test_backward_compatibility(sample_data, sample_config, tmp_path):
    """Test backward compatibility for loading split files."""

    # 1. Create split files manually
    trainer = ChurnTrainer(sample_config)
    X, y = trainer.prepare_features(sample_data)
    trainer.train(X, y, use_cv=False)

    # Manually save split
    model_path = tmp_path / "legacy_model.pkl"
    prep_path = tmp_path / "legacy_prep.pkl"

    joblib.dump(trainer.model_, model_path)
    joblib.dump(trainer.preprocessor_, prep_path)

    # 2. Load using Predictor with both paths
    predictor = ChurnPredictor.from_files(model_path, prep_path)

    # 3. Predict
    predictions = predictor.predict(X)
    assert len(predictions) == len(X)
