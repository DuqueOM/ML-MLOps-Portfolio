#!/usr/bin/env python3
"""
Run all MLflow experiments for the portfolio demo.

This script executes multiple training runs across all 3 projects,
logging everything to MLflow at http://localhost:5000.

Usage:
    python scripts/run_experiments.py
"""

import os
import sys
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Configure MLflow
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(MLFLOW_URI)

print(f"🎯 MLflow Tracking URI: {MLFLOW_URI}")

BASE_DIR = Path(__file__).parent.parent


def rmse(y_true, y_pred):
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


# =============================================================================
# BANKCHURN EXPERIMENTS
# =============================================================================


def run_bankchurn_experiments():
    """Run BankChurn experiments: baseline, tuned, overfit."""
    print("\n" + "=" * 60)
    print("🏦 BANKCHURN EXPERIMENTS")
    print("=" * 60)

    mlflow.set_experiment("BankChurn-Predictor")

    # Load data
    data_path = BASE_DIR / "BankChurn-Predictor/data/raw/Churn_Modelling.csv"
    if not data_path.exists():
        print(f"⚠️  Data not found: {data_path}")
        return

    df = pd.read_csv(data_path)
    print(f"📊 Loaded {len(df)} rows")

    # Features
    cat_features = ["Geography", "Gender"]
    num_features = [
        "CreditScore",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
        "EstimatedSalary",
    ]
    target = "Exited"

    X = df[cat_features + num_features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Preprocessor
    preprocessor = ColumnTransformer(
        [
            (
                "cat",
                Pipeline(
                    [
                        (
                            "imputer",
                            SimpleImputer(strategy="constant", fill_value="missing"),
                        ),
                        (
                            "onehot",
                            OneHotEncoder(
                                drop="first",
                                sparse_output=False,
                                handle_unknown="ignore",
                            ),
                        ),
                    ]
                ),
                cat_features,
            ),
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                num_features,
            ),
        ]
    )

    # Experiment configs
    experiments = [
        {
            "run_name": "BC-1_Baseline",
            "tags": {"run_type": "baseline", "project": "bankchurn"},
            "model": LogisticRegression(C=1.0, max_iter=1000, random_state=42),
            "description": "Simple logistic regression baseline",
        },
        {
            "run_name": "BC-2_RandomForest_Tuned",
            "tags": {"run_type": "tuned", "project": "bankchurn"},
            "model": RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=10,
                min_samples_leaf=5,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            ),
            "description": "Tuned Random Forest with balanced weights",
        },
        {
            "run_name": "BC-3_Overfit_Demo",
            "tags": {"run_type": "overfit", "project": "bankchurn"},
            "model": RandomForestClassifier(
                n_estimators=200,
                max_depth=30,  # Too deep
                min_samples_split=2,
                min_samples_leaf=1,  # No regularization
                random_state=42,
                n_jobs=-1,
            ),
            "description": "Overfitted model to show trade-offs",
        },
    ]

    for exp in experiments:
        print(f"\n🚀 Running: {exp['run_name']}")

        with mlflow.start_run(run_name=exp["run_name"]):
            mlflow.set_tags(exp["tags"])
            mlflow.set_tag("mlflow.note.content", exp["description"])

            # Build pipeline
            pipeline = Pipeline([("preprocessor", preprocessor), ("classifier", exp["model"])])

            # Log params
            model_params = exp["model"].get_params()
            mlflow.log_params({k: v for k, v in model_params.items() if not callable(v) and k != "n_jobs"})

            # Train
            pipeline.fit(X_train, y_train)

            # Predict
            y_train_pred = pipeline.predict(X_train)
            y_test_pred = pipeline.predict(X_test)
            y_test_proba = pipeline.predict_proba(X_test)[:, 1]

            # Metrics
            metrics = {
                "train_accuracy": accuracy_score(y_train, y_train_pred),
                "test_accuracy": accuracy_score(y_test, y_test_pred),
                "train_f1": f1_score(y_train, y_train_pred),
                "test_f1": f1_score(y_test, y_test_pred),
                "test_roc_auc": roc_auc_score(y_test, y_test_proba),
            }

            mlflow.log_metrics(metrics)

            print(f"   Test F1: {metrics['test_f1']:.4f}, AUC: {metrics['test_roc_auc']:.4f}")

    print("\n BankChurn experiments complete!")


# =============================================================================
# CARVISION EXPERIMENTS
# =============================================================================


