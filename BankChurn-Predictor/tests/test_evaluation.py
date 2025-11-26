"""Tests for ModelEvaluator."""

from unittest.mock import MagicMock

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
    assert output_path.exists()


@pytest.fixture
def mock_evaluator():
    model = MagicMock()
    preprocessor = MagicMock()

    model.predict.return_value = np.array([0, 1, 0, 1])
    model.predict_proba.return_value = np.array([[0.8, 0.2], [0.3, 0.7], [0.9, 0.1], [0.4, 0.6]])

    # Mock pipeline behavior
    preprocessor.transform.return_value = np.random.rand(4, 5)

    return ModelEvaluator(model, preprocessor)


def test_evaluate_metrics_mock(mock_evaluator):
    X = pd.DataFrame({"A": [1, 2, 3, 4]})
    y = pd.Series([0, 1, 0, 1])

    metrics = mock_evaluator.evaluate(X, y)

    assert "accuracy" in metrics
    assert "f1" in metrics
    assert "roc_auc" in metrics
    assert metrics["accuracy"] == 1.0


def test_fairness_metrics(mock_evaluator):
    X = pd.DataFrame({"A": [1, 2, 3, 4], "Gender": ["Male", "Female", "Male", "Female"]})
    y = pd.Series([0, 1, 0, 1])

    metrics = mock_evaluator.compute_fairness_metrics(X, y, ["Gender"])

    assert "Gender" in metrics
    assert "disparate_impact" in metrics["Gender"]


def test_save_results_private(mock_evaluator, tmp_path):
    mock_evaluator.metrics_ = {"acc": 0.9}
    path = tmp_path / "results.json"
    mock_evaluator._save_results(path)
    assert path.exists()
