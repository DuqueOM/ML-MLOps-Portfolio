#!/usr/bin/env python3
"""
Data Quality Gate for BankChurn-Predictor
Validates the Churn.csv dataset before training pipeline execution.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

import pandas as pd


def validate_bankchurn_data(file_path: str | Path) -> None:
    """Validate BankChurn dataset against quality rules.

    Args:
        file_path: Path to Churn.csv dataset

    Raises:
        SystemExit: If any validation rule fails
    """
    print(f"🔍 Validating BankChurn dataset: {file_path}")

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
        "CreditScore",
        "Geography",
        "Gender",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
        "EstimatedSalary",
        "Exited",  # Target variable
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        sys.exit(f"❌ Error: Missing required columns: {missing_cols}")

    print(f"   ✅ All required columns present: {len(required_cols)}")

    # Rule 4: Target column must not have nulls
    if df["Exited"].isnull().any():
        n_nulls = df["Exited"].isnull().sum()
        sys.exit(f"❌ Error: Target column 'Exited' has {n_nulls} null values")

    print("   ✅ Target column 'Exited' has no null values")

    # Rule 5: Target must be binary (0/1)
    unique_targets = df["Exited"].unique()
    if not set(unique_targets).issubset({0, 1}):
        sys.exit(
            f"❌ Error: Target 'Exited' must be binary (0/1), found: {unique_targets}"
        )

    print("   ✅ Target column is binary (0/1)")

    # Rule 6: Dataset must have reasonable size (>= 100 rows for meaningful training)
    if len(df) < 100:
        sys.exit(
            f"❌ Error: Dataset too small for training ({len(df)} rows). Minimum: 100"
        )

    print(f"   ✅ Dataset size adequate: {len(df)} rows")

    # Rule 7: Check class balance (warn if severe imbalance)
    class_dist = df["Exited"].value_counts(normalize=True)
    minority_pct = class_dist.min() * 100
    if minority_pct < 5:
        print(
            f"   ⚠️  Warning: Severe class imbalance detected (minority class: {minority_pct:.1f}%)"
        )
    else:
        print(f"   ✅ Class balance acceptable (minority class: {minority_pct:.1f}%)")

    # Rule 8: Check for duplicate rows
    n_duplicates = df.duplicated().sum()
    if n_duplicates > 0:
        print(
            f"   ⚠️  Warning: Found {n_duplicates} duplicate rows ({n_duplicates/len(df)*100:.1f}%)"
        )
    else:
        print("   ✅ No duplicate rows found")

    # Rule 9: Feature value ranges (basic sanity checks)
    if (df["Age"] < 0).any() or (df["Age"] > 120).any():
        sys.exit("❌ Error: Age column has unrealistic values (must be 0-120)")

    if (df["CreditScore"] < 300).any() or (df["CreditScore"] > 900).any():
        print("   ⚠️  Warning: Some CreditScore values outside typical range (300-900)")

    print("   ✅ Feature value ranges appear reasonable")

    print(
        "\n✅ All data quality checks passed! Dataset is ready for training pipeline."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate BankChurn dataset quality before training"
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/raw/Churn.csv",
        help="Path to Churn.csv dataset (default: data/raw/Churn.csv)",
    )
    args = parser.parse_args()

    validate_bankchurn_data(args.data_path)


if __name__ == "__main__":
    main()
