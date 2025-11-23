#!/usr/bin/env python3
"""
Data Quality Gate for CarVision-Market-Intelligence
Validates the vehicles_us.csv dataset before training pipeline execution.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

import pandas as pd


def validate_carvision_data(file_path: str | Path) -> None:
    """Validate CarVision dataset against quality rules.

    Args:
        file_path: Path to vehicles_us.csv dataset

    Raises:
        SystemExit: If any validation rule fails
    """
    print(f"🔍 Validating CarVision dataset: {file_path}")

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
        "price",  # Target variable
        "model_year",
        "model",
        "condition",
        "odometer",
        "fuel",
        "transmission",
        "type",
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        sys.exit(f"❌ Error: Missing required columns: {missing_cols}")

    print(f"   ✅ All required columns present: {len(required_cols)}")

    # Rule 4: Target column must not have nulls
    if df["price"].isnull().any():
        n_nulls = df["price"].isnull().sum()
        sys.exit(f"❌ Error: Target column 'price' has {n_nulls} null values")

    print("   ✅ Target column 'price' has no null values")

    # Rule 5: Price must be positive
    if (df["price"] <= 0).any():
        n_invalid = (df["price"] <= 0).sum()
        sys.exit(f"❌ Error: Found {n_invalid} rows with price <= 0")

    print("   ✅ All prices are positive")

    # Rule 6: Price range sanity check (reasonable car prices)
    if (df["price"] < 500).any() or (df["price"] > 500000).any():
        n_outliers = ((df["price"] < 500) | (df["price"] > 500000)).sum()
        print(f"   ⚠️  Warning: {n_outliers} prices outside typical range ($500-$500k)")
    else:
        print("   ✅ Price range appears reasonable ($500-$500k)")

    # Rule 7: Dataset must have reasonable size
    if len(df) < 100:
        sys.exit(f"❌ Error: Dataset too small for training ({len(df)} rows). Minimum: 100")

    print(f"   ✅ Dataset size adequate: {len(df)} rows")

    # Rule 8: Check for duplicate rows
    n_duplicates = df.duplicated().sum()
    if n_duplicates > 0:
        print(f"   ⚠️  Warning: Found {n_duplicates} duplicate rows ({n_duplicates/len(df)*100:.1f}%)")
    else:
        print("   ✅ No duplicate rows found")

    # Rule 9: Feature value ranges (basic sanity checks)
    current_year = pd.Timestamp.now().year
    if (df["model_year"] < 1900).any() or (df["model_year"] > current_year + 1).any():
        sys.exit(f"❌ Error: model_year has unrealistic values (must be 1900-{current_year+1})")

    if (df["odometer"] < 0).any():
        sys.exit("❌ Error: odometer has negative values")

    if (df["odometer"] > 1000000).any():
        n_high = (df["odometer"] > 1000000).sum()
        print(f"   ⚠️  Warning: {n_high} vehicles with odometer > 1M miles (potential outliers)")

    print("   ✅ Feature value ranges appear reasonable")

    # Rule 10: Check missing values percentage
    missing_pct = (df.isnull().sum() / len(df)) * 100
    high_missing = missing_pct[missing_pct > 50]
    if not high_missing.empty:
        print(f"   ⚠️  Warning: Some columns have >50% missing values:\n{high_missing}")
    else:
        print("   ✅ No columns with excessive missing values (>50%)")

    print("\n✅ All data quality checks passed! Dataset is ready for training pipeline.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate CarVision dataset quality before training")
    parser.add_argument(
        "--data-path",
        type=str,
        default="vehicles_us.csv",
        help="Path to vehicles_us.csv dataset (default: vehicles_us.csv)",
    )
    args = parser.parse_args()

    validate_carvision_data(args.data_path)


if __name__ == "__main__":
    main()
