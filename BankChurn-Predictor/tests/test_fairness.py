"""Tests for BankChurn fairness audit module."""

import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from src.bankchurn.fairness import compute_fairness_metrics, compute_group_metrics, run_fairness_audit


class TestComputeGroupMetrics:
    def test_perfect_predictions(self):
        y_true = np.array([1, 0, 1, 0, 1])
        y_pred = np.array([1, 0, 1, 0, 1])
        result = compute_group_metrics(y_true, y_pred)
        assert result["accuracy"] == 1.0
        assert result["precision"] == 1.0
        assert result["recall"] == 1.0
        assert result["f1"] == 1.0
        assert result["n_samples"] == 5

    def test_with_probabilities(self):
        y_true = np.array([1, 0, 1, 0])
        y_pred = np.array([1, 0, 1, 0])
        y_prob = np.array([0.9, 0.1, 0.8, 0.2])
        result = compute_group_metrics(y_true, y_pred, y_prob)
        assert "auc" in result
        assert result["auc"] == 1.0

    def test_empty_group(self):
        result = compute_group_metrics(np.array([]), np.array([]))
        assert result == {}

    def test_positive_rate(self):
        y_true = np.array([1, 0, 0, 0])
        y_pred = np.array([1, 1, 0, 0])
        result = compute_group_metrics(y_true, y_pred)
        assert result["positive_rate"] == 0.5
        assert result["base_rate"] == 0.25

    def test_false_positive_rate(self):
        y_true = np.array([0, 0, 0, 1])
        y_pred = np.array([1, 0, 0, 1])
        result = compute_group_metrics(y_true, y_pred)
        # 1 FP out of 3 negatives
        assert abs(result["false_positive_rate"] - 1 / 3) < 0.01


class TestComputeFairnessMetrics:
    def test_gender_fairness(self):
        y_true = np.array([1, 0, 1, 0, 1, 0, 1, 0])
        y_pred = np.array([1, 0, 1, 0, 1, 1, 0, 0])
        sensitive = pd.DataFrame(
            {
                "Gender": [
                    "Male",
                    "Male",
                    "Male",
                    "Male",
                    "Female",
                    "Female",
                    "Female",
                    "Female",
                ]
            }
        )
        report = compute_fairness_metrics(y_true, y_pred, sensitive)
        assert "Gender" in report
        assert "Male" in report["Gender"]["groups"]
        assert "Female" in report["Gender"]["groups"]
        assert "disparate_impact_ratio" in report["Gender"]["fairness"]

    def test_multiple_attributes(self):
        n = 100
        rng = np.random.RandomState(42)
        y_true = rng.randint(0, 2, n)
        y_pred = rng.randint(0, 2, n)
        sensitive = pd.DataFrame(
            {
                "Gender": rng.choice(["Male", "Female"], n),
                "Geography": rng.choice(["France", "Germany", "Spain"], n),
            }
        )
        report = compute_fairness_metrics(y_true, y_pred, sensitive)
        assert "Gender" in report
        assert "Geography" in report
        assert len(report["Geography"]["groups"]) == 3

    def test_equal_treatment_passes(self):
        # Identical performance across groups should pass
        y_true = np.array([1, 0, 1, 0, 1, 0, 1, 0])
        y_pred = np.array([1, 0, 1, 0, 1, 0, 1, 0])
        sensitive = pd.DataFrame({"Gender": ["M", "M", "M", "M", "F", "F", "F", "F"]})
        report = compute_fairness_metrics(y_true, y_pred, sensitive)
        fi = report["Gender"]["fairness"]
        assert fi["disparate_impact_ratio"] == 1.0
        assert fi["disparate_impact_pass"] is True

    def test_biased_model_detected(self):
        # Model predicts positive only for group A
        y_true = np.array([1, 1, 1, 1, 1, 1, 1, 1])
        y_pred = np.array([1, 1, 1, 1, 0, 0, 0, 0])
        sensitive = pd.DataFrame({"Group": ["A", "A", "A", "A", "B", "B", "B", "B"]})
        report = compute_fairness_metrics(y_true, y_pred, sensitive)
        fi = report["Group"]["fairness"]
        assert fi["disparate_impact_ratio"] == 0.0
        assert fi["disparate_impact_pass"] is False


class TestRunFairnessAudit:
    def test_saves_report(self):
        y_true = np.array([1, 0, 1, 0, 1, 0])
        y_pred = np.array([1, 0, 1, 1, 0, 0])
        sensitive = pd.DataFrame({"Gender": ["M", "M", "M", "F", "F", "F"]})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "fairness_report.json"
            run_fairness_audit(y_true, y_pred, sensitive, output_path=path)
            assert path.exists()
            loaded = json.loads(path.read_text())
            assert "_summary" in loaded
            assert "Gender" in loaded

    def test_summary_overall_pass(self):
        y_true = np.array([1, 0, 1, 0, 1, 0, 1, 0])
        y_pred = np.array([1, 0, 1, 0, 1, 0, 1, 0])
        sensitive = pd.DataFrame({"Gender": ["M", "M", "M", "M", "F", "F", "F", "F"]})
        report = run_fairness_audit(y_true, y_pred, sensitive)
        assert report["_summary"]["overall_pass"] is True

    def test_summary_with_issues(self):
        y_true = np.array([1, 1, 1, 1, 1, 1, 1, 1])
        y_pred = np.array([1, 1, 1, 1, 0, 0, 0, 0])
        sensitive = pd.DataFrame({"Gender": ["M", "M", "M", "M", "F", "F", "F", "F"]})
        report = run_fairness_audit(y_true, y_pred, sensitive)
        assert report["_summary"]["overall_pass"] is False
        assert len(report["_summary"]["issues"]) > 0

    def test_with_probabilities(self):
        y_true = np.array([1, 0, 1, 0, 1, 0])
        y_pred = np.array([1, 0, 1, 0, 1, 0])
        y_prob = np.array([0.9, 0.1, 0.8, 0.2, 0.7, 0.3])
        sensitive = pd.DataFrame({"Gender": ["M", "M", "M", "F", "F", "F"]})
        report = run_fairness_audit(y_true, y_pred, sensitive, y_prob=y_prob)
        assert "auc" in report["Gender"]["groups"]["F"]
