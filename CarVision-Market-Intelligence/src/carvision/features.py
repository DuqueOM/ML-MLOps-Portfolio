from __future__ import annotations

from typing import Optional

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class FeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Centralized feature engineering to ensure consistency across
    Training, Inference, and Analysis.
    """

    def __init__(self, current_year: Optional[int] = None):
        self.current_year = current_year

    def fit(self, X: pd.DataFrame, y: pd.DataFrame = None) -> "FeatureEngineer":
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()

        # Use configured year or current year
        year = self.current_year or pd.Timestamp.now().year

        if "model_year" in X.columns:
            X["vehicle_age"] = year - X["model_year"]

        if "model" in X.columns:
            X["brand"] = X["model"].astype(str).str.split().str[0]

        # Derived features for analysis/training only (requires target/extra cols)
        # Note: Inference usually doesn't have 'price' or 'odometer' might be user input
        if "odometer" in X.columns:
            # We handle price_per_mile only if price exists (training/analysis)
            if "price" in X.columns:
                X["price_per_mile"] = X["price"] / (X["odometer"] + 1)

            # Ensure price_category is created if price exists
            if "price" in X.columns and "price_category" not in X.columns:
                X["price_category"] = pd.cut(
                    X["price"],
                    bins=[0, 10000, 25000, 50000, float("inf")],
                    labels=["Budget", "Mid-Range", "Premium", "Luxury"],
                )

        return X
