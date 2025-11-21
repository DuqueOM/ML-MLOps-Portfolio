"""Specific tests for training.py uncovered lines."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.bankchurn.config import BankChurnConfig
from src.bankchurn.training import ChurnTrainer


@pytest.fixture
def config():
    """Load config."""
    config_path = Path(__file__).parent.parent / "configs" / "config.yaml"
    return BankChurnConfig.from_yaml(config_path)


@pytest.fixture
def full_sample_data():
    """Create full realistic sample data."""
    np.random.seed(42)
    n = 200

    return pd.DataFrame(
        {
            "RowNumber": range(1, n + 1),
            "CustomerId": range(10000, 10000 + n),
            "Surname": [f"Name{i}" for i in range(n)],
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


def test_full_training_workflow(config, full_sample_data, tmp_path):
    """Test complete training workflow from start to finish."""
    # Save data
    data_path = tmp_path / "data.csv"
    full_sample_data.to_csv(data_path, index=False)

    # Initialize trainer
    trainer = ChurnTrainer(config, random_state=42)

    # Load data
    data = trainer.load_data(data_path)
    assert len(data) > 0

    # Prepare features
    X, y = trainer.prepare_features(data)
    assert len(X) == len(y)

    # Build preprocessor
    preprocessor = trainer.build_preprocessor(X)
    assert preprocessor is not None

    # Fit preprocessor
    X_transformed = preprocessor.fit_transform(X)
    assert X_transformed.shape[0] == len(X)

    # Build model
    model = trainer.build_model()
    assert model is not None

    # Train model
    model.fit(X_transformed, y)

    # Make predictions
    predictions = model.predict(X_transformed)
    assert len(predictions) == len(y)

    # Store in trainer
    trainer.model_ = model
    trainer.preprocessor_ = preprocessor

    # Save model
    model_path = tmp_path / "model.pkl"
    prep_path = tmp_path / "prep.pkl"
    trainer.save_model(model_path, prep_path)

    assert model_path.exists()
    assert prep_path.exists()


def test_trainer_with_drop_columns(config, full_sample_data):
    """Test that trainer properly drops specified columns."""
    trainer = ChurnTrainer(config)

    X, y = trainer.prepare_features(full_sample_data)

    # Check drop columns worked
    drop_cols = config.data.drop_columns if config.data.drop_columns else []
    for col in drop_cols:
        assert col not in X.columns


def test_preprocessor_with_categorical_features(config):
    """Test preprocessor handles categorical features correctly."""
    trainer = ChurnTrainer(config)

    # Create data with known categorical features
    X = pd.DataFrame(
        {
            "cat1": ["A", "B", "C", "A", "B"],
            "cat2": ["X", "Y", "X", "Y", "X"],
            "num1": [1.0, 2.0, 3.0, 4.0, 5.0],
            "num2": [10, 20, 30, 40, 50],
        }
    )

    preprocessor = trainer.build_preprocessor(X)
    X_transformed = preprocessor.fit_transform(X)

    # Should have transformed features
    assert X_transformed.shape[0] == 5
    assert X_transformed.shape[1] > 0


def test_preprocessor_with_numerical_only(config):
    """Test preprocessor with only numerical features."""
    trainer = ChurnTrainer(config)

    X = pd.DataFrame({"num1": [1.0, 2.0, 3.0], "num2": [10.0, 20.0, 30.0], "num3": [100.0, 200.0, 300.0]})

    preprocessor = trainer.build_preprocessor(X)
    X_transformed = preprocessor.fit_transform(X)

    assert X_transformed.shape[0] == 3


def test_model_prediction_shape(config, full_sample_data):
    """Test that model predictions have correct shape."""
    trainer = ChurnTrainer(config, random_state=42)

    X, y = trainer.prepare_features(full_sample_data)

    preprocessor = trainer.build_preprocessor(X)
    model = trainer.build_model()

    X_transformed = preprocessor.fit_transform(X)
    model.fit(X_transformed, y)

    # Test predict
    predictions = model.predict(X_transformed[:10])
    assert len(predictions) == 10

    # Test predict_proba
    probas = model.predict_proba(X_transformed[:10])
    assert probas.shape == (10, 2)


def test_trainer_handles_empty_drop_columns(config, full_sample_data):
    """Test trainer when no columns need to be dropped."""
    trainer = ChurnTrainer(config)

    # Even if drop_columns is empty, should work
    X, y = trainer.prepare_features(full_sample_data)

    assert len(X) == len(full_sample_data)
    assert "Exited" not in X.columns


def test_save_model_creates_files(config, full_sample_data, tmp_path):
    """Test that save_model actually creates the files."""
    trainer = ChurnTrainer(config, random_state=42)

    X, y = trainer.prepare_features(full_sample_data)
    preprocessor = trainer.build_preprocessor(X)
    model = trainer.build_model()

    X_transformed = preprocessor.fit_transform(X)
    model.fit(X_transformed, y)

    trainer.model_ = model
    trainer.preprocessor_ = preprocessor

    # Save with different names
    m_path = tmp_path / "my_model.pkl"
    p_path = tmp_path / "my_prep.pkl"

    trainer.save_model(m_path, p_path)

    assert m_path.exists()
    assert p_path.exists()
    assert m_path.stat().st_size > 1000  # Should be reasonably large
    assert p_path.stat().st_size > 100
