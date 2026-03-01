"""Tests for ChurnFeatureEngineer."""

import numpy as np
import pandas as pd
import pytest

from src.bankchurn.features import ChurnFeatureEngineer


@pytest.fixture
def sample_data():
    """Create realistic sample data matching BankChurn schema."""
    np.random.seed(42)
    n = 100
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
        }
    )


class TestChurnFeatureEngineer:
    """Tests for ChurnFeatureEngineer transformer."""

    def test_fit_returns_self(self, sample_data):
        fe = ChurnFeatureEngineer()
        result = fe.fit(sample_data)
        assert result is fe

    def test_transform_adds_columns(self, sample_data):
        fe = ChurnFeatureEngineer()
        result = fe.fit_transform(sample_data)
        assert result.shape[1] > sample_data.shape[1]

    def test_original_columns_preserved(self, sample_data):
        fe = ChurnFeatureEngineer()
        result = fe.fit_transform(sample_data)
        for col in sample_data.columns:
            assert col in result.columns

    def test_no_nans_in_engineered_features(self, sample_data):
        fe = ChurnFeatureEngineer()
        result = fe.fit_transform(sample_data)
        new_cols = [c for c in result.columns if c not in sample_data.columns]
        for col in new_cols:
            assert result[col].isna().sum() == 0, f"NaN found in {col}"

    def test_interactions_created(self, sample_data):
        fe = ChurnFeatureEngineer(
            create_interactions=True,
            create_ratios=False,
            create_bins=False,
            create_risk_scores=False,
        )
        result = fe.fit_transform(sample_data)
        assert "Age_x_NumProducts" in result.columns
        assert "Balance_x_Active" in result.columns
        assert "CreditScore_x_Tenure" in result.columns
        assert "Age_x_Active" in result.columns

    def test_ratios_created(self, sample_data):
        fe = ChurnFeatureEngineer(
            create_interactions=False,
            create_ratios=True,
            create_bins=False,
            create_risk_scores=False,
        )
        result = fe.fit_transform(sample_data)
        assert "Balance_Salary_Ratio" in result.columns
        assert "CreditScore_Age_Ratio" in result.columns
        assert "Balance_per_Product" in result.columns

    def test_bins_created(self, sample_data):
        fe = ChurnFeatureEngineer(
            create_interactions=False,
            create_ratios=False,
            create_bins=True,
            create_risk_scores=False,
        )
        result = fe.fit_transform(sample_data)
        assert "Age_Group" in result.columns
        assert "Balance_Band" in result.columns
        assert "Tenure_Band" in result.columns
        assert "Credit_Band" in result.columns

    def test_risk_scores_created(self, sample_data):
        fe = ChurnFeatureEngineer(
            create_interactions=False,
            create_ratios=False,
            create_bins=False,
            create_risk_scores=True,
        )
        result = fe.fit_transform(sample_data)
        assert "Engagement_Score" in result.columns
        assert "Financial_Risk" in result.columns
        assert "Is_Zero_Balance" in result.columns
        assert "Is_Single_Product" in result.columns

    def test_all_disabled(self, sample_data):
        fe = ChurnFeatureEngineer(
            create_interactions=False,
            create_ratios=False,
            create_bins=False,
            create_risk_scores=False,
        )
        result = fe.fit_transform(sample_data)
        assert result.shape[1] == sample_data.shape[1]

    def test_engagement_score_range(self, sample_data):
        fe = ChurnFeatureEngineer()
        result = fe.fit_transform(sample_data)
        assert result["Engagement_Score"].min() >= 0
        assert result["Engagement_Score"].max() <= 1

    def test_financial_risk_range(self, sample_data):
        fe = ChurnFeatureEngineer()
        result = fe.fit_transform(sample_data)
        assert result["Financial_Risk"].min() >= 0
        assert result["Financial_Risk"].max() <= 1

    def test_binary_flags(self, sample_data):
        fe = ChurnFeatureEngineer()
        result = fe.fit_transform(sample_data)
        assert set(result["Is_Zero_Balance"].unique()).issubset({0, 1})
        assert set(result["Is_Single_Product"].unique()).issubset({0, 1})

    def test_sklearn_compatible(self, sample_data):
        """Verify sklearn BaseEstimator/TransformerMixin compatibility."""
        fe = ChurnFeatureEngineer()
        params = fe.get_params()
        assert "create_interactions" in params
        assert "create_ratios" in params

        fe2 = ChurnFeatureEngineer()
        fe2.set_params(create_interactions=False)
        assert fe2.create_interactions is False

    def test_idempotent_transform(self, sample_data):
        """Applying transform twice should not create duplicate columns."""
        fe = ChurnFeatureEngineer()
        result1 = fe.fit_transform(sample_data)
        result2 = fe.transform(sample_data)
        assert result1.shape == result2.shape
        assert list(result1.columns) == list(result2.columns)

    def test_partial_columns(self):
        """Test with minimal columns — no crash on missing features."""
        df = pd.DataFrame({"Age": [25, 35, 45], "Balance": [0, 50000, 150000]})
        fe = ChurnFeatureEngineer()
        result = fe.fit_transform(df)
        assert "Is_Zero_Balance" in result.columns
        assert result.shape[0] == 3


class TestStackingModel:
    """Test that stacking model builds correctly."""

    def test_stacking_builds(self):
        from src.bankchurn.models_advanced import build_model, get_available_models

        available = get_available_models()
        assert "stacking" in available
        assert available["stacking"] is True

        model = build_model("stacking", params={"calibrate": False})
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")

    def test_stacking_with_calibration(self):
        from src.bankchurn.models_advanced import build_model

        model = build_model("stacking", params={"calibrate": True})
        # CalibratedClassifierCV wraps the stacker
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")
        assert hasattr(model, "predict_proba")
