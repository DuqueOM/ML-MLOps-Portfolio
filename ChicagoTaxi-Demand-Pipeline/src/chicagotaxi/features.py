"""Feature engineering functions for Chicago Taxi pipeline.

Pure-Python implementations of the temporal and derived features
used in the PySpark ETL pipeline. Testable without Spark.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


def extract_hour(timestamp: datetime) -> int:
    """Extract hour of day from timestamp."""
    return timestamp.hour


def extract_day_of_week(timestamp: datetime) -> int:
    """Extract day of week (1=Sunday, 7=Saturday).

    Matches Spark's dayofweek() convention (1=Sun, 7=Sat).
    Python's weekday() returns 0=Mon, 6=Sun.
    """
    # Python: 0=Mon..6=Sun → Spark: 1=Sun..7=Sat
    py_dow = timestamp.weekday()  # 0=Mon, 6=Sun
    return (py_dow + 2) % 7 or 7  # Convert to 1=Sun..7=Sat


def is_weekend(day_of_week: int) -> int:
    """Check if day is weekend (Saturday=7 or Sunday=1).

    Args:
        day_of_week: Day in Spark convention (1=Sun, 7=Sat).

    Returns:
        1 if weekend, 0 if weekday.
    """
    return 1 if day_of_week in (1, 7) else 0


def compute_speed_mph(miles: float, seconds: int) -> float:
    """Compute average speed in miles per hour.

    Args:
        miles: Trip distance in miles.
        seconds: Trip duration in seconds.

    Returns:
        Speed in mph, or 0.0 if seconds is 0.
    """
    if seconds <= 0:
        return 0.0
    return round(miles / (seconds / 3600.0), 2)


def compute_fare_per_mile(fare: float, miles: float) -> float:
    """Compute fare per mile.

    Args:
        fare: Trip fare amount.
        miles: Trip distance in miles.

    Returns:
        Fare per mile, or 0.0 if miles is 0.
    """
    if miles <= 0:
        return 0.0
    return round(fare / miles, 2)


def compute_tip_percentage(tip: float, fare: float) -> float:
    """Compute tip as percentage of fare.

    Args:
        tip: Tip amount.
        fare: Fare amount.

    Returns:
        Tip percentage (0-100+), or 0.0 if fare is 0.
    """
    if fare <= 0:
        return 0.0
    return round((tip / fare) * 100, 2)


def engineer_features(row: Dict[str, Any], timestamp: datetime) -> Dict[str, Any]:
    """Apply all feature engineering to a cleaned row.

    Args:
        row: Cleaned row dict with trip_seconds, trip_miles, fare, tips.
        timestamp: Trip start timestamp.

    Returns:
        Dict with all engineered features added.
    """
    result = dict(row)

    # Temporal features
    result["hour"] = extract_hour(timestamp)
    result["day_of_week"] = extract_day_of_week(timestamp)
    result["is_weekend"] = is_weekend(result["day_of_week"])
    result["year"] = timestamp.year
    result["month"] = timestamp.month
    result["day"] = timestamp.day

    # Derived features
    seconds = row.get("trip_seconds", 0)
    miles = row.get("trip_miles", 0.0)
    fare = row.get("fare", 0.0)
    tips = row.get("tips", 0.0)

    result["speed_mph"] = compute_speed_mph(miles, seconds)
    result["fare_per_mile"] = compute_fare_per_mile(fare, miles)
    result["tip_percentage"] = compute_tip_percentage(tips, fare)

    return result


def categorize_demand(predicted_demand: float) -> str:
    """Categorize predicted demand into buckets.

    Args:
        predicted_demand: Predicted trip count per hour/area.

    Returns:
        Category string: 'low', 'medium', 'high', or 'very_high'.
    """
    if predicted_demand < 5:
        return "low"
    elif predicted_demand < 20:
        return "medium"
    elif predicted_demand < 50:
        return "high"
    else:
        return "very_high"
