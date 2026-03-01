#!/usr/bin/env python3
"""
NLP Drift Detection using Evidently + text-specific metrics.

Detects:
1. Text length distribution drift (input complexity changes)
2. Prediction distribution drift (model confidence shifts)
3. Vocabulary drift (new tokens appearing in production)
4. Evidently DataDriftPreset on extracted text features

Usage:
    python -m monitoring.drift_detection \
        --reference data/raw/train.csv \
        --current data/raw/production_sample.csv \
        --output reports/drift_report.json
"""

from __future__ import annotations

import argparse
import json
import logging
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

logger = logging.getLogger(__name__)


def extract_text_features(df: pd.DataFrame, text_col: str = "text") -> pd.DataFrame:
    """Extract numerical features from text for drift detection.

    Features:
    - text_length: character count
    - word_count: whitespace-split word count
    - avg_word_length: mean characters per word
    - uppercase_ratio: fraction of uppercase characters
    - punctuation_ratio: fraction of punctuation characters
    - digit_ratio: fraction of digit characters
    """
    features = pd.DataFrame(index=df.index)
    texts = df[text_col].fillna("").astype(str)

    features["text_length"] = texts.str.len()
    features["word_count"] = texts.str.split().str.len()
    features["avg_word_length"] = texts.apply(lambda t: np.mean([len(w) for w in t.split()]) if t.strip() else 0)
    features["uppercase_ratio"] = texts.apply(lambda t: sum(1 for c in t if c.isupper()) / max(len(t), 1))
    features["punctuation_ratio"] = texts.apply(lambda t: sum(1 for c in t if c in ".,!?;:'\"()-") / max(len(t), 1))
    features["digit_ratio"] = texts.apply(lambda t: sum(1 for c in t if c.isdigit()) / max(len(t), 1))
    return features


def compute_vocabulary_drift(ref_texts: List[str], cur_texts: List[str], top_k: int = 1000) -> Dict[str, Any]:
    """Detect vocabulary drift between reference and current texts.

    Computes Jaccard similarity of top-K vocabulary and identifies new tokens.
    """
    ref_words = Counter()
    for t in ref_texts:
        ref_words.update(t.lower().split())

    cur_words = Counter()
    for t in cur_texts:
        cur_words.update(t.lower().split())

    ref_top = set(w for w, _ in ref_words.most_common(top_k))
    cur_top = set(w for w, _ in cur_words.most_common(top_k))

    intersection = ref_top & cur_top
    union = ref_top | cur_top
    jaccard = len(intersection) / max(len(union), 1)

    new_tokens = cur_top - ref_top
    disappeared_tokens = ref_top - cur_top

    return {
        "jaccard_similarity": round(jaccard, 4),
        "new_tokens_count": len(new_tokens),
        "disappeared_tokens_count": len(disappeared_tokens),
        "new_tokens_sample": sorted(list(new_tokens))[:20],
        "vocabulary_drift_detected": jaccard < 0.7,
    }


def compute_ks_drift(
    ref_features: pd.DataFrame, cur_features: pd.DataFrame, threshold: float = 0.05
) -> Dict[str, Dict[str, Any]]:
    """Kolmogorov-Smirnov test for each feature."""
    results = {}
    for col in ref_features.columns:
        ref_vals = ref_features[col].dropna().values
        cur_vals = cur_features[col].dropna().values
        if len(ref_vals) < 5 or len(cur_vals) < 5:
            continue
        stat, pvalue = ks_2samp(ref_vals, cur_vals)
        results[col] = {
            "statistic": round(float(stat), 4),
            "p_value": round(float(pvalue), 6),
            "drift_detected": pvalue < threshold,
        }
    return results


def compute_prediction_drift(ref_preds: Optional[np.ndarray], cur_preds: Optional[np.ndarray]) -> Dict[str, Any]:
    """Detect drift in prediction distribution (label balance shift)."""
    if ref_preds is None or cur_preds is None:
        return {"status": "skipped", "reason": "predictions not available"}

    ref_pos_rate = float(np.mean(ref_preds == 1))
    cur_pos_rate = float(np.mean(cur_preds == 1))
    shift = abs(cur_pos_rate - ref_pos_rate)

    return {
        "reference_positive_rate": round(ref_pos_rate, 4),
        "current_positive_rate": round(cur_pos_rate, 4),
        "absolute_shift": round(shift, 4),
        "drift_detected": shift > 0.10,
    }


