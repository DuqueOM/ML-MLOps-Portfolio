"""Data cleaning functions for Chicago Taxi pipeline.

Pure-Python implementations of the cleaning logic used in the PySpark ETL.
These functions can be tested without Spark and are used as the canonical
reference for data quality rules.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

# --- Constants ---
COMMUNITY_AREA_MIN = 1
COMMUNITY_AREA_MAX = 77
TRIP_SECONDS_MIN = 60
TRIP_SECONDS_MAX = 86400  # 24 hours
TRIP_MILES_MIN = 0.1
TRIP_MILES_MAX = 500.0
FARE_MIN = 0.0
FARE_MAX = 10_000.0


def strip_currency(value: str) -> float:
    """Strip dollar signs and commas from currency strings.

    Args:
        value: String like '$1,234.50' or '8.25'

    Returns:
        Parsed float value.

    Raises:
        ValueError: If value cannot be parsed.
    """
    if not isinstance(value, str):
        return float(value)
    cleaned = value.replace("$", "").replace(",", "").strip()
    if not cleaned:
        raise ValueError(f"Empty value after stripping: '{value}'")
    return float(cleaned)


def strip_thousands_separator(value: str) -> int:
    """Strip thousand separators from numeric strings.

    Args:
        value: String like '1,326' or '500'

    Returns:
        Parsed integer value.
    """
    if not isinstance(value, str):
        return int(value)
    return int(value.replace(",", "").strip())


def is_valid_trip_seconds(seconds: int) -> bool:
    """Check if trip duration is within valid range.

    Args:
        seconds: Trip duration in seconds.

    Returns:
        True if duration is between 60s and 24h.
    """
    return TRIP_SECONDS_MIN < seconds < TRIP_SECONDS_MAX


def is_valid_trip_miles(miles: float) -> bool:
    """Check if trip distance is within valid range."""
    return TRIP_MILES_MIN <= miles <= TRIP_MILES_MAX


def is_valid_community_area(area: Optional[int]) -> bool:
    """Check if community area ID is valid (1-77)."""
    if area is None:
        return False
    return COMMUNITY_AREA_MIN <= area <= COMMUNITY_AREA_MAX


def is_valid_fare(fare: float) -> bool:
    """Check if fare amount is within valid range."""
    return FARE_MIN <= fare <= FARE_MAX


def clean_row(row: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Apply all cleaning rules to a single row.

    Args:
        row: Dictionary with raw trip data.

    Returns:
        Tuple of (is_valid, cleaned_row). If is_valid is False,
        the row should be dropped.
    """
    try:
        # Parse numeric fields
        trip_seconds = strip_thousands_separator(str(row.get("Trip Seconds", "0")))
        trip_miles = float(str(row.get("Trip Miles", "0")).replace(",", ""))
        fare = strip_currency(str(row.get("Fare", "0")))
        tips = strip_currency(str(row.get("Tips", "0")))
        trip_total = strip_currency(str(row.get("Trip Total", "0")))

        # Parse area IDs
        pickup_area_raw = row.get("Pickup Community Area")
        dropoff_area_raw = row.get("Dropoff Community Area")

        pickup_area = int(float(pickup_area_raw)) if pickup_area_raw else None
        dropoff_area = int(float(dropoff_area_raw)) if dropoff_area_raw else None

        # Apply validation rules
        if not is_valid_trip_seconds(trip_seconds):
            return False, {}
        if not is_valid_trip_miles(trip_miles):
            return False, {}
        if not is_valid_community_area(pickup_area):
            return False, {}
        if not is_valid_fare(fare):
            return False, {}

        return True, {
            "trip_seconds": trip_seconds,
            "trip_miles": trip_miles,
            "fare": fare,
            "tips": tips,
            "trip_total": trip_total,
            "pickup_community_area": pickup_area,
            "dropoff_community_area": dropoff_area,
        }

    except (ValueError, TypeError):
        return False, {}


def compute_drop_rate(raw_count: int, clean_count: int) -> float:
    """Compute the percentage of rows dropped during cleaning.

    Args:
        raw_count: Number of rows before cleaning.
        clean_count: Number of rows after cleaning.

    Returns:
        Drop rate as percentage (0-100).
    """
    if raw_count == 0:
        return 0.0
    return round((1 - clean_count / raw_count) * 100, 2)
