#!/usr/bin/env python3
"""Generate lightweight test models for CI integration tests.

Creates tiny sklearn pipelines for BankChurn and CarVision so that
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
from sklearn.linear_model import LinearRegression, LogisticRegression
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


def generate_carvision_model():
    """Generate a tiny CarVision model that accepts the real API schema.

    Columns (matches VehicleFeatures Pydantic schema + _prepare_dataframe extras):
        model_year, model, condition, cylinders, fuel, odometer,
        transmission, drive, type, paint_color, is_4wd, date_posted, days_listed
    """
    output = Path("CarVision-Market-Intelligence/models/model.joblib")
    output.parent.mkdir(parents=True, exist_ok=True)

    cat_cols = ["model", "condition", "fuel", "transmission", "drive", "type", "paint_color", "date_posted"]
    num_cols = ["model_year", "cylinders", "odometer", "is_4wd", "days_listed"]

    rows = [
        {
            "model_year": 2015,
            "model": "ford f-150",
            "condition": "good",
            "cylinders": 6.0,
            "fuel": "gas",
            "odometer": 50000.0,
            "transmission": "automatic",
            "drive": "4wd",
            "type": "truck",
            "paint_color": "white",
            "is_4wd": 1.0,
            "date_posted": "2021-01-01",
            "days_listed": 30,
        },
        {
            "model_year": 2012,
            "model": "toyota camry",
            "condition": "fair",
            "cylinders": 4.0,
            "fuel": "gas",
            "odometer": 120000.0,
            "transmission": "automatic",
            "drive": "fwd",
            "type": "sedan",
            "paint_color": "black",
            "is_4wd": 0.0,
            "date_posted": "2021-02-01",
            "days_listed": 15,
        },
        {
            "model_year": 2018,
            "model": "honda civic",
            "condition": "excellent",
            "cylinders": 4.0,
            "fuel": "gas",
            "odometer": 20000.0,
            "transmission": "automatic",
            "drive": "fwd",
            "type": "sedan",
            "paint_color": "blue",
            "is_4wd": 0.0,
            "date_posted": "2021-03-01",
            "days_listed": 7,
        },
        {
            "model_year": 2010,
            "model": "chevrolet silverado 1500",
            "condition": "good",
            "cylinders": 8.0,
            "fuel": "gas",
            "odometer": 90000.0,
            "transmission": "automatic",
            "drive": "4wd",
            "type": "truck",
            "paint_color": "red",
            "is_4wd": 1.0,
            "date_posted": "2021-01-15",
            "days_listed": 45,
        },
        {
            "model_year": 2016,
            "model": "jeep grand cherokee",
            "condition": "good",
            "cylinders": 6.0,
            "fuel": "gas",
            "odometer": 60000.0,
            "transmission": "automatic",
            "drive": "4wd",
            "type": "SUV",
            "paint_color": "silver",
            "is_4wd": 1.0,
            "date_posted": "2021-04-01",
            "days_listed": 20,
        },
        {
            "model_year": 2014,
            "model": "nissan altima",
            "condition": "fair",
            "cylinders": 4.0,
            "fuel": "gas",
            "odometer": 80000.0,
            "transmission": "automatic",
            "drive": "fwd",
            "type": "sedan",
            "paint_color": "white",
            "is_4wd": 0.0,
            "date_posted": "2021-02-15",
            "days_listed": 10,
        },
        {
            "model_year": 2019,
            "model": "ram 1500",
            "condition": "excellent",
            "cylinders": 8.0,
            "fuel": "gas",
            "odometer": 15000.0,
            "transmission": "automatic",
            "drive": "4wd",
            "type": "truck",
            "paint_color": "grey",
            "is_4wd": 1.0,
            "date_posted": "2021-05-01",
            "days_listed": 5,
        },
        {
            "model_year": 2011,
            "model": "ford f-150",
            "condition": "good",
            "cylinders": 6.0,
            "fuel": "gas",
            "odometer": 110000.0,
            "transmission": "manual",
            "drive": "rwd",
            "type": "truck",
            "paint_color": "brown",
            "is_4wd": 0.0,
            "date_posted": "2021-01-20",
            "days_listed": 60,
        },
    ]
    df = pd.DataFrame(rows)
    X = df[cat_cols + num_cols]
    y = np.array([18000.0, 8000.0, 22000.0, 12000.0, 25000.0, 10000.0, 38000.0, 11000.0])

    preprocessor = ColumnTransformer(
        [
            ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), cat_cols),
            ("num", StandardScaler(), num_cols),
        ]
    )
    pipe = Pipeline(
        [
            ("preprocessor", preprocessor),
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
