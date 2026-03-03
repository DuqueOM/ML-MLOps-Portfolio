"""Advanced feature engineering for vehicle price prediction.

Implements domain-driven features that encode automotive market knowledge:
- Depreciation modeling (non-linear age effects)
- Mileage efficiency metrics
- Brand tier classification
- Condition-based scoring
- Market segment indicators
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

logger = logging.getLogger(__name__)

# Brand tiers based on market positioning (used for target encoding proxy)
LUXURY_BRANDS = {
    "bmw",
    "mercedes-benz",
    "audi",
    "lexus",
    "porsche",
    "tesla",
    "jaguar",
    "land rover",
    "volvo",
}
ECONOMY_BRANDS = {
    "nissan",
    "hyundai",
    "kia",
    "mitsubishi",
    "suzuki",
    "fiat",
    "mazda",
    "subaru",
}
DOMESTIC_BRANDS = {
    "ford",
    "chevrolet",
    "gmc",
    "dodge",
    "ram",
    "jeep",
    "chrysler",
    "cadillac",
    "buick",
    "lincoln",
}


class FeatureEngineer(BaseEstimator, TransformerMixin):
    """Centralized feature engineering for vehicle price prediction.

    Creates domain-driven features that improve model performance:
    - Vehicle age and non-linear depreciation curve
    - Brand extraction and tier classification
    - Mileage efficiency and usage intensity
    - Condition-based numerical scoring
    - Market segment indicators

    Parameters
    ----------
    current_year : int, optional
        Reference year for age calculation. Defaults to current year.
    """

    def __init__(self, current_year: Optional[int] = None):
        self.current_year = current_year

    def fit(self, X: pd.DataFrame, y: pd.DataFrame = None) -> "FeatureEngineer":
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        n_original = X.shape[1]
        year = self.current_year or pd.Timestamp.now().year

        # --- Core features ---
        if "model_year" in X.columns:
            X["vehicle_age"] = year - X["model_year"]
            # Non-linear depreciation: vehicles lose ~15-20% in year 1, then slower
            X["depreciation_factor"] = 1 - np.exp(-0.15 * X["vehicle_age"].clip(lower=0))
            X["age_squared"] = X["vehicle_age"] ** 2

        if "model" in X.columns:
            X["brand"] = X["model"].astype(str).str.split().str[0]

        # --- Brand tier (proxy for target encoding without leakage) ---
        if "brand" in X.columns:
            brand_lower = X["brand"].str.lower()
            X["is_luxury"] = brand_lower.isin(LUXURY_BRANDS).astype(int)
            X["is_domestic"] = brand_lower.isin(DOMESTIC_BRANDS).astype(int)
            X["is_economy"] = brand_lower.isin(ECONOMY_BRANDS).astype(int)

        # --- Mileage features ---
        if "odometer" in X.columns:
            X["log_odometer"] = np.log1p(X["odometer"])

            if "vehicle_age" in X.columns:
                # Miles per year: usage intensity indicator
                X["miles_per_year"] = X["odometer"] / (X["vehicle_age"].clip(lower=1))
                X["is_low_mileage"] = (X["miles_per_year"] < 10000).astype(int)
                X["is_high_mileage"] = (X["miles_per_year"] > 20000).astype(int)

        # --- Condition scoring (ordinal encoding) ---
        if "condition" in X.columns:
            condition_map = {
                "salvage": 0,
                "fair": 1,
                "good": 2,
                "excellent": 3,
                "like new": 4,
                "new": 5,
            }
            X["condition_score"] = X["condition"].str.lower().map(condition_map).fillna(2)

        # --- Cylinder power proxy ---
        if "cylinders" in X.columns:
            cyl = pd.to_numeric(
                X["cylinders"].astype(str).str.extract(r"(\d+)", expand=False),
                errors="coerce",
            ).fillna(0)
            X["is_high_power"] = (cyl >= 8).astype(int)

        # --- Fuel type indicators ---
        if "fuel" in X.columns:
            X["is_electric_hybrid"] = (X["fuel"].str.lower().isin({"electric", "hybrid"})).astype(int)
            X["is_diesel"] = (X["fuel"].str.lower() == "diesel").astype(int)

        # --- Derived features for analysis/training only (requires target) ---
        if "odometer" in X.columns:
            if "price" in X.columns:
                X["price_per_mile"] = X["price"] / (X["odometer"] + 1)
            if "price" in X.columns and "price_category" not in X.columns:
                X["price_category"] = pd.cut(
                    X["price"],
                    bins=[0, 10000, 25000, 50000, float("inf")],
                    labels=["Budget", "Mid-Range", "Premium", "Luxury"],
                )

        n_new = X.shape[1] - n_original
        logger.info(f"CarVision features: {n_original} → {X.shape[1]} (+{n_new})")
        return X
