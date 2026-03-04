#!/usr/bin/env python
"""PySpark ETL pipeline for Chicago Taxi Trips (2013-2023).

Processes ~6.3M taxi trip records into partitioned Parquet files with
temporal feature engineering for downstream ML demand prediction.

Pipeline stages:
  1. Ingest   — Read raw CSV (~2.8 GB)
  2. Clean    — Cast types, drop nulls, filter invalid trips
  3. Engineer — Temporal features (hour, day_of_week, month, year, is_weekend)
  4. Aggregate — Hourly demand per pickup community area
  5. Export   — Write partitioned Parquet (by year/month)

Usage:
    python scripts/data_at_scale/spark_etl_taxi.py \
        --input "Taxi_Trips_(2013-2023)_20260304.csv" \
        --output data/processed/taxi_trips_parquet \
        --driver-memory 4g

    # Or process a smaller sample for development:
    python scripts/data_at_scale/spark_etl_taxi.py \
        --input "Taxi_Trips_(2013-2023)_20260304.csv" \
        --output data/processed/taxi_trips_parquet \
        --sample 0.1

Prerequisites:
    pip install pyspark>=3.5
    java -version  # Java 11+ required
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("spark_etl_taxi")

# --- Schema Definition ---
# Explicit schema avoids expensive inferSchema pass over 2.8 GB
TAXI_SCHEMA = T.StructType(
    [
        T.StructField("Trip ID", T.StringType(), True),
        T.StructField("Taxi ID", T.StringType(), True),
        T.StructField("Trip Start Timestamp", T.StringType(), True),
        T.StructField("Trip End Timestamp", T.StringType(), True),
        T.StructField("Trip Seconds", T.StringType(), True),
        T.StructField("Trip Miles", T.StringType(), True),
        T.StructField("Pickup Census Tract", T.StringType(), True),
        T.StructField("Dropoff Census Tract", T.StringType(), True),
        T.StructField("Pickup Community Area", T.StringType(), True),
        T.StructField("Dropoff Community Area", T.StringType(), True),
        T.StructField("Fare", T.StringType(), True),
        T.StructField("Tips", T.StringType(), True),
        T.StructField("Tolls", T.StringType(), True),
        T.StructField("Extras", T.StringType(), True),
        T.StructField("Trip Total", T.StringType(), True),
        T.StructField("Payment Type", T.StringType(), True),
        T.StructField("Company", T.StringType(), True),
        T.StructField("Pickup Centroid Latitude", T.StringType(), True),
        T.StructField("Pickup Centroid Longitude", T.StringType(), True),
        T.StructField("Pickup Centroid Location", T.StringType(), True),
        T.StructField("Dropoff Centroid Latitude", T.StringType(), True),
        T.StructField("Dropoff Centroid Longitude", T.StringType(), True),
        T.StructField("Dropoff Centroid Location", T.StringType(), True),
    ]
)


def create_spark_session(driver_memory: str = "4g") -> SparkSession:
    """Initialize SparkSession with optimized settings for local processing."""
    return (
        SparkSession.builder.appName("ChicagoTaxi-ETL")
        .master("local[*]")
        .config("spark.driver.memory", driver_memory)
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.sql.parquet.compression.codec", "snappy")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.ui.showConsoleProgress", "true")
        .getOrCreate()
    )


def ingest(spark: SparkSession, input_path: str, sample: float | None = None):
    """Stage 1: Read raw CSV with explicit schema."""
    logger.info("Stage 1/5: INGEST — Reading %s", input_path)
    t0 = time.time()

    df = spark.read.csv(input_path, header=True, schema=TAXI_SCHEMA, quote='"')

    if sample and 0.0 < sample < 1.0:
        logger.info("  Sampling %.0f%% of data for development", sample * 100)
        df = df.sample(fraction=sample, seed=42)

    raw_count = df.count()
    logger.info("  Ingested %s rows in %.1fs", f"{raw_count:,}", time.time() - t0)
    return df, raw_count


def clean(df):
    """Stage 2: Cast types, drop nulls, filter invalid trips."""
    logger.info("Stage 2/5: CLEAN — Casting types and filtering")
    t0 = time.time()

    # Parse timestamps — Chicago format: "MM/dd/yyyy hh:mm:ss a"
    df = df.withColumn(
        "trip_start",
        F.to_timestamp("Trip Start Timestamp", "MM/dd/yyyy hh:mm:ss a"),
    )
    df = df.withColumn(
        "trip_end",
        F.to_timestamp("Trip End Timestamp", "MM/dd/yyyy hh:mm:ss a"),
    )

    # Cast numeric columns — strip commas from thousand separators first
    df = df.withColumn(
        "trip_seconds",
        F.regexp_replace(F.col("Trip Seconds"), ",", "").cast(T.IntegerType()),
    )
    df = df.withColumn(
        "trip_miles",
        F.regexp_replace(F.col("Trip Miles"), ",", "").cast(T.DoubleType()),
    )
    df = df.withColumn(
        "pickup_community_area",
        F.regexp_replace(F.col("Pickup Community Area"), ",", "").cast(T.IntegerType()),
    )
    df = df.withColumn(
        "dropoff_community_area",
        F.regexp_replace(F.col("Dropoff Community Area"), ",", "").cast(T.IntegerType()),
    )
    # Strip $ from monetary columns
    df = df.withColumn(
        "fare",
        F.regexp_replace(F.col("Fare"), "[$,]", "").cast(T.DoubleType()),
    )
    df = df.withColumn(
        "tips",
        F.regexp_replace(F.col("Tips"), "[$,]", "").cast(T.DoubleType()),
    )
    df = df.withColumn(
        "trip_total",
        F.regexp_replace(F.col("Trip Total"), "[$,]", "").cast(T.DoubleType()),
    )
    df = df.withColumn("payment_type", F.col("Payment Type"))
    df = df.withColumn("company", F.col("Company"))
    df = df.withColumn(
        "pickup_lat",
        F.col("Pickup Centroid Latitude").cast(T.DoubleType()),
    )
    df = df.withColumn(
        "pickup_lon",
        F.col("Pickup Centroid Longitude").cast(T.DoubleType()),
    )

    # Filter invalid trips
    df_clean = df.filter(
        (F.col("trip_start").isNotNull())
        & (F.col("trip_seconds") > 60)  # At least 1 minute
        & (F.col("trip_seconds") < 86400)  # Less than 24 hours
        & (F.col("trip_miles") > 0.1)  # At least 0.1 miles
        & (F.col("trip_miles") < 500)  # Less than 500 miles
        & (F.col("fare") > 0)  # Positive fare
        & (F.col("pickup_community_area").isNotNull())
    )

    # Select only clean columns
    df_clean = df_clean.select(
        "trip_start",
        "trip_end",
        "trip_seconds",
        "trip_miles",
        "pickup_community_area",
        "dropoff_community_area",
        "fare",
        "tips",
        "trip_total",
        "payment_type",
        "company",
        "pickup_lat",
        "pickup_lon",
    )

    clean_count = df_clean.count()
    logger.info("  Cleaned to %s rows in %.1fs", f"{clean_count:,}", time.time() - t0)
    return df_clean, clean_count


def engineer_features(df):
    """Stage 3: Create temporal and derived features."""
    logger.info("Stage 3/5: ENGINEER — Creating temporal features")
    t0 = time.time()

    df = (
        df.withColumn("year", F.year("trip_start"))
        .withColumn("month", F.month("trip_start"))
        .withColumn("day", F.dayofmonth("trip_start"))
        .withColumn("hour", F.hour("trip_start"))
        .withColumn("day_of_week", F.dayofweek("trip_start"))  # 1=Sun, 7=Sat
        .withColumn(
            "is_weekend",
            F.when(F.dayofweek("trip_start").isin([1, 7]), 1).otherwise(0),
        )
        .withColumn(
            "time_of_day",
            F.when(F.col("hour").between(6, 11), "morning")
            .when(F.col("hour").between(12, 16), "afternoon")
            .when(F.col("hour").between(17, 21), "evening")
            .otherwise("night"),
        )
        # Speed (mph) — useful for detecting anomalies
        .withColumn(
            "speed_mph",
            F.round(F.col("trip_miles") / (F.col("trip_seconds") / 3600.0), 2),
        )
        # Fare per mile
        .withColumn("fare_per_mile", F.round(F.col("fare") / F.col("trip_miles"), 2))
        # Tip percentage
        .withColumn(
            "tip_pct",
            F.round(
                F.when(F.col("fare") > 0, F.col("tips") / F.col("fare") * 100).otherwise(0.0),
                2,
            ),
        )
    )

    # Filter unreasonable speeds
    df = df.filter((F.col("speed_mph") > 1) & (F.col("speed_mph") < 100))

    logger.info("  Feature engineering completed in %.1fs", time.time() - t0)
    return df


def aggregate_hourly_demand(df):
    """Stage 4: Aggregate to hourly demand per community area."""
    logger.info("Stage 4/5: AGGREGATE — Hourly demand per community area")
    t0 = time.time()

    hourly = df.groupBy(
        "year",
        "month",
        "day",
        "hour",
        "day_of_week",
        "is_weekend",
        "pickup_community_area",
    ).agg(
        F.count("*").alias("trip_count"),
        F.round(F.avg("trip_seconds"), 1).alias("avg_duration_seconds"),
        F.round(F.avg("trip_miles"), 2).alias("avg_distance_miles"),
        F.round(F.avg("fare"), 2).alias("avg_fare"),
        F.round(F.avg("tips"), 2).alias("avg_tips"),
        F.round(F.avg("speed_mph"), 2).alias("avg_speed_mph"),
        F.round(F.avg("tip_pct"), 2).alias("avg_tip_pct"),
        F.round(F.sum("trip_total"), 2).alias("total_revenue"),
    )

    agg_count = hourly.count()
    logger.info(
        "  Aggregated to %s rows in %.1fs",
        f"{agg_count:,}",
        time.time() - t0,
    )
    return hourly, agg_count


def export(df_trips, df_hourly, output_dir: str):
    """Stage 5: Write partitioned Parquet files."""
    logger.info("Stage 5/5: EXPORT — Writing partitioned Parquet")
    t0 = time.time()

    trips_path = f"{output_dir}/trips"
    hourly_path = f"{output_dir}/hourly_demand"

    # Trip-level data partitioned by year/month
    df_trips.write.partitionBy("year", "month").mode("overwrite").parquet(trips_path)
    logger.info("  Trip-level data → %s", trips_path)

    # Hourly aggregation (smaller, single partition)
    df_hourly.coalesce(4).write.mode("overwrite").parquet(hourly_path)
    logger.info("  Hourly demand   → %s", hourly_path)

    logger.info("  Export completed in %.1fs", time.time() - t0)


def print_summary(spark, raw_count, clean_count, agg_count, output_dir, total_time):
    """Print processing summary with key statistics."""
    print("\n" + "=" * 70)
    print("  CHICAGO TAXI ETL — PROCESSING SUMMARY")
    print("=" * 70)
    print(f"  Raw rows ingested:     {raw_count:>12,}")
    print(f"  Clean rows retained:   {clean_count:>12,}")
    print(
        f"  Rows dropped:          {raw_count - clean_count:>12,}"
        f"  ({(raw_count - clean_count) / raw_count * 100:.1f}%)"
    )
    print(f"  Hourly demand rows:    {agg_count:>12,}")
    print(f"  Total processing time: {total_time:>11.1f}s")
    print(f"  Throughput:            {raw_count / total_time:>11,.0f} rows/sec")
    print(f"  Output:                {output_dir}/")
    print("=" * 70 + "\n")


def parse_args():
    parser = argparse.ArgumentParser(description="PySpark ETL for Chicago Taxi Trips")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to raw CSV file",
    )
    parser.add_argument(
        "--output",
        default="data/processed/taxi_trips_parquet",
        help="Output directory for Parquet files",
    )
    parser.add_argument(
        "--driver-memory",
        default="4g",
        help="Spark driver memory (default: 4g)",
    )
    parser.add_argument(
        "--sample",
        type=float,
        default=None,
        help="Sample fraction (0.0-1.0) for development runs",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    total_start = time.time()

    logger.info("=" * 50)
    logger.info("Chicago Taxi ETL Pipeline — PySpark")
    logger.info("Input:  %s", args.input)
    logger.info("Output: %s", args.output)
    logger.info("=" * 50)

    # Verify input exists
    if not Path(args.input).exists():
        logger.error("Input file not found: %s", args.input)
        sys.exit(1)

    # Create output directory
    Path(args.output).mkdir(parents=True, exist_ok=True)

    # Initialize Spark
    spark = create_spark_session(args.driver_memory)
    logger.info("Spark UI: %s", spark.sparkContext.uiWebUrl)

    try:
        # Pipeline stages
        df_raw, raw_count = ingest(spark, args.input, args.sample)
        df_clean, clean_count = clean(df_raw)
        df_features = engineer_features(df_clean)
        df_hourly, agg_count = aggregate_hourly_demand(df_features)
        export(df_features, df_hourly, args.output)

        total_time = time.time() - total_start
        print_summary(spark, raw_count, clean_count, agg_count, args.output, total_time)

        # Save processing metadata
        import json

        metadata = {
            "input_file": args.input,
            "raw_rows": raw_count,
            "clean_rows": clean_count,
            "rows_dropped": raw_count - clean_count,
            "drop_rate_pct": round((raw_count - clean_count) / raw_count * 100, 2),
            "hourly_demand_rows": agg_count,
            "processing_time_seconds": round(total_time, 1),
            "throughput_rows_per_sec": round(raw_count / total_time),
            "output_dir": args.output,
            "spark_version": spark.version,
            "partitioning": "year/month",
            "compression": "snappy",
        }
        meta_path = Path(args.output) / "etl_metadata.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)
        logger.info("Metadata saved to %s", meta_path)

    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
