"""Tests for advanced model implementations (XGBoost, LightGBM, PyTorch) for CarVision.

Covers:
- Model factory: build_model() for all supported model types.
- Sklearn models: RandomForest, MLP fit/predict with synthetic data.
- XGBoost/LightGBM: fit/predict (skipped if not installed).
- PyTorch neural network: TorchTabularRegressor fit/predict (skipped if not installed).
- ImportError guards: verifies graceful failure when optional deps are unavailable.
- Pipeline integration: models work inside sklearn Pipeline.
"""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest
from sklearn.datasets import make_regression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.carvision.models_advanced import (
    build_lightgbm_regressor,
    build_model,
    build_xgboost_regressor,
    get_available_models,
)


@pytest.fixture
def regression_data():
    """Generate synthetic regression data similar to vehicle pricing."""
    X, y = make_regression(
        n_samples=500,
        n_features=10,
        n_informative=6,
        noise=10.0,
        random_state=42,
    )
    y = np.abs(y) + 1000  # Ensure positive prices
    return X, y


class TestModelFactory:
    def test_build_random_forest(self):
        model = build_model("random_forest", seed=42)
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")

    def test_build_mlp(self):
        model = build_model("mlp", seed=42)
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")

    def test_build_unknown_model_raises(self):
        with pytest.raises(ValueError, match="Unknown model"):
            build_model("nonexistent_model")

    def test_available_models(self):
        available = get_available_models()
        assert isinstance(available, dict)
        assert available["random_forest"] is True


class TestSklearnModels:
    def test_random_forest_fit_predict(self, regression_data):
        X, y = regression_data
        model = build_model("random_forest", params={"n_estimators": 10}, seed=42)
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == y.shape
        assert np.all(np.isfinite(preds))

    def test_mlp_fit_predict(self, regression_data):
        X, y = regression_data
        model = build_model(
            "mlp",
            params={"hidden_layer_sizes": (32, 16), "max_iter": 150},
            seed=42,
        )
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == y.shape
        assert np.all(np.isfinite(preds))

    def test_model_in_pipeline(self, regression_data):
        X, y = regression_data
        model = build_model("random_forest", params={"n_estimators": 10}, seed=42)
        pipe = Pipeline([("scaler", StandardScaler()), ("model", model)])
        pipe.fit(X, y)
        preds = pipe.predict(X)
        assert preds.shape == y.shape


class TestXGBoost:
    @pytest.fixture(autouse=True)
    def check_xgboost(self):
        if not get_available_models().get("xgboost"):
            pytest.skip("xgboost not installed")

    def test_xgboost_fit_predict(self, regression_data):
        X, y = regression_data
        model = build_model("xgboost", params={"n_estimators": 10}, seed=42)
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == y.shape


class TestLightGBM:
    @pytest.fixture(autouse=True)
    def check_lightgbm(self):
        if not get_available_models().get("lightgbm"):
            pytest.skip("lightgbm not installed")

    def test_lightgbm_fit_predict(self, regression_data):
        X, y = regression_data
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

    def test_neural_network_fit_predict(self, regression_data):
        X, y = regression_data
        model = build_model(
            "neural_network",
            params={"epochs": 5, "hidden_dims": [32, 16], "verbose": False},
            seed=42,
        )
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == y.shape
        assert np.all(np.isfinite(preds))

    def test_neural_network_in_pipeline(self, regression_data):
        X, y = regression_data
        model = build_model(
            "neural_network",
            params={"epochs": 3, "hidden_dims": [16, 8], "verbose": False},
            seed=42,
        )
        pipe = Pipeline([("scaler", StandardScaler()), ("model", model)])
        pipe.fit(X, y)
        preds = pipe.predict(X)
        assert preds.shape == y.shape


class TestImportErrorGuards:
    """Verify graceful ImportError when optional dependencies are unavailable.

    Each test mocks the availability flag to False and asserts that the
    corresponding builder raises ImportError with a helpful message.
    """

    def test_xgboost_unavailable_raises(self):
        """build_xgboost_regressor raises ImportError when xgboost is missing."""
        with patch("src.carvision.models_advanced.XGBOOST_AVAILABLE", False):
            with pytest.raises(ImportError, match="xgboost"):
                build_xgboost_regressor()

    def test_lightgbm_unavailable_raises(self):
        """build_lightgbm_regressor raises ImportError when lightgbm is missing."""
        with patch("src.carvision.models_advanced.LIGHTGBM_AVAILABLE", False):
            with pytest.raises(ImportError, match="lightgbm"):
                build_lightgbm_regressor()

    def test_neural_network_unavailable_raises(self):
        """build_model('neural_network') raises ImportError when torch is missing."""
        with patch("src.carvision.models_advanced.TORCH_AVAILABLE", False):
            with pytest.raises(ImportError, match="torch"):
                build_model("neural_network")
