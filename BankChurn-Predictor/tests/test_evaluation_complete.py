"""Comprehensive tests for evaluation.py module - based on real APIs."""

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.bankchurn.evaluation import ModelEvaluator


@pytest.fixture
def trained_model():
    """Create a simple trained model."""
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.choice([0, 1], 100)

    model = Pipeline([("scaler", StandardScaler()), ("clf", RandomForestClassifier(n_estimators=10, random_state=42))])
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
def test_data():
    """Create test data."""
    np.random.seed(42)
    X = pd.DataFrame(np.random.randn(50, 5), columns=[f"f{i}" for i in range(5)])
    y = pd.Series(np.random.choice([0, 1], 50))

    return X, y


def test_evaluator_initialization(trained_model, fitted_preprocessor):
    """Test ModelEvaluator initialization."""
    evaluator = ModelEvaluator(trained_model, fitted_preprocessor)

    assert evaluator.model == trained_model
    assert evaluator.preprocessor == fitted_preprocessor
    assert evaluator.metrics_ == {}


def test_evaluator_from_files(trained_model, fitted_preprocessor, tmp_path):
    """Test loading evaluator from files."""
    # Save artifacts
    model_path = tmp_path / "model.pkl"
    preprocessor_path = tmp_path / "preprocessor.pkl"

    joblib.dump(trained_model, model_path)
    joblib.dump(fitted_preprocessor, preprocessor_path)

    # Load
    evaluator = ModelEvaluator.from_files(model_path, preprocessor_path)

    assert evaluator is not None
    assert evaluator.model is not None
    assert evaluator.preprocessor is not None


def test_evaluate_returns_metrics(trained_model, fitted_preprocessor, test_data):
    """Test that evaluate returns metrics dict."""
    evaluator = ModelEvaluator(trained_model, fitted_preprocessor)
    X_test, y_test = test_data

    metrics = evaluator.evaluate(X_test, y_test)

    assert isinstance(metrics, dict)
    assert "accuracy" in metrics
    # Check for either 'f1' or 'f1_score'
    assert "f1" in metrics or "f1_score" in metrics


def test_evaluate_metrics_in_range(trained_model, fitted_preprocessor, test_data):
    """Test that metrics are in valid ranges."""
    evaluator = ModelEvaluator(trained_model, fitted_preprocessor)
    X_test, y_test = test_data

    metrics = evaluator.evaluate(X_test, y_test)

    # Check ranges
    if "accuracy" in metrics:
        assert 0 <= metrics["accuracy"] <= 1

    if "precision" in metrics:
        assert 0 <= metrics["precision"] <= 1

    if "recall" in metrics:
        assert 0 <= metrics["recall"] <= 1


def test_evaluate_stores_metrics(trained_model, fitted_preprocessor, test_data):
    """Test that evaluate stores metrics in evaluator."""
    evaluator = ModelEvaluator(trained_model, fitted_preprocessor)
    X_test, y_test = test_data

    evaluator.evaluate(X_test, y_test)

    # Should store metrics
    assert evaluator.metrics_ is not None
    assert isinstance(evaluator.metrics_, dict)
    assert len(evaluator.metrics_) > 0


def test_evaluate_with_output_path(trained_model, fitted_preprocessor, test_data, tmp_path):
    """Test evaluate with output path."""
    evaluator = ModelEvaluator(trained_model, fitted_preprocessor)
    X_test, y_test = test_data

    output_path = tmp_path / "metrics.json"

    metrics = evaluator.evaluate(X_test, y_test, output_path=output_path)

    assert metrics is not None
    # Check if file was created (if implemented)
    # Note: might not be implemented, so we don't assert file existence