def run_evidently_report(
    ref_features: pd.DataFrame, cur_features: pd.DataFrame, output_html: Optional[str] = None
) -> Optional[Dict]:
    """Run Evidently DataDriftPreset on extracted text features."""
    try:
        from evidently import Report
        from evidently.presets import DataDriftPreset

        report = Report(metrics=[DataDriftPreset()])
        report.run(reference_data=ref_features, current_data=cur_features)

        if output_html:
            Path(output_html).parent.mkdir(parents=True, exist_ok=True)
            report.save_html(output_html)
            logger.info(f"Evidently HTML report saved: {output_html}")

        result = report.as_dict()
        return result
    except ImportError:
        logger.warning("Evidently not installed — skipping HTML report")
        return None
    except Exception as e:
        logger.warning(f"Evidently report failed: {e}")
        return None


def detect_drift(
    reference_path: str,
    current_path: str,
    text_col: str = "text",
    label_col: str = "label",
    output_path: Optional[str] = None,
    html_output: Optional[str] = None,
) -> Dict[str, Any]:
    """Full drift detection pipeline for NLP data.

    Returns a comprehensive drift report with:
    - Text feature drift (KS tests)
    - Vocabulary drift (Jaccard similarity)
    - Prediction distribution drift (if labels present)
    - Evidently report (if installed)
    """
    logger.info(f"Loading reference: {reference_path}")
    ref_df = pd.read_csv(reference_path)
    logger.info(f"Loading current: {current_path}")
    cur_df = pd.read_csv(current_path)

    # Extract text features
    ref_features = extract_text_features(ref_df, text_col)
    cur_features = extract_text_features(cur_df, text_col)

    # KS drift on text features
    ks_results = compute_ks_drift(ref_features, cur_features)

    # Vocabulary drift
    ref_texts = ref_df[text_col].fillna("").astype(str).tolist()
    cur_texts = cur_df[text_col].fillna("").astype(str).tolist()
    vocab_drift = compute_vocabulary_drift(ref_texts, cur_texts)

    # Prediction drift (if labels exist)
    pred_drift = {}
    if label_col in ref_df.columns and label_col in cur_df.columns:
        pred_drift = compute_prediction_drift(ref_df[label_col].values, cur_df[label_col].values)

    # Evidently report
    evidently_summary = run_evidently_report(ref_features, cur_features, html_output)

    # Aggregate
    any_ks_drift = any(r["drift_detected"] for r in ks_results.values())
    overall_drift = any_ks_drift or vocab_drift.get("vocabulary_drift_detected", False)

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "reference_samples": len(ref_df),
        "current_samples": len(cur_df),
        "overall_drift_detected": overall_drift,
        "text_feature_drift": ks_results,
        "vocabulary_drift": vocab_drift,
        "prediction_drift": pred_drift,
        "evidently_available": evidently_summary is not None,
    }

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Drift report saved: {output_path}")

    drifted = [k for k, v in ks_results.items() if v["drift_detected"]]
    if drifted:
        logger.warning(f"DRIFT DETECTED in features: {drifted}")
    if vocab_drift.get("vocabulary_drift_detected"):
        logger.warning(
            f"VOCABULARY DRIFT: Jaccard={vocab_drift['jaccard_similarity']}, "
            f"new_tokens={vocab_drift['new_tokens_count']}"
        )
    if not overall_drift:
        logger.info("No significant drift detected")

    return report


def main():
    parser = argparse.ArgumentParser(description="NLP Drift Detection")
    parser.add_argument("--reference", required=True, help="Path to reference CSV")
    parser.add_argument("--current", required=True, help="Path to current CSV")
    parser.add_argument("--text-col", default="text", help="Text column name")
    parser.add_argument("--label-col", default="label", help="Label column name")
    parser.add_argument("--output", default="reports/drift_report.json")
    parser.add_argument("--html", default=None, help="Evidently HTML report path")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    report = detect_drift(
        args.reference,
        args.current,
        args.text_col,
        args.label_col,
        args.output,
        args.html,
    )

    if report["overall_drift_detected"]:
        logger.warning("⚠️  DRIFT DETECTED — consider retraining")
        raise SystemExit(1)
    else:
        logger.info("✅ No drift detected")


if __name__ == "__main__":
    main()
