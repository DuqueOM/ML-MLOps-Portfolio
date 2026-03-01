"""Advanced feature engineering for churn prediction.

Implements a sklearn-compatible transformer that creates domain-driven
features to improve model performance beyond basic preprocessing.

Features created:
- Interaction features (Age × products, Balance × activity)
- Ratio features (Balance/Salary, CreditScore/Age)
- Binning features (age groups, balance quartiles, tenure bands)
- Risk composite scores (engagement, financial, loyalty)
"""

from __future__ import annotations

import logging

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

logger = logging.getLogger(__name__)


class ChurnFeatureEngineer(BaseEstimator, TransformerMixin):
    """Domain-driven feature engineering for bank churn prediction.

    Creates interaction, ratio, binning, and composite risk features
    that encode banking domain knowledge into the model pipeline.

    Parameters
    ----------
    create_interactions : bool, default=True
        Create interaction features between key predictors.
    create_ratios : bool, default=True
        Create ratio features (e.g., Balance/Salary).
    create_bins : bool, default=True
        Create binned versions of continuous features.
    create_risk_scores : bool, default=True
        Create composite risk scoring features.

    Examples
    --------
    >>> fe = ChurnFeatureEngineer()
    >>> X_transformed = fe.fit_transform(X)
    """

    def __init__(
        self,
        create_interactions: bool = True,
        create_ratios: bool = True,
        create_bins: bool = True,
        create_risk_scores: bool = True,
    ):
        self.create_interactions = create_interactions
        self.create_ratios = create_ratios
        self.create_bins = create_bins
        self.create_risk_scores = create_risk_scores

    def fit(self, X: pd.DataFrame, y=None) -> "ChurnFeatureEngineer":
        """Fit is a no-op — all transformations are stateless.

        Parameters
        ----------
        X : DataFrame
            Input features.
        y : ignored

        Returns
        -------
        self
        """
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Apply feature engineering transformations.

        Parameters
        ----------
        X : DataFrame
            Raw input features.

        Returns
        -------
        X_out : DataFrame
            Features with engineered columns appended.
        """
        X = X.copy()
        n_original = X.shape[1]

        if self.create_interactions:
            X = self._add_interactions(X)
        if self.create_ratios:
            X = self._add_ratios(X)
        if self.create_bins:
            X = self._add_bins(X)
        if self.create_risk_scores:
            X = self._add_risk_scores(X)

        n_new = X.shape[1] - n_original
        logger.info(f"Feature engineering: {n_original} → {X.shape[1]} features (+{n_new})")
        return X

    # ------------------------------------------------------------------
    # Interaction features
    # ------------------------------------------------------------------
    @staticmethod
    def _add_interactions(X: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features between key predictors.

        Domain rationale:
        - Age × NumOfProducts: older customers with few products churn more
        - Balance × IsActiveMember: high balance + inactive = flight risk
        - CreditScore × Tenure: loyalty signal
        """
        if "Age" in X.columns and "NumOfProducts" in X.columns:
            X["Age_x_NumProducts"] = X["Age"] * X["NumOfProducts"]

        if "Balance" in X.columns and "IsActiveMember" in X.columns:
            X["Balance_x_Active"] = X["Balance"] * X["IsActiveMember"]

        if "CreditScore" in X.columns and "Tenure" in X.columns:
            X["CreditScore_x_Tenure"] = X["CreditScore"] * X["Tenure"]

        if "Age" in X.columns and "IsActiveMember" in X.columns:
            X["Age_x_Active"] = X["Age"] * X["IsActiveMember"]

        return X

    # ------------------------------------------------------------------
    # Ratio features
    # ------------------------------------------------------------------
    @staticmethod
    def _add_ratios(X: pd.DataFrame) -> pd.DataFrame:
        """Create ratio features encoding financial behavior.

        Domain rationale:
        - Balance/Salary: savings rate — low ratio may indicate dissatisfaction
        - CreditScore/Age: creditworthiness relative to age
        - Balance per product: account concentration
        """
        if "Balance" in X.columns and "EstimatedSalary" in X.columns:
            X["Balance_Salary_Ratio"] = X["Balance"] / (X["EstimatedSalary"] + 1)

        if "CreditScore" in X.columns and "Age" in X.columns:
            X["CreditScore_Age_Ratio"] = X["CreditScore"] / (X["Age"] + 1)

        if "Balance" in X.columns and "NumOfProducts" in X.columns:
            X["Balance_per_Product"] = X["Balance"] / (X["NumOfProducts"] + 1)

        return X

    # ------------------------------------------------------------------
    # Binning features
    # ------------------------------------------------------------------
    @staticmethod
    def _add_bins(X: pd.DataFrame) -> pd.DataFrame:
        """Create binned categorical features from continuous variables.

        Domain rationale:
        - Age groups capture non-linear churn patterns (55+ churns 2.3× more)
        - Balance quartiles capture the high-balance churn paradox
        - Tenure bands capture loyalty tiers
        """
        if "Age" in X.columns:
            X["Age_Group"] = pd.cut(
                X["Age"],
                bins=[0, 30, 40, 50, 60, 100],
                labels=["Young", "Early_Mid", "Mid", "Senior", "Elder"],
            ).astype(str)

        if "Balance" in X.columns:
            X["Balance_Band"] = pd.cut(
                X["Balance"],
                bins=[-1, 1, 50000, 100000, 150000, float("inf")],
                labels=["Zero", "Low", "Medium", "High", "VeryHigh"],
            ).astype(str)

        if "Tenure" in X.columns:
            X["Tenure_Band"] = pd.cut(
                X["Tenure"],
                bins=[-1, 2, 5, 8, 11],
                labels=["New", "Growing", "Mature", "Veteran"],
            ).astype(str)

        if "CreditScore" in X.columns:
            X["Credit_Band"] = pd.cut(
                X["CreditScore"],
                bins=[0, 580, 670, 740, 800, 900],
                labels=["Poor", "Fair", "Good", "VeryGood", "Excellent"],
            ).astype(str)

        return X

    # ------------------------------------------------------------------
    # Composite risk scores
    # ------------------------------------------------------------------
    @staticmethod
    def _add_risk_scores(X: pd.DataFrame) -> pd.DataFrame:
        """Create composite risk scores combining multiple signals.

        Domain rationale:
        - Engagement score: multi-factor measure of customer engagement
        - Financial risk: combines balance and product usage patterns
        - Churn risk index: weighted composite of top churn predictors
        """
        # Engagement score: active + products + tenure (higher = more engaged)
        engagement_cols = ["IsActiveMember", "NumOfProducts", "Tenure", "HasCrCard"]
        available = [c for c in engagement_cols if c in X.columns]
        if len(available) >= 2:
            # Normalize each component to 0-1 range before combining
            score = pd.DataFrame(index=X.index)
            if "IsActiveMember" in X.columns:
                score["active"] = X["IsActiveMember"]
            if "NumOfProducts" in X.columns:
                score["products"] = X["NumOfProducts"] / 4.0  # max 4 products
            if "Tenure" in X.columns:
                score["tenure"] = X["Tenure"] / 10.0  # max 10 years
            if "HasCrCard" in X.columns:
                score["card"] = X["HasCrCard"]
            X["Engagement_Score"] = score.mean(axis=1)

        # Financial risk score (higher = more risk of leaving)
        if all(c in X.columns for c in ["Balance", "EstimatedSalary", "NumOfProducts"]):
            # High balance + low products + high salary = looking elsewhere
            bal_norm = X["Balance"] / (X["Balance"].max() + 1)
            prod_inv = 1 - (X["NumOfProducts"] / 4.0)
            X["Financial_Risk"] = (bal_norm + prod_inv) / 2

        # Zero-balance flag (strong churn signal)
        if "Balance" in X.columns:
            X["Is_Zero_Balance"] = (X["Balance"] == 0).astype(int)

        # Single-product flag (high churn risk)
        if "NumOfProducts" in X.columns:
            X["Is_Single_Product"] = (X["NumOfProducts"] == 1).astype(int)

        return X
