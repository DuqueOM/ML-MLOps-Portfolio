#!/usr/bin/env python3
"""Data Quality Gate for CarVision-Market-Intelligence.

Validates the vehicles dataset using pandera schemas before training.
Can be run standalone or imported as a module in the training pipeline.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict

import pandas as pd
import pandera as pa
from pandera import Check, Column, DataFrameSchema

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pandera Schema — CarVision Dataset
# ---------------------------------------------------------------------------

CarVisionRawSchema = DataFrameSchema(
    columns={
        "price": Column(
            float,
            checks=[
                Check.greater_than(0, error="Price must be positive"),
                Check.less_than(500_000, error="Price exceeds $500k — likely error"),
            ],
            nullable=False,
            coerce=True,
            description="Vehicle sale price in USD",
        ),
        "model_year": Column(
            float,
            checks=[
                Check.greater_than_or_equal_to(1900, error="Model year before 1900"),
                Check.less_than_or_equal_to(2026, error="Model year in the future"),
            ],
            nullable=True,
            coerce=True,
            description="Vehicle model year",
        ),
        "odometer": Column(
            float,
            checks=[
                Check.greater_than_or_equal_to(0, error="Negative odometer"),
                Check.less_than(1_000_000, error="Odometer exceeds 1M miles"),
            ],
            nullable=True,
            coerce=True,
            description="Vehicle mileage",
        ),
        "condition": Column(
            str,
            checks=Check.isin(
                ["new", "like new", "excellent", "good", "fair", "salvage"],
                error="Unknown vehicle condition",
            ),
            nullable=True,
            description="Vehicle condition category",
        ),
        "fuel": Column(
            str,
            checks=Check.isin(
                ["gas", "diesel", "electric", "hybrid", "other"],
                error="Unknown fuel type",
            ),
            nullable=True,
            description="Fuel type",
        ),
        "transmission": Column(
            str,
            checks=Check.isin(
                ["automatic", "manual", "other"],
                error="Unknown transmission type",
            ),
            nullable=True,
            description="Transmission type",
        ),
        "drive": Column(
            str,
            checks=Check.isin(["fwd", "rwd", "4wd"], error="Unknown drive type"),
            nullable=True,
            description="Drive type",
        ),
        "type": Column(
            str,
            nullable=True,
            description="Vehicle type (sedan, SUV, truck, etc.)",
        ),
        "paint_color": Column(str, nullable=True, description="Exterior color"),
        "state": Column(str, nullable=True, description="US state (2-letter code)"),
    },
    checks=[
        Check(
            lambda df: len(df) >= 100,
            error="Dataset must have at least 100 rows for training",
        ),
    ],
    strict=False,  # Allow extra columns (e.g., region, manufacturer, model)
    coerce=True,
    description="CarVision raw vehicle dataset schema",
)

# Inference request schema (API input)
CarVisionInferenceSchema = DataFrameSchema(
    columns={
        "model_year": Column(
            float, Check.in_range(1900, 2026), coerce=True, nullable=True
        ),
        "odometer": Column(
            float, Check.greater_than_or_equal_to(0), coerce=True, nullable=True
        ),
        "condition": Column(str, nullable=True),
        "fuel": Column(str, nullable=True),
        "transmission": Column(str, nullable=True),
    },
    strict=False,
    coerce=True,
    description="CarVision inference request schema",
)


def validate_carvision_data(file_path: str | Path) -> pd.DataFrame:
    """Validate CarVision dataset against pandera schema.

    Args:
        file_path: Path to vehicles CSV dataset

    Returns:
        Validated DataFrame

    Raises:
        FileNotFoundError: If file doesn't exist
        pa.errors.SchemaErrors: If validation fails
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    df = pd.read_csv(file_path, low_memory=False)
    logger.info(f"Loaded {len(df)} rows from {file_path}")

    validated_df = CarVisionRawSchema.validate(df, lazy=True)

    # Quality metrics
    null_pct = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
    logger.info(f"Overall null percentage: {null_pct:.2f}%")

    price_stats = df["price"].describe()
    logger.info(
        f"Price range: ${price_stats['min']:.0f} — ${price_stats['max']:.0f} (median: ${price_stats['50%']:.0f})"
    )

    return validated_df


def validate_inference_input(df: pd.DataFrame) -> pd.DataFrame:
    """Validate inference input against schema."""
    return CarVisionInferenceSchema.validate(df, lazy=True)


def get_validation_report(file_path: str | Path) -> Dict:
    """Generate a validation report for CI/CD pipelines."""
    file_path = Path(file_path)
    report: Dict = {"file": str(file_path), "status": "unknown"}

    try:
        df = pd.read_csv(file_path, low_memory=False)
        CarVisionRawSchema.validate(df, lazy=True)
        report["status"] = "passed"
        report["rows"] = len(df)
        report["columns"] = len(df.columns)
        report["null_pct"] = round(
            df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100, 2
        )
        report["price_median"] = float(df["price"].median())
        report["duplicates"] = int(df.duplicated().sum())
    except pa.errors.SchemaErrors as e:
        report["status"] = "failed"
        report["errors"] = [
            {"check": str(err["check"]), "column": str(err.get("column", "dataframe"))}
            for _, err in e.failure_cases.iterrows()
        ]
    except Exception as e:
        report["status"] = "error"
        report["message"] = str(e)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate CarVision dataset quality before training"
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/raw/vehicles_us.csv",
        help="Path to vehicles CSV (default: data/raw/vehicles_us.csv)",
    )
    parser.add_argument("--report", action="store_true", help="Output JSON report")
    args = parser.parse_args()

    if args.report:
        import json

        report = get_validation_report(args.data_path)
        print(json.dumps(report, indent=2))
        sys.exit(0 if report["status"] == "passed" else 1)

    try:
        validated = validate_carvision_data(args.data_path)
        print(f"All checks passed: {len(validated)} rows validated")
    except pa.errors.SchemaErrors as e:
        print(f"Validation failed with {len(e.failure_cases)} errors:", file=sys.stderr)
        print(e.failure_cases.to_string(), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
