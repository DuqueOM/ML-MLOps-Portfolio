"""Tests for advanced model implementations (XGBoost, LightGBM, PyTorch)."""

from __future__ import annotations

import numpy as np
import pytest
from sklearn.datasets import make_classification
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.bankchurn.models_advanced import build_model, get_available_models


@pytest.fixture
def binary_classification_data():
    """Generate synthetic binary classification data similar to churn."""
    X, y = make_classification(
        n_samples=500,
        n_features=10,
        n_informative=6,
        n_redundant=2,
        weights=[0.8, 0.2],
        random_state=42,
    )
    return X, y


class TestModelFactory:
    """Tests for the build_model factory function."""

    def test_build_logistic_regression(self):
        model = build_model("logistic_regression", seed=42)
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")

    def test_build_random_forest(self):
        model = build_model("random_forest", seed=42)
        assert hasattr(model, "fit")
        assert hasattr(model, "predict_proba")

    def test_build_mlp(self):
        model = build_model("mlp", seed=42)
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")
        assert hasattr(model, "predict_proba")

    def test_build_ensemble(self):
        model = build_model("ensemble", seed=42)
        assert hasattr(model, "fit")

    def test_build_unknown_model_raises(self):
        with pytest.raises(ValueError, match="Unknown model"):
            build_model("nonexistent_model")

    def test_build_with_custom_params(self):
        model = build_model("random_forest", params={"n_estimators": 50, "max_depth": 3}, seed=42)
        assert model.n_estimators == 50
        assert model.max_depth == 3

    def test_available_models_returns_dict(self):
        available = get_available_models()
        assert isinstance(available, dict)
        assert "logistic_regression" in available
        assert "random_forest" in available
        assert available["logistic_regression"] is True


class TestSklearnModels:
    """Test sklearn-based models fit/predict correctly."""

    def test_logistic_regression_fit_predict(self, binary_classification_data):
        X, y = binary_classification_data
        model = build_model("logistic_regression", seed=42)
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == y.shape
        assert set(np.unique(preds)).issubset({0, 1})

    def test_random_forest_fit_predict(self, binary_classification_data):
        X, y = binary_classification_data
        model = build_model("random_forest", seed=42)
        model.fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (len(y), 2)
        assert np.allclose(proba.sum(axis=1), 1.0)

    def test_mlp_fit_predict(self, binary_classification_data):
        X, y = binary_classification_data
        model = build_model(
            "mlp",
            params={"hidden_layer_sizes": (32, 16), "max_iter": 150},
            seed=42,
        )
        model.fit(X, y)
        preds = model.predict(X)
        proba = model.predict_proba(X)
        assert preds.shape == y.shape
        assert proba.shape == (len(y), 2)

    def test_ensemble_fit_predict(self, binary_classification_data):
        X, y = binary_classification_data
        model = build_model("ensemble", seed=42)
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == y.shape

    def test_model_in_pipeline(self, binary_classification_data):
        X, y = binary_classification_data
        model = build_model("random_forest", seed=42)
        pipe = Pipeline([("scaler", StandardScaler()), ("clf", model)])
        pipe.fit(X, y)
        preds = pipe.predict(X)
        assert preds.shape == y.shape


class TestXGBoost:
    """Tests for XGBoost classifier (skipped if not installed)."""

    @pytest.fixture(autouse=True)
    def check_xgboost(self):
        available = get_available_models()
        if not available.get("xgboost"):
            pytest.skip("xgboost not installed")

    def test_build_xgboost(self):
        model = build_model("xgboost", seed=42)
        assert hasattr(model, "fit")

    def test_xgboost_fit_predict(self, binary_classification_data):
        X, y = binary_classification_data
        model = build_model("xgboost", seed=42)
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == y.shape
        proba = model.predict_proba(X)
        assert proba.shape == (len(y), 2)

    def test_xgboost_custom_params(self, binary_classification_data):
        X, y = binary_classification_data
        model = build_model("xgboost", params={"n_estimators": 10, "max_depth": 3}, seed=42)
        model.fit(X, y)
        preds = model.predict(X)
        assert len(preds) == len(y)


class TestLightGBM:
    """Tests for LightGBM classifier (skipped if not installed)."""

    @pytest.fixture(autouse=True)
    def check_lightgbm(self):
        available = get_available_models()
        if not available.get("lightgbm"):
            pytest.skip("lightgbm not installed")

    def test_build_lightgbm(self):
        model = build_model("lightgbm", seed=42)
        assert hasattr(model, "fit")

    def test_lightgbm_fit_predict(self, binary_classification_data):
        X, y = binary_classification_data
        model = build_model("lightgbm", seed=42)
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == y.shape
        proba = model.predict_proba(X)
        assert proba.shape == (len(y), 2)


class TestNeuralNetwork:
    """Tests for PyTorch TabularNet classifier (skipped if not installed)."""

    @pytest.fixture(autouse=True)
    def check_torch(self):
        available = get_available_models()
        if not available.get("neural_network"):
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
            params={"epochs": 5, "hidden_dims": [32, 16], "verbose": False},
            seed=42,
        )
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == y.shape
        assert set(np.unique(preds)).issubset({0, 1})

    def test_neural_network_predict_proba(self, binary_classification_data):
        X, y = binary_classification_data
        model = build_model(
            "neural_network",
            params={"epochs": 5, "hidden_dims": [32, 16], "verbose": False},
            seed=42,
        )
        model.fit(X, y)
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

    def test_neural_network_not_fitted_raises(self):
        model = build_model("neural_network", seed=42)
        with pytest.raises(RuntimeError, match="not fitted"):
            model.predict(np.zeros((5, 10)))
