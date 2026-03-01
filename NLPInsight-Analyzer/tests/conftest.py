"""Shared fixtures for NLPInsight tests."""

import sys
from pathlib import Path

import pandas as pd
import pytest

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_texts():
    """Sample texts for testing."""
    return [
        "This movie was absolutely fantastic! I loved every minute.",
        "Terrible experience. The worst service I have ever received.",
        "The product is okay, nothing special but gets the job done.",
        "Incredible performance and outstanding quality. Highly recommend!",
        "Awful. Complete waste of money. Do not buy this.",
    ]


@pytest.fixture
def sample_labels():
    """Sample labels corresponding to sample_texts."""
    return [1, 0, 1, 1, 0]  # positive, negative, positive, positive, negative


@pytest.fixture
def sample_dataframe(sample_texts, sample_labels):
    """Sample DataFrame for testing."""
    return pd.DataFrame({"text": sample_texts, "label": sample_labels})


@pytest.fixture
def config_path():
    """Path to test config."""
    return PROJECT_ROOT / "configs" / "config.yaml"
