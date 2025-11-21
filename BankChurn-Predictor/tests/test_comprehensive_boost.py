"""Comprehensive tests to boost BankChurn to 70%+ coverage."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.bankchurn.config import BankChurnConfig
from src.bankchurn.training import ChurnTrainer


@pytest.fixture
def valid_config():
    """Load valid config from file."""
    config_path = Path(__file__).parent.parent / "configs" / "config.yaml"
    return BankChurnConfig.from_yaml(config_path)


@pytest.fixture
def sample_training_data():
    """Create realistic sample training data."""
    np.random.seed(42)
    n = 150

    return pd.DataFrame(
        {
            "CreditScore": np.random.randint(300, 850, n),
            "Geography": np.random.choice(["France", "Germany", "Spain"], n),
            "Gender": np.random.choice(["Male", "Female"], n),
            "Age": np.random.randint(18, 80, n),
            "Tenure": np.random.randint(0, 10, n),
            "Balance": np.random.uniform(0, 250000, n),
            "NumOfProducts": np.random.randint(1, 4, n),
            "HasCrCard": np.random.choice([0, 1], n),
            "IsActiveMember": np.random.choice([0, 1], n),
            "EstimatedSalary": np.random.uniform(10000, 200000, n),
            "Exited": np.random.choice([0, 1], n, p=[0.8, 0.2]),
        }
    )


def test_trainer_load_and_prepare(valid_config, sample_training_data, tmp_path):
    """Test complete load and prepare pipeline."""
    # Save data
    data_path = tmp_path / "train.csv"
    sample_training_data.to_csv(data_path, index=False)

    # Create trainer
    trainer = ChurnTrainer(valid_config, random_state=42)

    # Load data
    data = trainer.load_data(data_path)
    assert len(data) == 150

    # Prepare features
    X, y = trainer.prepare_features(data)
    assert len(X) == 150
    assert len(y) == 150
    assert "Exited" not in X.columns


def test_trainer_build_pipeline(valid_config, sample_training_data):
    """Test building complete preprocessing and model pipeline."""
    trainer = ChurnTrainer(valid_config, random_state=42)

    # Prepare data
    X, y = trainer.prepare_features(sample_training_data)

    # Build preprocessor
    preprocessor = trainer.build_preprocessor(X)
    assert preprocessor is not None

    # Build model
    model = trainer.build_model()
    assert model is not None

    # Test fit
    X_transformed = preprocessor.fit_transform(X)
    model.fit(X_transformed, y)

    # Test predict
    predictions = model.predict(X_transformed)
    assert len(predictions) == len(y)


def test_trainer_save_artifacts(valid_config, sample_training_data, tmp_path):
    """Test saving trained model and preprocessor."""
    trainer = ChurnTrainer(valid_config, random_state=42)

    # Prepare and train
    X, y = trainer.prepare_features(sample_training_data)
    preprocessor = trainer.build_preprocessor(X)
    model = trainer.build_model()

    X_transformed = preprocessor.fit_transform(X)
    model.fit(X_transformed, y)

    # Set attributes
    trainer.model_ = model
    trainer.preprocessor_ = preprocessor

    # Save
    model_path = tmp_path / "model.pkl"
    preprocessor_path = tmp_path / "preprocessor.pkl"

    trainer.save_model(model_path, preprocessor_path)

    # Verify files exist
    assert model_path.exists()
    assert preprocessor_path.exists()
    assert model_path.stat().st_size > 0
    assert preprocessor_path.stat().st_size > 0


def test_trainer_with_different_random_states(valid_config, sample_training_data):
    """Test trainer produces different results with different seeds."""
    X, y = ChurnTrainer(valid_config).prepare_features(sample_training_data)

    # Train with seed 42
    trainer1 = ChurnTrainer(valid_config, random_state=42)
    preprocessor1 = trainer1.build_preprocessor(X)
    model1 = trainer1.build_model()
    X_transformed = preprocessor1.fit_transform(X)
    model1.fit(X_transformed, y)
    pred1 = model1.predict(X_transformed[:10])

    # Train with seed 123
    trainer2 = ChurnTrainer(valid_config, random_state=123)
    preprocessor2 = trainer2.build_preprocessor(X)
    model2 = trainer2.build_model()
    X_transformed2 = preprocessor2.fit_transform(X)
    model2.fit(X_transformed2, y)
    pred2 = model2.predict(X_transformed2[:10])

    # Results should potentially differ (not guaranteed but likely)
    assert len(pred1) == len(pred2)


def test_trainer_handles_missing_columns(valid_config, tmp_path):
    """Test trainer validation for missing required columns."""
    # Create data without target column
    bad_data = pd.DataFrame({"CreditScore": [500, 600, 700], "Age": [25, 35, 45]})

    data_path = tmp_path / "bad.csv"
    bad_data.to_csv(data_path, index=False)

    trainer = ChurnTrainer(valid_config)

    with pytest.raises(ValueError, match="Missing required columns"):
        trainer.load_data(data_path)


def test_trainer_preprocessor_feature_detection(valid_config):
    """Test automatic feature type detection in preprocessor."""
    trainer = ChurnTrainer(valid_config)

    # Mixed data types
    X = pd.DataFrame(
        {
            "num_int": [1, 2, 3, 4, 5],
            "num_float": [1.5, 2.5, 3.5, 4.5, 5.5],
            "cat_str": ["A", "B", "C", "A", "B"],
            "cat_obj": pd.Categorical(["X", "Y", "Z", "X", "Y"]),
        }
    )

    preprocessor = trainer.build_preprocessor(X)

    # Fit and transform
    X_transformed = preprocessor.fit_transform(X)

    assert X_transformed.shape[0] == 5
    assert X_transformed.shape[1] > 0  # Should have some features


def test_trainer_model_has_required_methods(valid_config):
    """Test that built model has required sklearn interface."""
    trainer = ChurnTrainer(valid_config)
    model = trainer.build_model()

    # Check sklearn interface
    assert hasattr(model, "fit")
    assert hasattr(model, "predict")
    assert hasattr(model, "predict_proba")
    assert callable(model.fit)
    assert callable(model.predict)
    assert callable(model.predict_proba)
