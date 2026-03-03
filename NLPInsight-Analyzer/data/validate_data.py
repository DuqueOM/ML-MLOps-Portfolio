#!/usr/bin/env python3
"""Data Quality Gate for NLPInsight-Analyzer.

Validates text classification datasets using pandera schemas before training.
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
# Pandera Schema — NLPInsight Text Classification Dataset
# ---------------------------------------------------------------------------

NLPInsightRawSchema = DataFrameSchema(
    columns={
        "text": Column(
            str,
            checks=[
                Check(
                    lambda s: s.str.len().ge(1),
                    element_wise=False,
                    error="Text must be non-empty",
                ),
                Check(
                    lambda s: s.str.len().le(10_000),
                    element_wise=False,
                    error="Text exceeds 10k chars — likely corrupted",
                ),
            ],
            nullable=False,
            description="Input text for sentiment classification",
        ),
        "label": Column(
            str,
            checks=Check.isin(
                ["negative", "neutral", "positive"],
                error="Label must be one of: negative, neutral, positive",
            ),
            nullable=False,
            description="Sentiment label",
        ),
    },
    checks=[
        Check(
            lambda df: len(df) >= 50,
            error="Dataset must have at least 50 samples for training",
        ),
        Check(
            lambda df: df["label"].nunique() >= 2,
            error="Dataset must have at least 2 distinct labels",
        ),
    ],
    strict=False,  # Allow extra columns (e.g., source, timestamp)
    coerce=True,
    description="NLPInsight text classification dataset schema",
)

# Inference request schema (API input)
NLPInsightInferenceSchema = DataFrameSchema(
    columns={
        "text": Column(
            str,
            checks=[
                Check(
                    lambda s: s.str.len().ge(1),
                    element_wise=False,
                    error="Text must be non-empty",
                ),
                Check(
                    lambda s: s.str.len().le(5_000),
                    element_wise=False,
                    error="Text too long for inference",
                ),
            ],
            nullable=False,
        ),
    },
    strict=False,
    coerce=True,
    description="NLPInsight inference request schema",
)


def validate_nlpinsight_data(
    file_path: str | Path,
    text_col: str = "text",
    label_col: str = "label",
) -> pd.DataFrame:
    """Validate NLPInsight dataset against pandera schema.

    Args:
        file_path: Path to CSV dataset
        text_col: Name of the text column
        label_col: Name of the label column

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

    # Rename columns if needed to match schema
    rename_map = {}
    if text_col != "text":
        rename_map[text_col] = "text"
    if label_col != "label":
        rename_map[label_col] = "label"
    if rename_map:
        df = df.rename(columns=rename_map)

    logger.info(f"Loaded {len(df)} rows from {file_path}")

    validated_df = NLPInsightRawSchema.validate(df, lazy=True)

    # Quality metrics
    label_dist = df["label"].value_counts(normalize=True)
    logger.info(f"Label distribution: {dict(label_dist.round(3))}")

    text_lengths = df["text"].str.len()
    logger.info(
        f"Text length: mean={text_lengths.mean():.0f}, median={text_lengths.median():.0f}, max={text_lengths.max():.0f}"
    )

    n_dups = df["text"].duplicated().sum()
    if n_dups:
        logger.warning(
            f"Found {n_dups} duplicate texts ({n_dups / len(df) * 100:.1f}%)"
        )

    return validated_df


def validate_inference_input(df: pd.DataFrame) -> pd.DataFrame:
    """Validate inference input against schema."""
    return NLPInsightInferenceSchema.validate(df, lazy=True)


def get_validation_report(file_path: str | Path) -> Dict:
    """Generate a validation report for CI/CD pipelines."""
    file_path = Path(file_path)
    report: Dict = {"file": str(file_path), "status": "unknown"}

    try:
        df = pd.read_csv(file_path)
        NLPInsightRawSchema.validate(df, lazy=True)
        report["status"] = "passed"
        report["rows"] = len(df)
        report["columns"] = len(df.columns)
        report["label_distribution"] = dict(
            df["label"].value_counts(normalize=True).round(3)
        )
        report["avg_text_length"] = int(df["text"].str.len().mean())
        report["duplicate_texts"] = int(df["text"].duplicated().sum())
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
        description="Validate NLPInsight dataset quality before training"
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/raw/train.csv",
        help="Path to text classification CSV",
    )
    parser.add_argument("--report", action="store_true", help="Output JSON report")
    args = parser.parse_args()

    if args.report:
        import json

        report = get_validation_report(args.data_path)
        print(json.dumps(report, indent=2))
        sys.exit(0 if report["status"] == "passed" else 1)

    try:
        validated = validate_nlpinsight_data(args.data_path)
        print(f"All checks passed: {len(validated)} rows validated")
    except pa.errors.SchemaErrors as e:
        print(f"Validation failed with {len(e.failure_cases)} errors:", file=sys.stderr)
        print(e.failure_cases.to_string(), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
