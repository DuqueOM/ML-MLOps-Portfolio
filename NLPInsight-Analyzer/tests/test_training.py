"""Tests for NLPInsight training pipeline."""

import numpy as np

from src.nlpinsight.training import compute_metrics


class TestComputeMetrics:
    def test_perfect_predictions(self):
        logits = np.array([[0.1, 0.9], [0.9, 0.1], [0.1, 0.9]])
        labels = np.array([1, 0, 1])
        result = compute_metrics((logits, labels))
        assert result["accuracy"] == 1.0
        assert result["f1"] == 1.0
        assert result["precision"] == 1.0
        assert result["recall"] == 1.0

    def test_wrong_predictions(self):
        logits = np.array([[0.1, 0.9], [0.1, 0.9]])
        labels = np.array([0, 0])
        result = compute_metrics((logits, labels))
        assert result["accuracy"] == 0.0

    def test_mixed_predictions(self):
        logits = np.array([[0.9, 0.1], [0.1, 0.9], [0.9, 0.1], [0.9, 0.1]])
        labels = np.array([0, 1, 1, 0])
        result = compute_metrics((logits, labels))
        assert 0 < result["accuracy"] < 1
        assert "f1" in result
        assert "precision" in result
        assert "recall" in result

    def test_returns_float(self):
        logits = np.array([[0.9, 0.1], [0.1, 0.9]])
        labels = np.array([0, 1])
        result = compute_metrics((logits, labels))
        for v in result.values():
            assert isinstance(v, float)
