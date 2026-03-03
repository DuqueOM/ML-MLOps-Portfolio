"""Tests for CarVision regression fairness audit module."""

import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from src.carvision.fairness import (
    ERROR_RATIO_THRESHOLD,
    compute_fairness_metrics,
    compute_group_metrics,
    run_fairness_audit,
)


class TestComputeGroupMetrics:
    def test_basic_metrics(self):
        y_true = np.array([10000, 15000, 12000, 18000])
        y_pred = np.array([10500, 14500, 12500, 17000])
        m = compute_group_metrics(y_true, y_pred)

        assert m["n_samples"] == 4
        assert m["mae"] > 0
        assert m["rmse"] >= m["mae"]
        assert "mape" in m
        assert "mean_error" in m
        assert "median_absolute_error" in m

    def test_perfect_predictions(self):
        y_true = np.array([10000.0, 20000.0, 30000.0])
        y_pred = np.array([10000.0, 20000.0, 30000.0])
        m = compute_group_metrics(y_true, y_pred)

        assert m["mae"] == 0.0
        assert m["rmse"] == 0.0
        assert m["mean_error"] == 0.0

    def test_empty_group(self):
        m = compute_group_metrics(np.array([]), np.array([]))
        assert m == {}

    def test_mape_with_zeros(self):
        y_true = np.array([0.0, 10000.0])
        y_pred = np.array([500.0, 10500.0])
        m = compute_group_metrics(y_true, y_pred)
        # MAPE computed only for nonzero y_true
        assert np.isfinite(m["mape"])

    def test_signed_mean_error(self):
        # Predictions consistently over-estimate
        y_true = np.array([10000, 20000])
        y_pred = np.array([12000, 22000])
        m = compute_group_metrics(y_true, y_pred)
        assert m["mean_error"] < 0  # y_true - y_pred < 0 means over-prediction


class TestComputeFairnessMetrics:
    def _make_data(self):
        y_true = np.array([10000, 15000, 12000, 18000, 22000, 13000, 17000, 21000])
        y_pred = np.array([10500, 14500, 12500, 17000, 21500, 13500, 16500, 20500])
        sensitive = pd.DataFrame(
            {
                "fuel": ["gas", "gas", "diesel", "gas", "diesel", "diesel", "gas", "gas"],
            }
        )
        return y_true, y_pred, sensitive

    def test_returns_per_attribute(self):
        y_true, y_pred, sensitive = self._make_data()
        report = compute_fairness_metrics(y_true, y_pred, sensitive)

        assert "fuel" in report
        assert "groups" in report["fuel"]
        assert "fairness" in report["fuel"]

    def test_groups_present(self):
        y_true, y_pred, sensitive = self._make_data()
        report = compute_fairness_metrics(y_true, y_pred, sensitive)

        groups = report["fuel"]["groups"]
        assert "diesel" in groups
        assert "gas" in groups

    def test_error_ratio_computed(self):
        y_true, y_pred, sensitive = self._make_data()
        report = compute_fairness_metrics(y_true, y_pred, sensitive)

        fi = report["fuel"]["fairness"]
        assert "error_ratio" in fi
        assert fi["error_ratio"] >= 1.0

    def test_error_ratio_pass(self):
        y_true, y_pred, sensitive = self._make_data()
        report = compute_fairness_metrics(y_true, y_pred, sensitive)

        fi = report["fuel"]["fairness"]
        # Similar errors across groups → should pass
        assert fi["error_ratio_pass"] is True

    def test_unfair_scenario(self):
        # diesel gets terrible predictions, gas gets perfect
        y_true = np.array([10000, 15000, 12000, 18000])
        y_pred = np.array([10000, 15000, 20000, 10000])
        sensitive = pd.DataFrame({"fuel": ["gas", "gas", "diesel", "diesel"]})

        report = compute_fairness_metrics(y_true, y_pred, sensitive)
        fi = report["fuel"]["fairness"]
        assert fi["error_ratio"] > ERROR_RATIO_THRESHOLD
        assert fi["error_ratio_pass"] is False

    def test_multiple_attributes(self):
        y_true = np.array([10000, 15000, 12000, 18000])
        y_pred = np.array([10500, 14500, 12500, 17500])
        sensitive = pd.DataFrame(
            {
                "fuel": ["gas", "gas", "diesel", "diesel"],
                "type": ["sedan", "suv", "sedan", "suv"],
            }
        )
        report = compute_fairness_metrics(y_true, y_pred, sensitive)
        assert "fuel" in report
        assert "type" in report


class TestRunFairnessAudit:
    def test_summary_present(self):
        y_true = np.array([10000, 15000, 12000, 18000])
        y_pred = np.array([10500, 14500, 12500, 17500])
        sensitive = pd.DataFrame({"fuel": ["gas", "gas", "diesel", "diesel"]})

        report = run_fairness_audit(y_true, y_pred, sensitive)
        assert "_summary" in report
        assert "overall_pass" in report["_summary"]
        assert "thresholds" in report["_summary"]

    def test_overall_pass_true(self):
        y_true = np.array([10000, 15000, 12000, 18000])
        y_pred = np.array([10500, 14500, 12500, 17500])
        sensitive = pd.DataFrame({"fuel": ["gas", "gas", "diesel", "diesel"]})

        report = run_fairness_audit(y_true, y_pred, sensitive)
        assert report["_summary"]["overall_pass"] is True

    def test_overall_pass_false(self):
        y_true = np.array([10000, 15000, 12000, 18000])
        y_pred = np.array([10000, 15000, 20000, 10000])
        sensitive = pd.DataFrame({"fuel": ["gas", "gas", "diesel", "diesel"]})

        report = run_fairness_audit(y_true, y_pred, sensitive)
        assert report["_summary"]["overall_pass"] is False
        assert any("FAIL" in issue for issue in report["_summary"]["issues"])

    def test_save_json(self):
        y_true = np.array([10000, 15000, 12000, 18000])
        y_pred = np.array([10500, 14500, 12500, 17500])
        sensitive = pd.DataFrame({"fuel": ["gas", "gas", "diesel", "diesel"]})

        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "fairness.json"
            run_fairness_audit(y_true, y_pred, sensitive, output_path=out)
            assert out.exists()
            data = json.loads(out.read_text())
            assert "_summary" in data
