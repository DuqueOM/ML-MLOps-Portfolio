"""
Tests for the ModelExplainer class.

Tests cover both SHAP-based explanations (when available) and fallback modes.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.bankchurn.explainability import SHAP_AVAILABLE, ModelExplainer


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    np.random.seed(42)
    X = pd.DataFrame(
        {
            "Age": np.random.randint(18, 70, 100),
            "Balance": np.random.uniform(0, 200000, 100),
            "NumOfProducts": np.random.randint(1, 5, 100),
            "IsActiveMember": np.random.randint(0, 2, 100),
            "Geography": np.random.choice(["France", "Germany", "Spain"], 100),
        }
    )
    y = np.random.randint(0, 2, 100)
    return X, y


@pytest.fixture
def simple_model(sample_data):
    """Create a simple model for testing."""
    X, y = sample_data
    # Use only numeric columns
    X_numeric = X[["Age", "Balance", "NumOfProducts", "IsActiveMember"]]
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_numeric, y)
    return model, X_numeric


@pytest.fixture
def pipeline_model(sample_data):
    """Create a pipeline model for testing."""
    X, y = sample_data
    X_numeric = X[["Age", "Balance", "NumOfProducts", "IsActiveMember"]]
    pipeline = Pipeline(
        [
            ("preprocessor", StandardScaler()),
            ("classifier", RandomForestClassifier(n_estimators=10, random_state=42)),
        ]
    )
    pipeline.fit(X_numeric, y)
    return pipeline, X_numeric


class TestModelExplainerInitialization:
    """Tests for ModelExplainer initialization."""

    def test_init_without_background_data(self, simple_model):
        """Test initialization without background data."""
        model, _ = simple_model
        explainer = ModelExplainer(model)
        assert explainer.model is model
        assert explainer.explainer is None
        assert explainer.feature_names is None

    def test_init_with_feature_names(self, simple_model):
        """Test initialization with explicit feature names."""
        model, X = simple_model
        feature_names = ["f1", "f2", "f3", "f4"]
        explainer = ModelExplainer(model, feature_names=feature_names)
        assert explainer.feature_names == feature_names

    def test_init_samples_large_background(self, simple_model):
        """Test that large background data is sampled."""
        model, X = simple_model
        # Create larger dataset
        large_X = pd.concat([X] * 5, ignore_index=True)  # 500 samples
        explainer = ModelExplainer(model, X_background=large_X, max_background_samples=50)
        # Feature names should be inferred
        assert explainer.feature_names == list(X.columns)


class TestFallbackMethods:
    """Tests for fallback methods when SHAP is not available."""

    def test_fallback_feature_importance_rf(self, simple_model):
        """Test fallback importance for RandomForest."""
        model, X = simple_model
        explainer = ModelExplainer(model, feature_names=list(X.columns))
        importance = explainer._fallback_feature_importance()

        assert isinstance(importance, dict)
        assert len(importance) == len(X.columns)
        assert all(isinstance(v, (int, float, np.floating)) for v in importance.values())

    def test_fallback_feature_importance_lr(self, sample_data):
        """Test fallback importance for LogisticRegression."""
        X, y = sample_data
        X_numeric = X[["Age", "Balance", "NumOfProducts", "IsActiveMember"]]
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_numeric, y)

        explainer = ModelExplainer(model, feature_names=list(X_numeric.columns))
        importance = explainer._fallback_feature_importance()

        assert isinstance(importance, dict)
        assert len(importance) == len(X_numeric.columns)

    def test_fallback_feature_importance_no_model_attrs(self):
        """Test fallback when model has no importance attributes."""

        # Create a simple class without feature_importances_ or coef_
        class DummyModel:
            pass

        dummy_model = DummyModel()
        explainer = ModelExplainer(dummy_model)
        importance = explainer._fallback_feature_importance()

        assert importance == {"no_importance_available": 1.0}

    def test_fallback_contributions(self, simple_model):
        """Test fallback contributions calculation."""
        model, X = simple_model
        explainer = ModelExplainer(model)

        # Create single sample
        X_single = pd.DataFrame(
            [
                {
                    "Age": 55,
                    "Balance": 100000,
                    "NumOfProducts": 1,
                    "IsActiveMember": 0,
                }
            ]
        )

        contributions = explainer._fallback_contributions(X_single)

        assert isinstance(contributions, dict)
        assert "Age" in contributions
        assert contributions["Age"] == 0.15  # Age > 50
        assert contributions["IsActiveMember"] == 0.18  # Inactive

    def test_fallback_contributions_germany(self, simple_model):
        """Test fallback contributions for Germany customer."""
        model, _ = simple_model
        explainer = ModelExplainer(model)

        X_single = pd.DataFrame(
            [
                {
                    "Age": 30,
                    "Geography": "Germany",
                    "NumOfProducts": 2,
                    "IsActiveMember": 1,
                }
            ]
        )

        contributions = explainer._fallback_contributions(X_single)
        assert contributions["Geography"] == 0.14


class TestGetFeatureImportance:
    """Tests for get_feature_importance method."""

    def test_get_importance_no_shap(self, simple_model):
        """Test feature importance without SHAP (uses fallback)."""
        model, X = simple_model
        explainer = ModelExplainer(model, feature_names=list(X.columns))
        # Ensure no SHAP explainer
        explainer.explainer = None

        importance = explainer.get_feature_importance()

        assert isinstance(importance, dict)
        assert len(importance) <= 10  # top_n default

    def test_get_importance_with_top_n(self, simple_model):
        """Test limiting number of returned features."""
        model, X = simple_model
        explainer = ModelExplainer(model, feature_names=list(X.columns))
        explainer.explainer = None

        importance = explainer.get_feature_importance(top_n=2)

        assert len(importance) <= 2


class TestExplainPrediction:
    """Tests for explain_prediction method."""

    def test_explain_prediction_dict_input(self, simple_model):
        """Test prediction explanation with dict input."""
        model, X = simple_model
        explainer = ModelExplainer(model, feature_names=list(X.columns))
        explainer.explainer = None  # Force fallback

        sample = {
            "Age": 45,
            "Balance": 80000,
            "NumOfProducts": 2,
            "IsActiveMember": 1,
        }

        result = explainer.explain_prediction(sample)

        assert "prediction" in result
        assert "probability" in result
        assert "base_value" in result
        assert "feature_contributions" in result
        assert "explanation_type" in result
        assert result["explanation_type"] == "fallback"
        assert result["prediction"] in [0, 1]
        assert 0 <= result["probability"] <= 1

    def test_explain_prediction_dataframe_input(self, simple_model):
        """Test prediction explanation with DataFrame input."""
        model, X = simple_model
        explainer = ModelExplainer(model, feature_names=list(X.columns))
        explainer.explainer = None

        X_single = X.iloc[[0]]
        result = explainer.explain_prediction(X_single)

        assert "prediction" in result
        assert "probability" in result
        assert result["explanation_type"] == "fallback"

    def test_explain_prediction_top_features(self, simple_model):
        """Test that top positive/negative features are returned."""
        model, X = simple_model
        explainer = ModelExplainer(model, feature_names=list(X.columns))
        explainer.explainer = None

        sample = {
            "Age": 60,  # High age -> positive contribution
            "Balance": 80000,
            "NumOfProducts": 1,  # Single product -> positive
            "IsActiveMember": 0,  # Inactive -> positive
        }

        result = explainer.explain_prediction(sample)

        assert "top_positive" in result
        assert "top_negative" in result
        assert isinstance(result["top_positive"], list)
        assert isinstance(result["top_negative"], list)


class TestPipelineModel:
    """Tests for pipeline-based models."""

    def test_fallback_importance_pipeline(self, pipeline_model):
        """Test fallback importance with pipeline model."""
        pipeline, X = pipeline_model
        explainer = ModelExplainer(pipeline, feature_names=list(X.columns))

        importance = explainer._fallback_feature_importance()

        assert isinstance(importance, dict)
        # Pipeline should extract classifier's feature_importances_
        assert len(importance) == len(X.columns)

    def test_explain_prediction_pipeline(self, pipeline_model):
        """Test prediction explanation with pipeline model."""
        pipeline, X = pipeline_model
        explainer = ModelExplainer(pipeline, feature_names=list(X.columns))
        explainer.explainer = None

        sample = X.iloc[[0]].to_dict("records")[0]
        result = explainer.explain_prediction(sample)

        assert "prediction" in result
        assert result["explanation_type"] == "fallback"


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_feature_names(self, simple_model):
        """Test with no feature names provided."""
        model, X = simple_model
        explainer = ModelExplainer(model)
        explainer.explainer = None

        importance = explainer._fallback_feature_importance()

        # Should use generic feature names
        assert all(k.startswith("feature_") for k in importance.keys())

    def test_exception_in_fallback(self):
        """Test graceful handling of exceptions in fallback."""

        class DummyModel:
            @property
            def feature_importances_(self):  # pragma: no cover - only used to trigger exception
                raise ValueError("boom")

        dummy_model = DummyModel()
        explainer = ModelExplainer(dummy_model)

        importance = explainer._fallback_feature_importance()
        assert importance == {"no_importance_available": 1.0}


# Test SHAP availability flag
def test_shap_availability_flag():
    """Test that SHAP_AVAILABLE is properly set."""
    assert isinstance(SHAP_AVAILABLE, bool)
