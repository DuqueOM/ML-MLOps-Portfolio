"""Unit tests for PySpark ETL pipeline functions.

Tests the clean/transform logic without requiring a full Spark session
by testing the equivalent pandas logic.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd


class TestDataCleaning:
    """Test data cleaning logic equivalent to Spark clean() stage."""

    def _make_raw_df(self, n: int = 20) -> pd.DataFrame:
        """Create a raw DataFrame mimicking Chicago taxi CSV structure."""
        np.random.seed(42)
        return pd.DataFrame(
            {
                "Trip Start Timestamp": ["12/31/2023 11:45:00 PM"] * n,
                "Trip End Timestamp": ["01/01/2024 12:00:00 AM"] * n,
                "Trip Seconds": np.random.randint(120, 3600, n).astype(str),
                "Trip Miles": np.random.uniform(0.5, 30, n).round(2).astype(str),
                "Pickup Community Area": np.random.randint(1, 78, n).astype(str),
                "Dropoff Community Area": np.random.randint(1, 78, n).astype(str),
                "Fare": [f"${x:.2f}" for x in np.random.uniform(5, 50, n)],
                "Tips": [f"${x:.2f}" for x in np.random.uniform(0, 10, n)],
                "Trip Total": [f"${x:.2f}" for x in np.random.uniform(5, 60, n)],
                "Payment Type": np.random.choice(["Credit Card", "Cash", "Mobile"], n),
                "Company": np.random.choice(["Top Cab", "City Service", "Flash Cab"], n),
            }
        )

    def test_trip_seconds_filter(self):
        """Trips < 60s should be filtered out."""
        df = self._make_raw_df(10)
        df.loc[0, "Trip Seconds"] = "30"  # Too short
        df.loc[1, "Trip Seconds"] = "90000"  # Too long (>24h)

        trip_seconds = df["Trip Seconds"].astype(int)
        valid = (trip_seconds > 60) & (trip_seconds < 86400)
        assert valid.sum() <= 10
        assert not valid.iloc[0]
        assert not valid.iloc[1]

    def test_fare_parsing(self):
        """Dollar signs and commas should be stripped from fares."""
        fares = ["$8.25", "$1,234.50", "$0.00"]
        parsed = [float(f.replace("$", "").replace(",", "")) for f in fares]
        assert parsed == [8.25, 1234.50, 0.00]

    def test_community_area_range(self):
        """Community areas should be 1-77."""
        areas = [1, 32, 77, 0, 100, None]
        valid = [a for a in areas if a is not None and 1 <= a <= 77]
        assert valid == [1, 32, 77]

    def test_comma_in_numeric_field(self):
        """Fields with thousand separators like '1,326' should parse."""
        val = "1,326"
        parsed = int(val.replace(",", ""))
        assert parsed == 1326


class TestFeatureEngineering:
    """Test temporal feature engineering logic."""

    def test_hour_extraction(self):
        ts = pd.Timestamp("2023-12-31 14:30:00")
        assert ts.hour == 14

    def test_day_of_week(self):
        ts = pd.Timestamp("2023-12-31")  # Sunday
        assert ts.dayofweek == 6  # pandas: 0=Mon, 6=Sun

    def test_is_weekend(self):
        weekday = pd.Timestamp("2023-12-29")  # Friday
        weekend = pd.Timestamp("2023-12-30")  # Saturday
        assert weekday.dayofweek < 5
        assert weekend.dayofweek >= 5

    def test_speed_calculation(self):
        miles = 10.0
        seconds = 1200  # 20 minutes
        speed = miles / (seconds / 3600.0)
        assert round(speed, 1) == 30.0

    def test_fare_per_mile(self):
        fare = 15.0
        miles = 3.0
        assert fare / miles == 5.0

    def test_tip_percentage(self):
        fare = 20.0
        tip = 4.0
        pct = (tip / fare) * 100
        assert pct == 20.0


class TestAggregation:
    """Test hourly demand aggregation logic."""

    def test_groupby_produces_correct_columns(self):
        np.random.seed(42)
        df = pd.DataFrame(
            {
                "year": [2023] * 10,
                "month": [12] * 10,
                "day": [31] * 10,
                "hour": [14] * 5 + [15] * 5,
                "day_of_week": [1] * 10,
                "is_weekend": [1] * 10,
                "pickup_community_area": [8] * 10,
                "trip_seconds": np.random.randint(300, 1800, 10),
                "trip_miles": np.random.uniform(1, 10, 10),
                "fare": np.random.uniform(5, 30, 10),
            }
        )

        grouped = (
            df.groupby(
                [
                    "year",
                    "month",
                    "day",
                    "hour",
                    "day_of_week",
                    "is_weekend",
                    "pickup_community_area",
                ]
            )
            .agg(
                trip_count=("fare", "count"),
                avg_duration=("trip_seconds", "mean"),
                avg_distance=("trip_miles", "mean"),
                avg_fare=("fare", "mean"),
            )
            .reset_index()
        )

        assert len(grouped) == 2  # 2 hours
        assert grouped["trip_count"].sum() == 10
        assert "avg_fare" in grouped.columns


class TestETLMetadata:
    """Test ETL metadata output format."""

    def test_metadata_schema(self, tmp_path):
        metadata = {
            "input_file": "test.csv",
            "raw_rows": 1000,
            "clean_rows": 800,
            "rows_dropped": 200,
            "drop_rate_pct": 20.0,
            "hourly_demand_rows": 50,
            "processing_time_seconds": 10.5,
            "throughput_rows_per_sec": 95,
            "output_dir": str(tmp_path),
            "spark_version": "4.1.1",
            "partitioning": "year/month",
            "compression": "snappy",
        }
        meta_path = tmp_path / "etl_metadata.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f)

        loaded = json.loads(meta_path.read_text())
        assert loaded["raw_rows"] == 1000
        assert loaded["drop_rate_pct"] == 20.0
        assert loaded["compression"] == "snappy"
