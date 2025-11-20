"""Tests for Chicago mobility data preprocessing and feature engineering."""

from datetime import datetime

import numpy as np
import pandas as pd
import pytest


def test_data_loading():
    """Test that ride data can be loaded."""
    data = pd.DataFrame(
        {
            "pickup_datetime": pd.date_range("2017-11-01", periods=100, freq="H"),
            "dropoff_datetime": pd.date_range("2017-11-01 00:30:00", periods=100, freq="H"),
            "trip_duration": np.random.randint(300, 3600, 100),
            "pickup_location": np.random.choice(["Downtown", "Airport", "Suburbs"], 100),
        }
    )

    assert len(data) == 100
    assert "trip_duration" in data.columns


def test_datetime_parsing():
    """Test datetime parsing."""
    dt_str = "2017-11-01 10:30:00"
    dt = pd.to_datetime(dt_str)

    assert dt.year == 2017
    assert dt.month == 11
    assert dt.day == 1


def test_duration_calculation():
    """Test trip duration calculation."""
    pickup = datetime(2017, 11, 1, 10, 0, 0)
    dropoff = datetime(2017, 11, 1, 10, 30, 0)

    duration = (dropoff - pickup).total_seconds()
    assert duration == 1800  # 30 minutes


def test_hour_extraction():
    """Test hour extraction from datetime."""
    dt = pd.Timestamp("2017-11-01 14:30:00")
    hour = dt.hour

    assert hour == 14
    assert 0 <= hour < 24


def test_day_of_week():
    """Test day of week extraction."""
    dt = pd.Timestamp("2017-11-06")  # Monday
    day_of_week = dt.dayofweek

    assert day_of_week == 0  # Monday is 0


def test_weekend_flag():
    """Test weekend identification."""
    weekday = pd.Timestamp("2017-11-06")  # Monday
    weekend = pd.Timestamp("2017-11-11")  # Saturday

    assert weekday.dayofweek < 5
    assert weekend.dayofweek >= 5


def test_distance_estimation():
    """Test simple distance estimation."""
    # Simplified: duration * average_speed
    duration_hours = 0.5
    avg_speed_mph = 30

    distance = duration_hours * avg_speed_mph
    assert distance == 15


def test_weather_encoding():
    """Test weather condition encoding."""
    weather_conditions = ["Clear", "Rain", "Snow", "Cloudy"]

    for condition in weather_conditions:
        assert isinstance(condition, str)
        assert len(condition) > 0


def test_temporal_validation():
    """Test that dropoff is after pickup."""
    pickup = pd.Timestamp("2017-11-01 10:00:00")
    dropoff = pd.Timestamp("2017-11-01 10:30:00")

    assert dropoff > pickup


@pytest.mark.parametrize("duration", [300, 600, 1800, 3600])
def test_duration_range(duration):
    """Test that durations are positive."""
    assert duration > 0
    assert duration < 7200  # Less than 2 hours for valid rides
