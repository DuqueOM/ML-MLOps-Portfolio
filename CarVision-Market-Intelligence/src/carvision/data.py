"""
Data preprocessing utilities for CarVision Market Intelligence.
Provides functions to load, clean, split, and transform the vehicles dataset.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def load_data(csv_path: str) -> pd.DataFrame:
    """Load dataset from CSV path.

    Args:
        csv_path: Path to CSV file.
    Returns:
        pandas DataFrame
    """
    df = pd.read_csv(csv_path)
    return df


def clean_data(df: pd.DataFrame, filters: Optional[Dict[str, float]] = None) -> pd.DataFrame:
    """Basic cleaning strictly for filtering invalid rows.

    Feature engineering has been moved to src.carvision.features.FeatureEngineer
    to ensure pipeline consistency.

    Args:
        df: Input DataFrame
        filters: Dictionary with filter thresholds (min_price, max_price, min_year, etc.)
    """
    filters = filters or {}
    min_price = filters.get("min_price", 1000)
    max_price = filters.get("max_price", 500000)
    min_year = filters.get("min_year", 1990)
    max_odometer = filters.get("max_odometer", 500000)

    dfc = df.copy()
    # Ensure columns exist before filtering to be robust
    if "price" in dfc.columns:
        dfc = dfc[(dfc["price"] > min_price) & (dfc["price"] < max_price)]

    if "model_year" in dfc.columns:
        # Filter by minimum year
        dfc = dfc[(dfc["model_year"] >= min_year)]

    if "odometer" in dfc.columns:
        dfc = dfc[(dfc["odometer"] > 0) & (dfc["odometer"] < max_odometer)]

    return dfc


def _filter_columns(
    candidates: List[str],
    valid_columns: pd.Index,
    excluded: set,
) -> List[str]:
    """Filter columns that exist in dataframe and are not excluded.

    Args:
        candidates: List of candidate column names.
        valid_columns: Index of valid column names in dataframe.
        excluded: Set of column names to exclude.

    Returns:
        Filtered list of column names.
    """
    return [c for c in candidates if c in valid_columns and c not in excluded]


def _infer_numeric_columns(df: pd.DataFrame, excluded: set) -> List[str]:
    """Infer numeric columns from dataframe dtypes."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    return [c for c in numeric_cols if c not in excluded]


def _infer_categorical_columns(df: pd.DataFrame, excluded: set) -> List[str]:
    """Infer categorical columns from dataframe dtypes."""
    cat_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    return [c for c in cat_cols if c not in excluded]


def infer_feature_types(
    df: pd.DataFrame,
    target: str,
    numeric_features: Optional[List[str]] = None,
    categorical_features: Optional[List[str]] = None,
    drop_columns: Optional[List[str]] = None,
) -> Tuple[List[str], List[str]]:
    """Infer numeric and categorical features from dataframe if not provided.

    Args:
        df: Input DataFrame.
        target: Target column name (excluded from features).
        numeric_features: Optional list of numeric feature names.
        categorical_features: Optional list of categorical feature names.
        drop_columns: Optional list of columns to exclude.

    Returns:
        Tuple of (numeric_columns, categorical_columns).
    """
    excluded = set(drop_columns or [])
    excluded.add(target)

    if numeric_features:
        num_cols = _filter_columns(numeric_features, df.columns, excluded)
    else:
        num_cols = _infer_numeric_columns(df, excluded)

    if categorical_features:
        cat_cols = _filter_columns(categorical_features, df.columns, excluded)
    else:
        cat_cols = _infer_categorical_columns(df, excluded)

    return num_cols, cat_cols


def build_preprocessor(
    numeric_features: List[str],
    categorical_features: List[str],
    numeric_imputer: str = "median",
    categorical_imputer: str = "most_frequent",
    scale_numeric: bool = True,
    handle_unknown: str = "ignore",
) -> ColumnTransformer:
    """Build ColumnTransformer for numeric and categorical features."""
    numeric_steps = [("imputer", SimpleImputer(strategy=numeric_imputer))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))
    numeric_pipeline = Pipeline(steps=numeric_steps)

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy=categorical_imputer)),
            ("onehot", OneHotEncoder(handle_unknown=handle_unknown, sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ]
    )
    return preprocessor


def split_data(
    df: pd.DataFrame,
    target: str,
    test_size: float,
    val_size: float,
    seed: int,
    shuffle: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series, Dict[str, List[int]],]:
    """Split dataframe into train/val/test and return indices mapping for reproducibility."""
    X = df.drop(columns=[target])
    y = df[target]

    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=test_size, random_state=seed, shuffle=shuffle
    )
    # val split from trainval
    val_rel_size = val_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval,
        y_trainval,
        test_size=val_rel_size,
        random_state=seed,
        shuffle=shuffle,
    )

    split_indices = {
        "train": X_train.index.tolist(),
        "val": X_val.index.tolist(),
        "test": X_test.index.tolist(),
    }

    return X_train, X_val, X_test, y_train, y_val, y_test, split_indices


def save_split_indices(indices: Dict[str, List[int]], path: str) -> None:
    Path(Path(path).parent).mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(indices, f)


def load_split_indices(path: str) -> Dict[str, List[int]]:
    with open(path, "r") as f:
        return json.load(f)
