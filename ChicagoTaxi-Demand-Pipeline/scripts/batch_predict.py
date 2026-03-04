#!/usr/bin/env python
"""Batch prediction on processed Chicago Taxi data using Dask.

Reads the partitioned Parquet output from the Spark ETL pipeline and
generates demand predictions using a trained RandomForest model. Uses
Dask for parallel partition-level inference, demonstrating batch ML
scoring at scale.

Pipeline:
  1. Load trained model (or train a quick one from aggregated data)
  2. Read hourly demand Parquet with Dask
  3. Feature matrix construction
  4. Parallel prediction across partitions
  5. Export predictions to Parquet + summary statistics

Usage:
    python scripts/data_at_scale/batch_predict_taxi.py \
        --input data/processed/taxi_trips_parquet/hourly_demand \
        --output data/processed/taxi_predictions \
        --model models/taxi_demand_model.joblib

    # Train a model first (if none exists):
    python scripts/data_at_scale/batch_predict_taxi.py \
        --input data/processed/taxi_trips_parquet/hourly_demand \
        --output data/processed/taxi_predictions \
        --train

Prerequisites:
    pip install dask[dataframe] scikit-learn joblib
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path

import dask.dataframe as dd
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("batch_predict_taxi")

FEATURE_COLS = [
    "hour",
    "day_of_week",
    "is_weekend",
    "pickup_community_area",
    "avg_distance_miles",
    "avg_fare",
    "avg_speed_mph",
]

TARGET_COL = "trip_count"


def train_demand_model(input_path: str, model_path: str, seed: int = 42) -> RandomForestRegressor:
    """Train a RandomForest demand prediction model from aggregated data."""
    logger.info("Training demand model from %s", input_path)
    t0 = time.time()

    # Load with Dask, then compute to pandas for training
    ddf = dd.read_parquet(input_path)
    df = ddf.compute()
    logger.info("  Loaded %s rows for training", f"{len(df):,}")

    # Prepare features
    available_features = [c for c in FEATURE_COLS if c in df.columns]
    if len(available_features) < 3:
        raise ValueError(f"Not enough features. Available: {list(df.columns)}, " f"Expected: {FEATURE_COLS}")

    X = df[available_features].fillna(0)
    y = df[TARGET_COL].fillna(0)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=seed)

    # Train
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=5,
        n_jobs=-1,
        random_state=seed,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    metrics = {
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "r2": float(r2_score(y_test, y_pred)),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "features": available_features,
    }

    logger.info("  RMSE: %.2f | MAE: %.2f | R²: %.4f", metrics["rmse"], metrics["mae"], metrics["r2"])
    logger.info("  Training completed in %.1fs", time.time() - t0)

    # Save model
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    logger.info("  Model saved to %s", model_path)

    # Save metrics alongside model
    metrics_path = str(Path(model_path).with_suffix(".metrics.json"))
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info("  Metrics saved to %s", metrics_path)

    return model


def batch_predict(model: RandomForestRegressor, input_path: str, output_path: str):
    """Run batch predictions using Dask for parallel inference."""
    logger.info("Batch prediction on %s", input_path)
    t0 = time.time()

    # Read with Dask
    ddf = dd.read_parquet(input_path)
    total_rows = len(ddf)
    n_partitions = ddf.npartitions
    logger.info(
        "  Loaded %s rows across %d partitions",
        f"{total_rows:,}",
        n_partitions,
    )

    # Determine available features
    available_features = [c for c in FEATURE_COLS if c in ddf.columns]
    logger.info("  Using features: %s", available_features)

    # Define prediction function for map_partitions
    def predict_partition(partition: pd.DataFrame) -> pd.DataFrame:
        """Predict on a single Dask partition."""
        if len(partition) == 0:
            partition["predicted_demand"] = []
            partition["demand_category"] = []
            return partition

        X = partition[available_features].fillna(0)
        preds = model.predict(X)

        partition = partition.copy()
        partition["predicted_demand"] = np.round(preds, 1)
        partition["demand_category"] = pd.cut(
            preds,
            bins=[0, 5, 20, 50, float("inf")],
            labels=["low", "medium", "high", "very_high"],
        )
        return partition

    # Apply predictions across all partitions in parallel
    logger.info("  Running parallel inference across %d partitions...", n_partitions)
    ddf_preds = ddf.map_partitions(predict_partition)

    # Write predictions to Parquet
    Path(output_path).mkdir(parents=True, exist_ok=True)
    ddf_preds.to_parquet(output_path, write_index=False, overwrite=True)

    pred_time = time.time() - t0
    throughput = total_rows / pred_time if pred_time > 0 else 0

    logger.info("  Predictions written to %s", output_path)
    logger.info(
        "  %s rows in %.1fs (%.0f rows/sec)",
        f"{total_rows:,}",
        pred_time,
        throughput,
    )

    return total_rows, pred_time, throughput


def generate_summary(output_path: str, total_rows: int, pred_time: float, throughput: float):
    """Generate summary statistics from predictions."""
    logger.info("Generating prediction summary...")

    ddf = dd.read_parquet(output_path)
    df = ddf.compute()

    summary = {
        "total_predictions": total_rows,
        "processing_time_seconds": round(pred_time, 2),
        "throughput_rows_per_sec": round(throughput),
        "demand_stats": {
            "mean": round(float(df["predicted_demand"].mean()), 2),
            "median": round(float(df["predicted_demand"].median()), 2),
            "std": round(float(df["predicted_demand"].std()), 2),
            "min": round(float(df["predicted_demand"].min()), 2),
            "max": round(float(df["predicted_demand"].max()), 2),
        },
    }

    if "demand_category" in df.columns:
        cat_counts = df["demand_category"].value_counts().to_dict()
        summary["demand_distribution"] = {str(k): int(v) for k, v in cat_counts.items()}

    # Top-10 community areas by predicted demand
    if "pickup_community_area" in df.columns and "predicted_demand" in df.columns:
        top_areas = df.groupby("pickup_community_area")["predicted_demand"].mean().sort_values(ascending=False).head(10)
        summary["top_demand_areas"] = {str(int(k)): round(float(v), 2) for k, v in top_areas.items()}

    summary_path = Path(output_path) / "prediction_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info("Summary saved to %s", summary_path)

    # Print summary
    print("\n" + "=" * 60)
    print("  BATCH PREDICTION SUMMARY")
    print("=" * 60)
    print(f"  Total predictions:  {total_rows:>12,}")
    print(f"  Processing time:    {pred_time:>11.2f}s")
    print(f"  Throughput:         {throughput:>11,.0f} rows/sec")
    print(f"  Mean demand:        {summary['demand_stats']['mean']:>11.2f}")
    print(f"  Median demand:      {summary['demand_stats']['median']:>11.2f}")
    if "demand_distribution" in summary:
        print("  Demand distribution:")
        for cat, count in sorted(summary["demand_distribution"].items()):
            print(f"    {cat:>12s}: {count:>10,}")
    print("=" * 60 + "\n")


def parse_args():
    parser = argparse.ArgumentParser(description="Batch demand prediction with Dask")
    parser.add_argument(
        "--input",
        default="data/processed/taxi_trips_parquet/hourly_demand",
        help="Path to hourly demand Parquet directory",
    )
    parser.add_argument(
        "--output",
        default="data/processed/taxi_predictions",
        help="Output directory for predictions",
    )
    parser.add_argument(
        "--model",
        default="models/taxi_demand_model.joblib",
        help="Path to trained model",
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Train a new model before predicting",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    total_start = time.time()

    logger.info("=" * 50)
    logger.info("Batch Demand Prediction — Dask")
    logger.info("Input:  %s", args.input)
    logger.info("Output: %s", args.output)
    logger.info("=" * 50)

    # Load or train model
    if args.train or not Path(args.model).exists():
        logger.info("Training new model...")
        model = train_demand_model(args.input, args.model, args.seed)
    else:
        logger.info("Loading model from %s", args.model)
        model = joblib.load(args.model)

    # Batch predict
    total_rows, pred_time, throughput = batch_predict(model, args.input, args.output)

    # Summary
    generate_summary(args.output, total_rows, pred_time, throughput)

    total_time = time.time() - total_start
    logger.info("Total pipeline time: %.1fs", total_time)


if __name__ == "__main__":
    main()
