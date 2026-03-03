"""Tests for NLPInsight NLP classification fairness audit module."""

import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from src.nlpinsight.fairness import (
    compute_fairness_metrics,
    compute_group_metrics,
    compute_per_class_metrics,
    run_fairness_audit,
)

LABELS = ["negative", "neutral", "positive"]


class TestComputeGroupMetrics:
    def test_basic_metrics(self):
        y_true = np.array(["positive", "neutral", "negative", "positive"])
        y_pred = np.array(["positive", "neutral", "neutral", "positive"])
        m = compute_group_metrics(y_true, y_pred, LABELS)

        assert m["n_samples"] == 4
        assert 0 <= m["accuracy"] <= 1
        assert "precision_macro" in m
        assert "recall_macro" in m
        assert "f1_macro" in m

    def test_perfect_predictions(self):
        y_true = np.array(["positive", "neutral", "negative"])
        y_pred = np.array(["positive", "neutral", "negative"])
        m = compute_group_metrics(y_true, y_pred, LABELS)

        assert m["accuracy"] == 1.0
        assert m["f1_macro"] == 1.0

    def test_empty_group(self):
        m = compute_group_metrics(np.array([]), np.array([]))
        assert m == {}


class TestComputePerClassMetrics:
    def test_all_classes_present(self):
        y_true = np.array(["positive", "neutral", "negative", "positive", "neutral"])
        y_pred = np.array(["positive", "neutral", "negative", "neutral", "neutral"])
        result = compute_per_class_metrics(y_true, y_pred, LABELS)

        assert "positive" in result
        assert "neutral" in result
        assert "negative" in result

    def test_perfect_class(self):
        y_true = np.array(["positive", "positive", "negative"])
        y_pred = np.array(["positive", "positive", "negative"])
        result = compute_per_class_metrics(y_true, y_pred, LABELS)

        assert result["positive"]["precision"] == 1.0
        assert result["positive"]["recall"] == 1.0
        assert result["negative"]["f1"] == 1.0

    def test_n_samples_correct(self):
        y_true = np.array(["positive", "positive", "neutral", "negative"])
        y_pred = np.array(["positive", "neutral", "neutral", "negative"])
        result = compute_per_class_metrics(y_true, y_pred, LABELS)

        assert result["positive"]["n_samples"] == 2
        assert result["neutral"]["n_samples"] == 1
        assert result["negative"]["n_samples"] == 1


class TestComputeFairnessMetrics:
    def test_class_parity_present(self):
        y_true = np.array(["positive", "neutral", "negative", "positive", "neutral", "negative"])
        y_pred = np.array(["positive", "neutral", "negative", "positive", "neutral", "negative"])
        report = compute_fairness_metrics(y_true, y_pred, labels=LABELS)

        assert "class_parity" in report
        assert "per_class" in report["class_parity"]
        assert "f1_parity_ratio" in report["class_parity"]

    def test_class_parity_perfect(self):
        y_true = np.array(["positive", "neutral", "negative"] * 3)
        y_pred = np.array(["positive", "neutral", "negative"] * 3)
        report = compute_fairness_metrics(y_true, y_pred, labels=LABELS)

        assert report["class_parity"]["f1_parity_ratio"] == 1.0
        assert report["class_parity"]["f1_parity_pass"] is True

    def test_with_sensitive_features(self):
        y_true = np.array(["positive", "neutral", "negative", "positive"])
        y_pred = np.array(["positive", "neutral", "negative", "positive"])
        sensitive = pd.DataFrame({"text_length_bin": ["short", "short", "long", "long"]})

        report = compute_fairness_metrics(y_true, y_pred, sensitive, labels=LABELS)
        assert "class_parity" in report
        assert "text_length_bin" in report

    def test_group_fairness_indicators(self):
        y_true = np.array(["positive", "neutral", "negative", "positive", "neutral", "negative"])
        y_pred = np.array(["positive", "neutral", "negative", "positive", "neutral", "negative"])
        sensitive = pd.DataFrame({"text_length_bin": ["short", "short", "short", "long", "long", "long"]})

        report = compute_fairness_metrics(y_true, y_pred, sensitive, labels=LABELS)
        fi = report["text_length_bin"]["fairness"]
        assert "f1_parity_ratio" in fi
        assert fi["f1_parity_pass"] is True

    def test_imbalanced_class_detection(self):
        # Model gets negative class completely wrong
        y_true = np.array(["positive", "positive", "neutral", "neutral", "negative", "negative"])
        y_pred = np.array(["positive", "positive", "neutral", "neutral", "positive", "neutral"])
        report = compute_fairness_metrics(y_true, y_pred, labels=LABELS)

        # negative class has 0 recall → low F1 → parity should fail
        cp = report["class_parity"]
        assert cp["per_class"]["negative"]["recall"] == 0.0
        assert cp["f1_parity_pass"] is False


class TestRunFairnessAudit:
    def test_summary_present(self):
        y_true = np.array(["positive", "neutral", "negative"] * 3)
        y_pred = np.array(["positive", "neutral", "negative"] * 3)
        report = run_fairness_audit(y_true, y_pred, labels=LABELS)

        assert "_summary" in report
        assert "overall_pass" in report["_summary"]
        assert "thresholds" in report["_summary"]

    def test_overall_pass_true(self):
        y_true = np.array(["positive", "neutral", "negative"] * 3)
        y_pred = np.array(["positive", "neutral", "negative"] * 3)
        report = run_fairness_audit(y_true, y_pred, labels=LABELS)

        assert report["_summary"]["overall_pass"] is True

    def test_overall_pass_false(self):
        y_true = np.array(["positive", "positive", "neutral", "neutral", "negative", "negative"])
        y_pred = np.array(["positive", "positive", "neutral", "neutral", "positive", "neutral"])
        report = run_fairness_audit(y_true, y_pred, labels=LABELS)

        assert report["_summary"]["overall_pass"] is False
        assert any("FAIL" in issue for issue in report["_summary"]["issues"])

    def test_save_json(self):
        y_true = np.array(["positive", "neutral", "negative"] * 3)
        y_pred = np.array(["positive", "neutral", "negative"] * 3)

        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "fairness.json"
            run_fairness_audit(y_true, y_pred, labels=LABELS, output_path=out)
            assert out.exists()
            data = json.loads(out.read_text())
            assert "_summary" in data

    def test_with_sensitive_features_and_output(self):
        y_true = np.array(["positive", "neutral", "negative", "positive", "neutral", "negative"])
        y_pred = np.array(["positive", "neutral", "negative", "positive", "neutral", "negative"])
        sensitive = pd.DataFrame({"text_length_bin": ["short", "short", "short", "long", "long", "long"]})

        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "fairness.json"
            report = run_fairness_audit(y_true, y_pred, sensitive, labels=LABELS, output_path=out)
            assert report["_summary"]["overall_pass"] is True
            assert "text_length_bin" in report
