"""Tests for chicagotaxi.features module."""

from __future__ import annotations

from datetime import datetime

from src.chicagotaxi.features import (
    categorize_demand,
    compute_fare_per_mile,
    compute_speed_mph,
    compute_tip_percentage,
    engineer_features,
    extract_day_of_week,
    extract_hour,
    is_weekend,
)


class TestExtractHour:
    def test_morning(self):
        assert extract_hour(datetime(2023, 12, 31, 8, 30)) == 8

    def test_midnight(self):
        assert extract_hour(datetime(2023, 12, 31, 0, 0)) == 0

    def test_noon(self):
        assert extract_hour(datetime(2023, 12, 31, 12, 0)) == 12

    def test_evening(self):
        assert extract_hour(datetime(2023, 12, 31, 23, 59)) == 23


class TestExtractDayOfWeek:
    def test_sunday(self):
        # 2023-12-31 is a Sunday → should be 1
        assert extract_day_of_week(datetime(2023, 12, 31)) == 1

    def test_monday(self):
        # 2024-01-01 is a Monday → should be 2
        assert extract_day_of_week(datetime(2024, 1, 1)) == 2

    def test_saturday(self):
        # 2023-12-30 is a Saturday → should be 7
        assert extract_day_of_week(datetime(2023, 12, 30)) == 7

    def test_wednesday(self):
        # 2024-01-03 is a Wednesday → should be 4
        assert extract_day_of_week(datetime(2024, 1, 3)) == 4

    def test_friday(self):
        # 2024-01-05 is a Friday → should be 6
        assert extract_day_of_week(datetime(2024, 1, 5)) == 6


class TestIsWeekend:
    def test_sunday(self):
        assert is_weekend(1) == 1

    def test_saturday(self):
        assert is_weekend(7) == 1

    def test_monday(self):
        assert is_weekend(2) == 0

    def test_friday(self):
        assert is_weekend(6) == 0

    def test_wednesday(self):
        assert is_weekend(4) == 0


class TestComputeSpeedMph:
    def test_normal_speed(self):
        # 10 miles in 1200 seconds (20 min) = 30 mph
        assert compute_speed_mph(10.0, 1200) == 30.0

    def test_zero_seconds(self):
        assert compute_speed_mph(10.0, 0) == 0.0

    def test_negative_seconds(self):
        assert compute_speed_mph(10.0, -100) == 0.0

    def test_short_trip(self):
        # 1 mile in 120 seconds (2 min) = 30 mph
        assert compute_speed_mph(1.0, 120) == 30.0

    def test_long_trip(self):
        # 60 miles in 3600 seconds (1 hour) = 60 mph
        assert compute_speed_mph(60.0, 3600) == 60.0


class TestComputeFarePerMile:
    def test_normal(self):
        assert compute_fare_per_mile(15.0, 3.0) == 5.0

    def test_zero_miles(self):
        assert compute_fare_per_mile(15.0, 0.0) == 0.0

    def test_negative_miles(self):
        assert compute_fare_per_mile(15.0, -1.0) == 0.0

    def test_high_fare(self):
        assert compute_fare_per_mile(100.0, 10.0) == 10.0


class TestComputeTipPercentage:
    def test_normal(self):
        assert compute_tip_percentage(4.0, 20.0) == 20.0

    def test_zero_fare(self):
        assert compute_tip_percentage(4.0, 0.0) == 0.0

    def test_no_tip(self):
        assert compute_tip_percentage(0.0, 20.0) == 0.0

    def test_generous_tip(self):
        assert compute_tip_percentage(10.0, 20.0) == 50.0

    def test_negative_fare(self):
        assert compute_tip_percentage(4.0, -5.0) == 0.0


class TestEngineerFeatures:
    def test_full_engineering(self):
        row = {
            "trip_seconds": 600,
            "trip_miles": 5.0,
            "fare": 15.0,
            "tips": 3.0,
        }
        ts = datetime(2023, 12, 31, 14, 30)  # Sunday, 2:30 PM
        result = engineer_features(row, ts)

        assert result["hour"] == 14
        assert result["day_of_week"] == 1  # Sunday
        assert result["is_weekend"] == 1
        assert result["year"] == 2023
        assert result["month"] == 12
        assert result["day"] == 31
        assert result["speed_mph"] == 30.0
        assert result["fare_per_mile"] == 3.0
        assert result["tip_percentage"] == 20.0

    def test_weekday(self):
        row = {"trip_seconds": 300, "trip_miles": 2.0, "fare": 10.0, "tips": 0.0}
        ts = datetime(2024, 1, 3, 9, 0)  # Wednesday
        result = engineer_features(row, ts)
        assert result["is_weekend"] == 0
        assert result["day_of_week"] == 4  # Wednesday

    def test_preserves_original_fields(self):
        row = {
            "trip_seconds": 300,
            "trip_miles": 2.0,
            "fare": 10.0,
            "tips": 1.0,
            "extra_field": "keep",
        }
        ts = datetime(2023, 6, 15, 10, 0)
        result = engineer_features(row, ts)
        assert result["extra_field"] == "keep"
        assert result["trip_seconds"] == 300


class TestCategorizeDemand:
    def test_low(self):
        assert categorize_demand(2.0) == "low"

    def test_medium(self):
        assert categorize_demand(10.0) == "medium"

    def test_high(self):
        assert categorize_demand(30.0) == "high"

    def test_very_high(self):
        assert categorize_demand(75.0) == "very_high"

    def test_boundary_low_medium(self):
        assert categorize_demand(5.0) == "medium"

    def test_boundary_medium_high(self):
        assert categorize_demand(20.0) == "high"

    def test_boundary_high_very_high(self):
        assert categorize_demand(50.0) == "very_high"

    def test_zero(self):
        assert categorize_demand(0.0) == "low"

    def test_negative(self):
        assert categorize_demand(-1.0) == "low"
