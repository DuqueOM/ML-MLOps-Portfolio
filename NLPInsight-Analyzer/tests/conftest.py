"""Shared fixtures for NLPInsight tests."""

from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


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


@pytest.fixture
def fake_tokenizer():
    """Offline stand-in for a HuggingFace tokenizer.

    Mimics the callable interface used by ``TextDataset`` (returns a mapping
    with ``input_ids`` and ``attention_mask`` tensors padded to ``max_length``)
    without any network access, so tests never depend on the HuggingFace Hub.
    """
    torch = pytest.importorskip("torch")

    class _FakeTokenizer:
        def __call__(self, text, max_length=256, padding="max_length", truncation=True, return_tensors="pt"):
            tokens = text.split()[:max_length]
            ids = [hash(tok) % 30000 for tok in tokens]
            attention = [1] * len(ids)
            if padding == "max_length":
                pad = max_length - len(ids)
                ids = ids + [0] * pad
                attention = attention + [0] * pad
            return {
                "input_ids": torch.tensor([ids], dtype=torch.long),
                "attention_mask": torch.tensor([attention], dtype=torch.long),
            }

    return _FakeTokenizer()
