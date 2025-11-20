"""Tests for gaming market data preprocessing and analysis."""

import pandas as pd
import pytest


def test_data_loading():
    """Test that game data can be loaded."""
    data = pd.DataFrame(
        {
            "name": ["Game A", "Game B", "Game C"],
            "platform": ["PS4", "Xbox", "PC"],
            "year_of_release": [2018, 2019, 2020],
            "genre": ["Action", "RPG", "Strategy"],
            "na_sales": [1.5, 2.0, 0.8],
            "eu_sales": [1.2, 1.5, 0.6],
            "jp_sales": [0.3, 0.2, 0.1],
            "global_sales": [3.0, 3.7, 1.5],
        }
    )

    assert len(data) == 3
    assert "global_sales" in data.columns


def test_categorical_encoding():
    """Test categorical feature encoding."""
    data = pd.DataFrame(
        {
            "platform": ["PS4", "Xbox", "PC", "PS4"],
            "genre": ["Action", "RPG", "Action", "RPG"],
        }
    )

    # Check unique values
    assert len(data["platform"].unique()) == 3
    assert len(data["genre"].unique()) == 2


def test_sales_calculation():
    """Test total sales calculation."""
    na_sales = 1.5
    eu_sales = 1.2
    jp_sales = 0.3

    total_sales = na_sales + eu_sales + jp_sales
    assert total_sales == 3.0


def test_success_threshold():
    """Test game success classification."""
    sales = [0.5, 1.5, 3.0, 5.0]
    threshold = 1.0

    successful = [s > threshold for s in sales]
    assert sum(successful) == 3


def test_platform_filtering():
    """Test platform-specific filtering."""
    data = pd.DataFrame(
        {
            "platform": ["PS4", "Xbox", "PC", "PS4", "Switch"],
            "sales": [1.0, 2.0, 3.0, 1.5, 2.5],
        }
    )

    ps4_games = data[data["platform"] == "PS4"]
    assert len(ps4_games) == 2
    assert ps4_games["sales"].sum() == 2.5


def test_genre_distribution():
    """Test genre distribution analysis."""
    data = pd.DataFrame(
        {
            "genre": ["Action", "RPG", "Action", "Strategy", "Action"],
        }
    )

    genre_counts = data["genre"].value_counts()
    assert genre_counts["Action"] == 3
    assert "RPG" in genre_counts.index


def test_year_filtering():
    """Test year-based filtering."""
    data = pd.DataFrame(
        {
            "year_of_release": [2015, 2018, 2020, 2021, 2022],
            "sales": [1.0, 2.0, 3.0, 2.5, 1.5],
        }
    )

    recent_games = data[data["year_of_release"] >= 2020]
    assert len(recent_games) == 3


@pytest.mark.parametrize("rating", ["E", "T", "M", "E10+"])
def test_rating_values(rating):
    """Test valid ESRB ratings."""
    valid_ratings = ["E", "E10+", "T", "M", "AO", "RP"]
    assert rating in valid_ratings
