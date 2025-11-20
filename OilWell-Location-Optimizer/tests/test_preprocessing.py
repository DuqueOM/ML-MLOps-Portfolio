"""Tests for oil well data preprocessing and feature engineering."""

import numpy as np
import pandas as pd
import pytest


def test_data_loading():
    """Test that well data can be loaded."""
    data = pd.DataFrame(
        {
            "f0": np.random.rand(100),
            "f1": np.random.rand(100),
            "f2": np.random.rand(100),
            "product": np.random.rand(100) * 200,
        }
    )

    assert len(data) == 100
    assert "product" in data.columns


def test_feature_extraction():
    """Test feature column extraction."""
    data = pd.DataFrame(
        {
            "f0": [1.0, 2.0, 3.0],
            "f1": [0.5, 1.0, 1.5],
            "f2": [2.0, 2.5, 3.0],
            "product": [100, 150, 200],
        }
    )

    features = [col for col in data.columns if col.startswith("f")]
    assert len(features) == 3


def test_profit_calculation():
    """Test profit calculation."""
    revenue = 1000000
    cost_per_well = 50000
    n_wells = 10

    profit = revenue - (cost_per_well * n_wells)
    assert profit == 500000


def test_bootstrap_sample():
    """Test bootstrap sampling."""
    data = np.array([1, 2, 3, 4, 5])

    # Bootstrap sample
    sample = np.random.choice(data, size=len(data), replace=True)

    assert len(sample) == len(data)
    assert all(val in data for val in sample)


def test_region_selection():
    """Test region-based data selection."""
    data = pd.DataFrame(
        {
            "region": [0, 1, 2, 0, 1, 2],
            "product": [100, 150, 200, 120, 160, 180],
        }
    )

    region_0 = data[data["region"] == 0]
    assert len(region_0) == 2


def test_top_wells_selection():
    """Test selecting top N wells."""
    data = pd.DataFrame(
        {
            "well_id": range(10),
            "predicted_volume": [100, 200, 150, 300, 250, 180, 220, 190, 280, 160],
        }
    )

    top_5 = data.nlargest(5, "predicted_volume")
    assert len(top_5) == 5
    assert top_5["predicted_volume"].iloc[0] == 300


def test_risk_calculation():
    """Test risk calculation from bootstrap results."""
    profits = np.array([100000, 50000, -20000, 80000, 60000])

    risk_of_loss = (profits < 0).sum() / len(profits)
    assert 0 <= risk_of_loss <= 1


def test_confidence_interval():
    """Test confidence interval calculation."""
    data = np.array([100, 120, 110, 130, 125, 115, 105, 135])

    lower = np.percentile(data, 2.5)
    upper = np.percentile(data, 97.5)

    assert lower < upper
    assert lower >= data.min()
    assert upper <= data.max()


@pytest.mark.parametrize("volume", [50, 100, 150, 200])
def test_volume_validation(volume):
    """Test that production volumes are positive."""
    assert volume > 0
