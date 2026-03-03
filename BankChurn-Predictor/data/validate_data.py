#!/usr/bin/env python3
"""Data Quality Gate for BankChurn-Predictor.

Validates the Churn.csv dataset using pandera schemas before training.
Can be run standalone or imported as a module in the training pipeline.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd
import pandera as pa
from pandera import Check, Column, DataFrameSchema

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pandera Schema — BankChurn Dataset
# ---------------------------------------------------------------------------

BankChurnRawSchema = DataFrameSchema(
    columns={
        "CreditScore": Column(
            int,
            checks=[
                Check.greater_than_or_equal_to(300, error="CreditScore below 300"),
                Check.less_than_or_equal_to(900, error="CreditScore above 900"),
            ],
            nullable=False,
            description="Customer credit score (300-900)",
        ),
        "Geography": Column(
            str,
            checks=Check.isin(
                ["France", "Spain", "Germany"],
                error="Unknown geography value",
            ),
            nullable=False,
            description="Customer country",
        ),
        "Gender": Column(
            str,
            checks=Check.isin(["Male", "Female"], error="Invalid gender value"),
            nullable=False,
            description="Customer gender",
        ),
        "Age": Column(
            int,
            checks=[
                Check.greater_than_or_equal_to(18, error="Age below 18"),
                Check.less_than_or_equal_to(100, error="Age above 100"),
            ],
            nullable=False,
            description="Customer age (18-100)",
        ),
        "Tenure": Column(
            int,
            checks=[
                Check.greater_than_or_equal_to(0, error="Tenure below 0"),
                Check.less_than_or_equal_to(10, error="Tenure above 10"),
            ],
            nullable=False,
            description="Years with bank (0-10)",
        ),
        "Balance": Column(
            float,
            checks=Check.greater_than_or_equal_to(0, error="Negative balance"),
            nullable=False,
            coerce=True,
            description="Account balance (>= 0)",
        ),
        "NumOfProducts": Column(
            int,
            checks=[
                Check.greater_than_or_equal_to(1, error="Must have >= 1 product"),
                Check.less_than_or_equal_to(4, error="Max 4 products"),
            ],
            nullable=False,
            description="Number of bank products (1-4)",
        ),
        "HasCrCard": Column(
            int,
            checks=Check.isin([0, 1], error="HasCrCard must be 0 or 1"),
            nullable=False,
            description="Has credit card (0/1)",
        ),
        "IsActiveMember": Column(
            int,
            checks=Check.isin([0, 1], error="IsActiveMember must be 0 or 1"),
            nullable=False,
            description="Active member flag (0/1)",
        ),
        "EstimatedSalary": Column(
            float,
            checks=Check.greater_than_or_equal_to(0, error="Negative salary"),
            nullable=False,
            coerce=True,
            description="Estimated annual salary",
        ),
        "Exited": Column(
            int,
            checks=Check.isin([0, 1], error="Exited must be 0 or 1"),
            nullable=False,
            description="Target: customer churned (0/1)",
        ),
    },
    checks=[
        Check(
            lambda df: len(df) >= 100,
            error="Dataset must have at least 100 rows for training",
        ),
        Check(
            lambda df: df["Exited"].mean() >= 0.05,
            error="Minority class < 5% — severe imbalance",
        ),
    ],
    strict=False,  # Allow extra columns (e.g., RowNumber, CustomerId, Surname)
    coerce=True,
    description="BankChurn raw dataset schema",
)

# Inference request schema (API input validation)
BankChurnInferenceSchema = DataFrameSchema(
    columns={
        "CreditScore": Column(int, Check.in_range(300, 900), coerce=True),
        "Geography": Column(str, Check.isin(["France", "Spain", "Germany"])),
        "Gender": Column(str, Check.isin(["Male", "Female"])),
        "Age": Column(int, Check.in_range(18, 100), coerce=True),
        "Tenure": Column(int, Check.in_range(0, 10), coerce=True),
        "Balance": Column(float, Check.greater_than_or_equal_to(0), coerce=True),
        "NumOfProducts": Column(int, Check.in_range(1, 4), coerce=True),
        "HasCrCard": Column(int, Check.isin([0, 1]), coerce=True),
        "IsActiveMember": Column(int, Check.isin([0, 1]), coerce=True),
        "EstimatedSalary": Column(
            float, Check.greater_than_or_equal_to(0), coerce=True
        ),
    },
    strict=False,
    coerce=True,
    description="BankChurn inference request schema",
)


def validate_bankchurn_data(file_path: str | Path) -> pd.DataFrame:
    """Validate BankChurn dataset against pandera schema.

    Args:
        file_path: Path to Churn.csv dataset

    Returns:
        Validated DataFrame

    Raises:
        FileNotFoundError: If file doesn't exist
        pa.errors.SchemaErrors: If validation fails
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    df = pd.read_csv(file_path)
    logger.info(f"Loaded {len(df)} rows from {file_path}")

    validated_df = BankChurnRawSchema.validate(df, lazy=True)

    # Additional quality metrics (warnings, not failures)
    n_duplicates = df.duplicated().sum()
    if n_duplicates > 0:
        logger.warning(
            f"Found {n_duplicates} duplicate rows ({n_duplicates / len(df) * 100:.1f}%)"
        )

    null_pct = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
    logger.info(f"Overall null percentage: {null_pct:.2f}%")

    class_dist = df["Exited"].value_counts(normalize=True)
    logger.info(f"Class distribution: {dict(class_dist.round(3))}")

    return validated_df


def validate_inference_input(df: pd.DataFrame) -> pd.DataFrame:
    """Validate inference input against schema.

    Args:
        df: Input DataFrame from API request

    Returns:
        Validated DataFrame
    """
    return BankChurnInferenceSchema.validate(df, lazy=True)


def get_validation_report(file_path: str | Path) -> Dict:
    """Generate a validation report for CI/CD pipelines.

    Returns:
        Dictionary with validation status, row count, schema checks, and warnings.
    """
    file_path = Path(file_path)
    report: Dict = {"file": str(file_path), "status": "unknown", "checks": []}

    try:
        df = pd.read_csv(file_path)
        BankChurnRawSchema.validate(df, lazy=True)
        report["status"] = "passed"
        report["rows"] = len(df)
        report["columns"] = len(df.columns)
        report["null_pct"] = round(
            df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100, 2
        )
        report["class_balance"] = dict(
            df["Exited"].value_counts(normalize=True).round(3)
        )
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
        description="Validate BankChurn dataset quality before training"
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/raw/Churn.csv",
        help="Path to Churn.csv dataset (default: data/raw/Churn.csv)",
    )
    parser.add_argument(
        "--report", action="store_true", help="Output JSON validation report"
    )
    args = parser.parse_args()

    if args.report:
        import json

        report = get_validation_report(args.data_path)
        print(json.dumps(report, indent=2))
        sys.exit(0 if report["status"] == "passed" else 1)

    try:
        validated = validate_bankchurn_data(args.data_path)
        print(f"All checks passed: {len(validated)} rows validated")
    except pa.errors.SchemaErrors as e:
        print(f"Validation failed with {len(e.failure_cases)} errors:", file=sys.stderr)
        print(e.failure_cases.to_string(), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
