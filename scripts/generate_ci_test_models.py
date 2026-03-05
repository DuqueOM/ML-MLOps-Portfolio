#!/usr/bin/env python3
"""Generate lightweight test models for CI integration tests.

Creates tiny sklearn pipelines for BankChurn so that
Docker Compose integration tests can validate predictions without
downloading production models from GCS.

The pipelines use ColumnTransformer to handle categorical string inputs
exactly as the real API endpoints receive them (e.g. Geography='France',
model='ford f-150'), so integration tests pass end-to-end.

Usage:
    python scripts/generate_ci_test_models.py
"""

import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, StandardScaler


def generate_bankchurn_model():
    """Generate a tiny BankChurn model that accepts the real API schema.

    Columns (matches CustomerData Pydantic schema):
        CreditScore, Geography, Gender, Age, Tenure, Balance,
        NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary
    """
    output = Path("BankChurn-Predictor/models/model.joblib")
    output.parent.mkdir(parents=True, exist_ok=True)

    cat_cols = ["Geography", "Gender"]
    num_cols = [
        "CreditScore",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
        "EstimatedSalary",
    ]

    rows = [
        {
            "CreditScore": 619,
            "Geography": "France",
            "Gender": "Female",
            "Age": 42,
            "Tenure": 2,
            "Balance": 0.0,
            "NumOfProducts": 1,
            "HasCrCard": 1,
            "IsActiveMember": 1,
            "EstimatedSalary": 101348.88,
        },
        {
            "CreditScore": 608,
            "Geography": "Spain",
            "Gender": "Female",
            "Age": 41,
            "Tenure": 1,
            "Balance": 83807.86,
            "NumOfProducts": 1,
            "HasCrCard": 0,
            "IsActiveMember": 1,
            "EstimatedSalary": 112542.58,
        },
        {
            "CreditScore": 502,
            "Geography": "France",
            "Gender": "Female",
            "Age": 42,
            "Tenure": 8,
            "Balance": 159660.80,
            "NumOfProducts": 3,
            "HasCrCard": 1,
            "IsActiveMember": 0,
            "EstimatedSalary": 113931.57,
        },
        {
            "CreditScore": 699,
            "Geography": "France",
            "Gender": "Female",
            "Age": 39,
            "Tenure": 1,
            "Balance": 0.0,
            "NumOfProducts": 2,
            "HasCrCard": 0,
            "IsActiveMember": 0,
            "EstimatedSalary": 93826.63,
        },
        {
            "CreditScore": 850,
            "Geography": "Spain",
            "Gender": "Female",
            "Age": 43,
            "Tenure": 2,
            "Balance": 125510.82,
            "NumOfProducts": 1,
            "HasCrCard": 1,
            "IsActiveMember": 1,
            "EstimatedSalary": 79084.10,
        },
        {
            "CreditScore": 645,
            "Geography": "Germany",
            "Gender": "Male",
            "Age": 44,
            "Tenure": 8,
            "Balance": 113755.78,
            "NumOfProducts": 2,
            "HasCrCard": 1,
            "IsActiveMember": 0,
            "EstimatedSalary": 149756.71,
        },
        {
            "CreditScore": 722,
            "Geography": "France",
            "Gender": "Male",
            "Age": 50,
            "Tenure": 7,
            "Balance": 0.0,
            "NumOfProducts": 2,
            "HasCrCard": 1,
            "IsActiveMember": 1,
            "EstimatedSalary": 10062.80,
        },
        {
            "CreditScore": 376,
            "Geography": "Germany",
            "Gender": "Female",
            "Age": 29,
            "Tenure": 4,
            "Balance": 115046.74,
            "NumOfProducts": 4,
            "HasCrCard": 1,
            "IsActiveMember": 0,
            "EstimatedSalary": 119346.88,
        },
    ]
    df = pd.DataFrame(rows)
    X = df[cat_cols + num_cols]
    y = np.array([1, 0, 1, 0, 0, 1, 0, 1])

    preprocessor = ColumnTransformer(
        [
            ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), cat_cols),
            ("num", StandardScaler(), num_cols),
        ]
    )
    pipe = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("model", LogisticRegression(max_iter=200)),
        ]
    )
    pipe.fit(X, y)
    joblib.dump(pipe, output)
    print(f"[CI] BankChurn test model saved: {output} ({output.stat().st_size} bytes)")


def generate_nlpinsight_model():
    """Generate a tiny NLPInsight model (TF-IDF + LogisticRegression).

    The SentimentPredictor looks for model.joblib in the models dir and
    falls back to transformer loading if not found.  Providing a joblib
    pipeline lets the Docker Compose integration test pass without
    downloading the production FinBERT transformer.

    Labels: 0=negative, 1=neutral, 2=positive  (matches LABEL_MAP).
    """
    from sklearn.feature_extraction.text import TfidfVectorizer

    output = Path("NLPInsight-Analyzer/models/model.joblib")
    output.parent.mkdir(parents=True, exist_ok=True)

    texts = [
        "Earnings fell sharply in Q3",
        "Revenue declined significantly",
        "The company reported steady results",
        "Market conditions remained stable",
        "Strong quarterly growth exceeded expectations",
        "Profit surged to record highs",
        "Losses mounted amid weak demand",
        "Stock plummeted after guidance cut",
        "Operations continued as normal",
        "Flat sales matched analyst estimates",
        "Outstanding performance across all segments",
        "Revenue hit an all-time high",
    ]
    labels = np.array([0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 2, 2])

    pipe = Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=200)),
            ("clf", LogisticRegression(max_iter=200)),
        ]
    )
    pipe.fit(texts, labels)
    joblib.dump(pipe, output)
    print(f"[CI] NLPInsight test model saved: {output} ({output.stat().st_size} bytes)")


def main():
    # Run from repo root
    repo_root = Path(__file__).resolve().parent.parent
    os.chdir(repo_root)

    generate_bankchurn_model()
    generate_nlpinsight_model()

    print("[CI] All test models generated successfully")


if __name__ == "__main__":
    main()
