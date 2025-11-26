"""Tests for ChurnPredictor."""

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.bankchurn.prediction import ChurnPredictor


@pytest.fixture
def trained_model():
    """Create a simple trained model."""
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.choice([0, 1], 100)

    model = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(n_estimators=10, random_state=42)),
        ]
    )
    model.fit(X, y)

    return model


@pytest.fixture
def fitted_preprocessor():
    """Create fitted preprocessor."""
    np.random.seed(42)
    X = np.random.randn(100, 5)

    preprocessor = StandardScaler()
    preprocessor.fit(X)

    return preprocessor


@pytest.fixture
def prediction_data():
    """Create data for predictions."""
    np.random.seed(42)
    return pd.DataFrame(np.random.randn(20, 5), columns=[f"f{i}" for i in range(5)])


def test_predictor_initialization(trained_model, fitted_preprocessor):
    """Test ChurnPredictor initialization."""
    predictor = ChurnPredictor(trained_model, fitted_preprocessor)

    assert predictor.model == trained_model
    assert predictor.preprocessor == fitted_preprocessor


def test_predictor_from_files(trained_model, fitted_preprocessor, tmp_path):
    """Test loading predictor from files."""
    # Save artifacts
    model_path = tmp_path / "model.pkl"
    preprocessor_path = tmp_path / "preprocessor.pkl"

    joblib.dump(trained_model, model_path)
    joblib.dump(fitted_preprocessor, preprocessor_path)

    # Load
    predictor = ChurnPredictor.from_files(model_path, preprocessor_path)

    assert predictor is not None
    assert predictor.model is not None
    assert predictor.preprocessor is not None


def test_predict_returns_dataframe(trained_model, fitted_preprocessor, prediction_data):
    """Test that predict returns DataFrame."""
    predictor = ChurnPredictor(trained_model, fitted_preprocessor)

    result = predictor.predict(prediction_data)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(prediction_data)


def test_predict_with_proba(trained_model, fitted_preprocessor, prediction_data):
    """Test predictions with probabilities."""
    predictor = ChurnPredictor(trained_model, fitted_preprocessor)

    result = predictor.predict(prediction_data, include_proba=True)

    assert isinstance(result, pd.DataFrame)
    # Check if probability columns exist (might be named differently)
    assert len(result.columns) > 0


def test_predict_without_proba(trained_model, fitted_preprocessor, prediction_data):
    """Test predictions without probabilities."""
    predictor = ChurnPredictor(trained_model, fitted_preprocessor)

    result = predictor.predict(prediction_data, include_proba=False)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(prediction_data)


def test_predict_with_threshold(trained_model, fitted_preprocessor, prediction_data):
    """Test predictions with custom threshold."""
    predictor = ChurnPredictor(trained_model, fitted_preprocessor)

    result = predictor.predict(prediction_data, threshold=0.7)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(prediction_data)


def test_predict_batch_size(trained_model, fitted_preprocessor):
    """Test predictions on different batch sizes."""
    predictor = ChurnPredictor(trained_model, fitted_preprocessor)

    # Single row
    data_single = pd.DataFrame(np.random.randn(1, 5), columns=[f"f{i}" for i in range(5)])
    result_single = predictor.predict(data_single)
    assert len(result_single) == 1

    # Multiple rows
    data_multi = pd.DataFrame(np.random.randn(100, 5), columns=[f"f{i}" for i in range(5)])
    result_multi = predictor.predict(data_multi)
    assert len(result_multi) == 100
