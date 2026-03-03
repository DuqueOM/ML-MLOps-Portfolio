#!/usr/bin/env python3
"""Generate lightweight test models for CI integration tests.

Creates tiny sklearn pipelines for BankChurn and CarVision so that
Docker Compose integration tests can validate predictions without
downloading production models from GCS.

Usage:
    python scripts/generate_ci_test_models.py
"""

import os
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def generate_bankchurn_model():
    """Generate a tiny BankChurn model (LogisticRegression)."""
    output = Path("BankChurn-Predictor/models/model.joblib")
    output.parent.mkdir(parents=True, exist_ok=True)

    np.random.seed(42)
    n = 100
    X = np.random.randn(n, 10)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)

    pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=200)),
        ]
    )
    pipe.fit(X, y)
    joblib.dump(pipe, output)
    print(f"[CI] BankChurn test model saved: {output} ({output.stat().st_size} bytes)")


def generate_carvision_model():
    """Generate a tiny CarVision model (LinearRegression)."""
    output = Path("CarVision-Market-Intelligence/models/model.joblib")
    output.parent.mkdir(parents=True, exist_ok=True)

    np.random.seed(42)
    n = 100
    X = np.random.randn(n, 5)
    y = X[:, 0] * 5000 + X[:, 1] * 3000 + 15000 + np.random.randn(n) * 500

    pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("model", LinearRegression()),
        ]
    )
    pipe.fit(X, y)
    joblib.dump(pipe, output)
    print(f"[CI] CarVision test model saved: {output} ({output.stat().st_size} bytes)")


def main():
    # Run from repo root
    repo_root = Path(__file__).resolve().parent.parent
    os.chdir(repo_root)

    generate_bankchurn_model()
    generate_carvision_model()

    # NLPInsight uses a transformer model — skip in CI unless specifically needed
    nlp_dir = Path("NLPInsight-Analyzer/models")
    nlp_dir.mkdir(parents=True, exist_ok=True)
    print("[CI] NLPInsight models dir created (transformer model skipped in CI)")

    print("[CI] All test models generated successfully")


if __name__ == "__main__":
    main()
