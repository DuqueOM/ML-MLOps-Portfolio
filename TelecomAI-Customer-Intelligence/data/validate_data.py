#!/usr/bin/env python3
"""
Data Quality Gate for TelecomAI-Customer-Intelligence
Validates the users_behavior.csv dataset before training pipeline execution.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

import pandas as pd


def validate_telecom_data(file_path: str | Path) -> None:
    """Validate TelecomAI dataset against quality rules.

    Args:
        file_path: Path to users_behavior.csv dataset

    Raises:
        SystemExit: If any validation rule fails
    """
    print(f"🔍 Validating TelecomAI dataset: {file_path}")

    # Rule 1: File must exist and be readable
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        sys.exit(f"❌ Error: Dataset file not found at {file_path}")
    except Exception as e:
        sys.exit(f"❌ Error: Failed to read dataset: {e}")

    # Rule 2: Dataset must not be empty
    if df.empty:
        sys.exit("❌ Error: Dataset is empty (0 rows)")

    print(f"   ✅ Dataset loaded: {len(df)} rows, {len(df.columns)} columns")

    # Rule 3: Required columns must exist
    required_cols: List[str] = [
        "calls",
        "minutes",
        "messages",
        "mb_used",
        "is_ultra",  # Target variable
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        sys.exit(f"❌ Error: Missing required columns: {missing_cols}")

    print(f"   ✅ All required columns present: {len(required_cols)}")

    # Rule 4: Target column must not have nulls
    if df["is_ultra"].isnull().any():
        n_nulls = df["is_ultra"].isnull().sum()
        sys.exit(f"❌ Error: Target column 'is_ultra' has {n_nulls} null values")

    print("   ✅ Target column 'is_ultra' has no null values")

    # Rule 5: Target must be binary (0/1)
    unique_targets = df["is_ultra"].unique()
    if not set(unique_targets).issubset({0, 1}):
        sys.exit(f"❌ Error: Target 'is_ultra' must be binary (0/1), found: {unique_targets}")

    print("   ✅ Target column is binary (0/1)")

    # Rule 6: Feature columns must not have nulls (critical for telecom usage data)
    feature_cols = ["calls", "minutes", "messages", "mb_used"]
    for col in feature_cols:
        if df[col].isnull().any():
            n_nulls = df[col].isnull().sum()
            sys.exit(f"❌ Error: Feature column '{col}' has {n_nulls} null values")

    print("   ✅ All feature columns have no null values")

    # Rule 7: Dataset must have reasonable size
    if len(df) < 100:
        sys.exit(f"❌ Error: Dataset too small for training ({len(df)} rows). Minimum: 100")

    print(f"   ✅ Dataset size adequate: {len(df)} rows")

    # Rule 8: Feature values must be non-negative
    for col in feature_cols:
        if (df[col] < 0).any():
            n_negative = (df[col] < 0).sum()
            sys.exit(f"❌ Error: Feature column '{col}' has {n_negative} negative values")

    print("   ✅ All feature values are non-negative")

    # Rule 9: Check class balance (warn if severe imbalance)
    class_dist = df["is_ultra"].value_counts(normalize=True)
    minority_pct = class_dist.min() * 100
    if minority_pct < 5:
        print(f"   ⚠️  Warning: Severe class imbalance detected (minority class: {minority_pct:.1f}%)")
    else:
        print(f"   ✅ Class balance acceptable (minority class: {minority_pct:.1f}%)")

    # Rule 10: Check for duplicate rows
    n_duplicates = df.duplicated().sum()
    if n_duplicates > 0:
        print(f"   ⚠️  Warning: Found {n_duplicates} duplicate rows ({n_duplicates/len(df)*100:.1f}%)")
    else:
        print("   ✅ No duplicate rows found")

    # Rule 11: Sanity checks on usage patterns
    # Check if minutes > 0 when calls > 0 (basic consistency)
    inconsistent = df[(df["calls"] > 0) & (df["minutes"] == 0)]
    if len(inconsistent) > 10:
        print(f"   ⚠️  Warning: {len(inconsistent)} rows have calls>0 but minutes=0 (potential data quality issue)")

    # Check for extreme outliers in usage
    if (df["minutes"] > 10000).any():
        n_extreme = (df["minutes"] > 10000).sum()
        print(f"   ⚠️  Warning: {n_extreme} rows with >10k minutes/month (potential outliers)")

    if (df["mb_used"] > 100000).any():
        n_extreme = (df["mb_used"] > 100000).sum()
        print(f"   ⚠️  Warning: {n_extreme} rows with >100GB data usage (potential outliers)")

    print("   ✅ Usage patterns appear reasonable")

    print("\n✅ All data quality checks passed! Dataset is ready for training pipeline.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate TelecomAI dataset quality before training")
    parser.add_argument(
        "--data-path",
        type=str,
        default="users_behavior.csv",
        help="Path to users_behavior.csv dataset (default: users_behavior.csv)",
    )
    args = parser.parse_args()

    validate_telecom_data(args.data_path)


if __name__ == "__main__":
    main()