def run_carvision_experiments():
    """Run CarVision experiments: baseline, tuned, gradient boosting."""
    print("\n" + "=" * 60)
    print(" CARVISION EXPERIMENTS")
    print("=" * 60)

    mlflow.set_experiment("CarVision-Market-Intelligence")

    # Load data
    data_path = BASE_DIR / "CarVision-Market-Intelligence/data/raw/vehicles_us.csv"
    if not data_path.exists():
        print(f"  Data not found: {data_path}")
        return

    df = pd.read_csv(data_path)

    # Clean data
    df = df[(df["price"] >= 1000) & (df["price"] <= 100000)]
    df = df[((df["model_year"] >= 1990) | (df["year"] >= 1990) if "year" in df.columns else (df["model_year"] >= 1990))]
    df = df.dropna(subset=["price"])

    # Rename year if needed
    if "year" in df.columns and "model_year" not in df.columns:
        df["model_year"] = df["year"]

    print(f" Loaded {len(df)} rows after cleaning")

    # Features
    cat_features = ["fuel", "transmission", "type"]
    num_features = ["model_year", "odometer"]
    target = "price"

    # Filter to available columns
    cat_features = [c for c in cat_features if c in df.columns]
    num_features = [c for c in num_features if c in df.columns]

    if not cat_features or not num_features:
        print("  Required columns not found")
        return

    X = df[cat_features + num_features].copy()
    for col in cat_features:
        X[col] = X[col].fillna("unknown")
    for col in num_features:
        X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0)

    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Preprocessor
    preprocessor = ColumnTransformer(
        [
            (
                "cat",
                Pipeline(
                    [
                        (
                            "imputer",
                            SimpleImputer(strategy="constant", fill_value="unknown"),
                        ),
                        (
                            "onehot",
                            OneHotEncoder(sparse_output=False, handle_unknown="ignore"),
                        ),
                    ]
                ),
                cat_features,
            ),
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                num_features,
            ),
        ]
    )

    experiments = [
        {
            "run_name": "CV-1_Baseline_Ridge",
            "tags": {"run_type": "baseline", "project": "carvision"},
            "model": Ridge(alpha=1.0, random_state=42),
            "description": "Simple Ridge regression baseline",
        },
        {
            "run_name": "CV-2_RandomForest_Tuned",
            "tags": {"run_type": "tuned", "project": "carvision"},
            "model": RandomForestRegressor(
                n_estimators=100,
                max_depth=12,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            ),
            "description": "Tuned Random Forest regressor",
        },
        {
            "run_name": "CV-3_GradientBoosting",
            "tags": {"run_type": "alternative", "project": "carvision"},
            "model": GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42),
            "description": "Gradient Boosting for comparison",
        },
    ]

    for exp in experiments:
        print(f"\n Running: {exp['run_name']}")

        with mlflow.start_run(run_name=exp["run_name"]):
            mlflow.set_tags(exp["tags"])
            mlflow.set_tag("mlflow.note.content", exp["description"])

            pipeline = Pipeline([("preprocessor", preprocessor), ("regressor", exp["model"])])

            # Log params
            model_params = exp["model"].get_params()
            mlflow.log_params({k: v for k, v in model_params.items() if not callable(v) and k != "n_jobs"})

            pipeline.fit(X_train, y_train)

            y_train_pred = pipeline.predict(X_train)
            y_test_pred = pipeline.predict(X_test)

            metrics = {
                "train_rmse": rmse(y_train, y_train_pred),
                "test_rmse": rmse(y_test, y_test_pred),
                "train_mae": mean_absolute_error(y_train, y_train_pred),
                "test_mae": mean_absolute_error(y_test, y_test_pred),
                "train_r2": r2_score(y_train, y_train_pred),
                "test_r2": r2_score(y_test, y_test_pred),
            }

            mlflow.log_metrics(metrics)

            print(f"   Test RMSE: ${metrics['test_rmse']:,.0f}, R²: {metrics['test_r2']:.4f}")

    print("\n CarVision experiments complete!")


# =============================================================================
# TELECOMAI EXPERIMENTS
# =============================================================================


