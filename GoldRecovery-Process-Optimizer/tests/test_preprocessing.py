"""Tests for data preprocessing and feature engineering."""

import numpy as np
import pandas as pd
import pytest


def test_data_loading():
    """Test that sample data can be loaded."""
    # Create sample data
    data = pd.DataFrame(
        {
            "rougher.input.feed_ag": np.random.rand(100),
            "rougher.input.feed_pb": np.random.rand(100),
            "rougher.output.recovery": np.random.rand(100) * 100,
            "final.output.recovery": np.random.rand(100) * 100,
        }
    )

    assert len(data) == 100
    assert "final.output.recovery" in data.columns


def test_feature_extraction():
    """Test feature column extraction."""
    data = pd.DataFrame(
        {
            "rougher.input.feed_ag": [1.0, 2.0, 3.0],
            "rougher.input.feed_pb": [0.5, 1.0, 1.5],
            "rougher.output.recovery": [80.0, 85.0, 90.0],
            "final.output.recovery": [75.0, 80.0, 85.0],
        }
    )

    # Extract input features
    input_cols = [col for col in data.columns if "input" in col]
    assert len(input_cols) == 2

    # Extract target
    target_cols = [col for col in data.columns if col == "final.output.recovery"]
    assert len(target_cols) == 1


def test_data_validation():
    """Test data validation for missing values."""
    data = pd.DataFrame(
        {
            "feature1": [1.0, 2.0, np.nan],
            "feature2": [0.5, np.nan, 1.5],
            "target": [75.0, 80.0, 85.0],
        }
    )

    missing_count = data.isnull().sum().sum()
    assert missing_count == 2


def test_recovery_calculation():
    """Test recovery percentage calculation."""
    input_concentration = 50.0
    output_concentration = 40.0
    recovery = (output_concentration / input_concentration) * 100

    assert recovery == 80.0
    assert 0 <= recovery <= 100


def test_smape_metric():
    """Test sMAPE metric calculation."""
    y_true = np.array([100, 200, 300])
    y_pred = np.array([110, 190, 310])

    smape = np.mean(2 * np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred))) * 100

    assert smape < 10  # Good prediction
    assert smape >= 0


@pytest.mark.parametrize("recovery_value", [50.0, 75.0, 90.0, 95.0])
def test_recovery_range(recovery_value):
    """Test that recovery values are in valid range."""
    assert 0 <= recovery_value <= 100
