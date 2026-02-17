"""Tests for advanced model implementations (XGBoost, LightGBM, PyTorch) for TelecomAI."""

from __future__ import annotations

import numpy as np
import pytest
from sklearn.datasets import make_classification
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.telecom.models_advanced import build_model, get_available_models


@pytest.fixture
def binary_classification_data():
    """Generate synthetic binary classification data similar to telecom plan."""
    X, y = make_classification(
        n_samples=300,
        n_features=4,
        n_informative=3,
        n_redundant=0,
        weights=[0.7, 0.3],
        random_state=42,
    )
    return X, y


class TestModelFactory:
    def test_build_gradient_boosting(self):
        model = build_model("gradient_boosting", seed=42)
        assert hasattr(model, "fit")

    def test_build_random_forest(self):
        model = build_model("random_forest", seed=42)
        assert hasattr(model, "fit")

    def test_build_logistic_regression(self):
        model = build_model("logistic_regression", seed=42)
        assert hasattr(model, "fit")

    def test_build_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown model"):
            build_model("nonexistent")

    def test_available_models(self):
        available = get_available_models()
        assert isinstance(available, dict)
        assert available["gradient_boosting"] is True
        assert available["random_forest"] is True


class TestSklearnModels:
    def test_gradient_boosting_fit_predict(self, binary_classification_data):
        X, y = binary_classification_data
        model = build_model("gradient_boosting", params={"n_estimators": 10}, seed=42)
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == y.shape

    def test_random_forest_fit_predict(self, binary_classification_data):
        X, y = binary_classification_data
        model = build_model("random_forest", params={"n_estimators": 10}, seed=42)
        model.fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (len(y), 2)


class TestXGBoost:
    @pytest.fixture(autouse=True)
    def check_xgboost(self):
        if not get_available_models().get("xgboost"):
            pytest.skip("xgboost not installed")

    def test_xgboost_fit_predict(self, binary_classification_data):
        X, y = binary_classification_data
        model = build_model("xgboost", params={"n_estimators": 10}, seed=42)
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == y.shape
        proba = model.predict_proba(X)
        assert proba.shape == (len(y), 2)


class TestLightGBM:
    @pytest.fixture(autouse=True)
    def check_lightgbm(self):
        if not get_available_models().get("lightgbm"):
            pytest.skip("lightgbm not installed")

    def test_lightgbm_fit_predict(self, binary_classification_data):
        X, y = binary_classification_data
        model = build_model("lightgbm", params={"n_estimators": 10}, seed=42)
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == y.shape


class TestNeuralNetwork:
    @pytest.fixture(autouse=True)
    def check_torch(self):
        if not get_available_models().get("neural_network"):
            pytest.skip("torch not installed")

    def test_build_neural_network(self):
        model = build_model("neural_network", seed=42)
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")
        assert hasattr(model, "predict_proba")

    def test_neural_network_fit_predict(self, binary_classification_data):
        X, y = binary_classification_data
        model = build_model(
            "neural_network",
            params={"epochs": 5, "hidden_dims": [16, 8], "verbose": False},
            seed=42,
        )
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == y.shape
        proba = model.predict_proba(X)
        assert proba.shape == (len(y), 2)
        assert np.allclose(proba.sum(axis=1), 1.0, atol=1e-5)

    def test_neural_network_in_pipeline(self, binary_classification_data):
        X, y = binary_classification_data
        model = build_model(
            "neural_network",
            params={"epochs": 3, "hidden_dims": [16, 8], "verbose": False},
            seed=42,
        )
        pipe = Pipeline([("scaler", StandardScaler()), ("clf", model)])
        pipe.fit(X, y)
        preds = pipe.predict(X)
        assert preds.shape == y.shape