def run_telecom_experiments():
    """Run TelecomAI experiments: baseline, tuned."""
    print("\n" + "=" * 60)
    print(" TELECOMAI EXPERIMENTS")
    print("=" * 60)

    mlflow.set_experiment("TelecomAI-Customer-Intelligence")

    # Load data
    data_path = BASE_DIR / "TelecomAI-Customer-Intelligence/data/raw/users_behavior.csv"
    if not data_path.exists():
        print(f"  Data not found: {data_path}")
        # Try synthetic
        print("   Creating synthetic data...")
        np.random.seed(42)
        n = 500
        df = pd.DataFrame(
            {
                "calls": np.random.uniform(20, 100, n),
                "minutes": np.random.uniform(100, 500, n),
                "messages": np.random.uniform(10, 100, n),
                "mb_used": np.random.uniform(5000, 30000, n),
                "is_ultra": np.random.choice([0, 1], n, p=[0.7, 0.3]),
            }
        )
    else:
        df = pd.read_csv(data_path)

    print(f" Loaded {len(df)} rows")

    features = ["calls", "minutes", "messages", "mb_used"]
    target = "is_ultra"

    # Ensure columns exist
    for col in features:
        if col not in df.columns:
            df[col] = np.random.uniform(0, 100, len(df))

    if target not in df.columns:
        df[target] = np.random.choice([0, 1], len(df))

    X = df[features].fillna(0)
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    experiments = [
        {
            "run_name": "TL-1_Baseline_LogReg",
            "tags": {"run_type": "baseline", "project": "telecom"},
            "model": LogisticRegression(max_iter=1000, random_state=42),
            "description": "Logistic Regression baseline",
        },
        {
            "run_name": "TL-2_GradientBoosting_Tuned",
            "tags": {"run_type": "tuned", "project": "telecom"},
            "model": GradientBoostingClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42),
            "description": "Tuned Gradient Boosting classifier",
        },
        {
            "run_name": "TL-3_RandomForest",
            "tags": {"run_type": "alternative", "project": "telecom"},
            "model": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1),
            "description": "Random Forest for comparison",
        },
    ]

    preprocessor = Pipeline([("scaler", StandardScaler())])

    for exp in experiments:
        print(f"\n Running: {exp['run_name']}")

        with mlflow.start_run(run_name=exp["run_name"]):
            mlflow.set_tags(exp["tags"])
            mlflow.set_tag("mlflow.note.content", exp["description"])

            pipeline = Pipeline([("preprocessor", preprocessor), ("classifier", exp["model"])])

            model_params = exp["model"].get_params()
            mlflow.log_params({k: v for k, v in model_params.items() if not callable(v) and k != "n_jobs"})

            pipeline.fit(X_train, y_train)

            y_train_pred = pipeline.predict(X_train)
            y_test_pred = pipeline.predict(X_test)

            try:
                y_test_proba = pipeline.predict_proba(X_test)[:, 1]
                test_auc = roc_auc_score(y_test, y_test_proba)
            except Exception:
                test_auc = 0.0

            metrics = {
                "train_accuracy": accuracy_score(y_train, y_train_pred),
                "test_accuracy": accuracy_score(y_test, y_test_pred),
                "train_f1": f1_score(y_train, y_train_pred),
                "test_f1": f1_score(y_test, y_test_pred),
                "test_roc_auc": test_auc,
            }

            mlflow.log_metrics(metrics)

            print(f"   Test Accuracy: {metrics['test_accuracy']:.4f}, F1: {metrics['test_f1']:.4f}")

    print("\n TelecomAI experiments complete!")


# =============================================================================
# MAIN
# =============================================================================


def main():
    print("=" * 60)
    print("🚀 ML-MLOps Portfolio - Running All Experiments")
    print("=" * 60)
    print(f"📡 MLflow Server: {MLFLOW_URI}")

    # Check MLflow connection
    try:
        import requests

        r = requests.get(f"{MLFLOW_URI}/health", timeout=5)
        if r.text == "OK":
            print("✅ MLflow server is healthy\n")
        else:
            print(f"⚠️  MLflow response: {r.text}")
    except Exception as e:
        print(f"❌ Cannot connect to MLflow: {e}")
        print("   Make sure: docker compose -f docker-compose.demo.yml up -d")
        sys.exit(1)

    # Run all experiments
    run_bankchurn_experiments()
    run_carvision_experiments()
    run_telecom_experiments()

    print("\n" + "=" * 60)
    print("🎉 ALL EXPERIMENTS COMPLETE!")
    print("=" * 60)
    print(f"\n👉 View results at: {MLFLOW_URI}")
    print("\nExperiments created:")
    print("  • BankChurn-Predictor (3 runs)")
    print("  • CarVision-Market-Intelligence (3 runs)")
    print("  • TelecomAI-Customer-Intelligence (3 runs)")


if __name__ == "__main__":
    main()
