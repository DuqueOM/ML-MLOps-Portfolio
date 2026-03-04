"""Tests for chicagotaxi.cleaning module."""

from __future__ import annotations

import pytest

from src.chicagotaxi.cleaning import (
    clean_row,
    compute_drop_rate,
    is_valid_community_area,
    is_valid_fare,
    is_valid_trip_miles,
    is_valid_trip_seconds,
    strip_currency,
    strip_thousands_separator,
)


class TestStripCurrency:
    def test_dollar_sign(self):
        assert strip_currency("$8.25") == 8.25

    def test_dollar_with_comma(self):
        assert strip_currency("$1,234.50") == 1234.50

    def test_plain_number(self):
        assert strip_currency("42.00") == 42.00

    def test_zero(self):
        assert strip_currency("$0.00") == 0.00

    def test_large_amount(self):
        assert strip_currency("$12,345,678.99") == 12345678.99

    def test_float_passthrough(self):
        assert strip_currency(8.25) == 8.25

    def test_int_passthrough(self):
        assert strip_currency(100) == 100.0

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            strip_currency("$")

    def test_whitespace(self):
        assert strip_currency("  $15.00  ") == 15.00


class TestStripThousandsSeparator:
    def test_with_comma(self):
        assert strip_thousands_separator("1,326") == 1326

    def test_without_comma(self):
        assert strip_thousands_separator("500") == 500

    def test_large_number(self):
        assert strip_thousands_separator("1,234,567") == 1234567

    def test_int_passthrough(self):
        assert strip_thousands_separator(42) == 42

    def test_whitespace(self):
        assert strip_thousands_separator(" 1,000 ") == 1000


class TestIsValidTripSeconds:
    def test_valid_short_trip(self):
        assert is_valid_trip_seconds(120) is True

    def test_valid_long_trip(self):
        assert is_valid_trip_seconds(3600) is True

    def test_too_short(self):
        assert is_valid_trip_seconds(30) is False

    def test_exactly_60(self):
        assert is_valid_trip_seconds(60) is False  # > 60, not >=

    def test_exactly_86400(self):
        assert is_valid_trip_seconds(86400) is False  # < 86400, not <=

    def test_too_long(self):
        assert is_valid_trip_seconds(100000) is False

    def test_zero(self):
        assert is_valid_trip_seconds(0) is False

    def test_negative(self):
        assert is_valid_trip_seconds(-100) is False


class TestIsValidTripMiles:
    def test_valid_short(self):
        assert is_valid_trip_miles(0.5) is True

    def test_valid_long(self):
        assert is_valid_trip_miles(30.0) is True

    def test_minimum_boundary(self):
        assert is_valid_trip_miles(0.1) is True

    def test_below_minimum(self):
        assert is_valid_trip_miles(0.05) is False

    def test_maximum_boundary(self):
        assert is_valid_trip_miles(500.0) is True

    def test_above_maximum(self):
        assert is_valid_trip_miles(501.0) is False

    def test_zero(self):
        assert is_valid_trip_miles(0.0) is False


class TestIsValidCommunityArea:
    def test_valid_area(self):
        assert is_valid_community_area(32) is True

    def test_area_1(self):
        assert is_valid_community_area(1) is True

    def test_area_77(self):
        assert is_valid_community_area(77) is True

    def test_area_0(self):
        assert is_valid_community_area(0) is False

    def test_area_78(self):
        assert is_valid_community_area(78) is False

    def test_area_none(self):
        assert is_valid_community_area(None) is False

    def test_area_negative(self):
        assert is_valid_community_area(-1) is False


class TestIsValidFare:
    def test_valid_fare(self):
        assert is_valid_fare(15.0) is True

    def test_zero_fare(self):
        assert is_valid_fare(0.0) is True

    def test_large_fare(self):
        assert is_valid_fare(9999.99) is True

    def test_negative_fare(self):
        assert is_valid_fare(-5.0) is False

    def test_over_max(self):
        assert is_valid_fare(10001.0) is False


class TestCleanRow:
    def _make_row(self, **overrides):
        base = {
            "Trip Seconds": "600",
            "Trip Miles": "5.0",
            "Fare": "$15.00",
            "Tips": "$3.00",
            "Trip Total": "$18.00",
            "Pickup Community Area": "8",
            "Dropoff Community Area": "32",
        }
        base.update(overrides)
        return base

    def test_valid_row(self):
        valid, cleaned = clean_row(self._make_row())
        assert valid is True
        assert cleaned["trip_seconds"] == 600
        assert cleaned["trip_miles"] == 5.0
        assert cleaned["fare"] == 15.0
        assert cleaned["tips"] == 3.0
        assert cleaned["pickup_community_area"] == 8

    def test_short_trip_rejected(self):
        valid, _ = clean_row(self._make_row(**{"Trip Seconds": "30"}))
        assert valid is False

    def test_zero_miles_rejected(self):
        valid, _ = clean_row(self._make_row(**{"Trip Miles": "0.0"}))
        assert valid is False

    def test_invalid_area_rejected(self):
        valid, _ = clean_row(self._make_row(**{"Pickup Community Area": "0"}))
        assert valid is False

    def test_missing_area_rejected(self):
        valid, _ = clean_row(self._make_row(**{"Pickup Community Area": ""}))
        assert valid is False

    def test_comma_in_seconds(self):
        valid, cleaned = clean_row(self._make_row(**{"Trip Seconds": "1,326"}))
        assert valid is True
        assert cleaned["trip_seconds"] == 1326

    def test_currency_fare(self):
        valid, cleaned = clean_row(self._make_row(**{"Fare": "$1,234.50"}))
        assert valid is True
        assert cleaned["fare"] == 1234.50

    def test_malformed_data_returns_false(self):
        valid, _ = clean_row({"Trip Seconds": "abc", "Trip Miles": "xyz"})
        assert valid is False


class TestComputeDropRate:
    def test_normal_drop(self):
        assert compute_drop_rate(1000, 800) == 20.0

    def test_no_drop(self):
        assert compute_drop_rate(1000, 1000) == 0.0

    def test_all_dropped(self):
        assert compute_drop_rate(1000, 0) == 100.0

    def test_zero_input(self):
        assert compute_drop_rate(0, 0) == 0.0

    def test_real_values(self):
        assert compute_drop_rate(6364313, 5369172) == 15.64
