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
from mlflow.data.pandas_dataset import from_pandas
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
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

    # Create MLflow dataset for logging
    bc_dataset = from_pandas(df, source=str(data_path), name="Churn_Modelling", targets="Exited")

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
            mlflow.set_tag("framework", "scikit-learn")
            mlflow.set_tag("task", "binary_classification")
            mlflow.log_input(bc_dataset, context="training")

            # Build pipeline
            pipeline = Pipeline([("preprocessor", preprocessor), ("classifier", exp["model"])])

            # Log params
            model_params = exp["model"].get_params()
            mlflow.log_params({k: v for k, v in model_params.items() if not callable(v) and k != "n_jobs"})
            mlflow.log_param("train_size", len(X_train))
            mlflow.log_param("test_size", len(X_test))
            mlflow.log_param("n_features", X_train.shape[1])

            # Train
            pipeline.fit(X_train, y_train)

            # Predict
            y_train_pred = pipeline.predict(X_train)
            y_test_pred = pipeline.predict(X_test)
            y_test_proba = pipeline.predict_proba(X_test)[:, 1]

            # Metrics (rounded to 4 decimals)
            metrics = {
                "train_accuracy": round(accuracy_score(y_train, y_train_pred), 4),
                "test_accuracy": round(accuracy_score(y_test, y_test_pred), 4),
                "train_f1": round(f1_score(y_train, y_train_pred), 4),
                "test_f1": round(f1_score(y_test, y_test_pred), 4),
                "test_precision": round(precision_score(y_test, y_test_pred), 4),
                "test_recall": round(recall_score(y_test, y_test_pred), 4),
                "test_roc_auc": round(roc_auc_score(y_test, y_test_proba), 4),
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

    # Create MLflow dataset for logging
    cv_dataset = from_pandas(df.head(1000), source=str(data_path), name="vehicles_us", targets="price")

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
            mlflow.set_tag("framework", "scikit-learn")
            mlflow.set_tag("task", "regression")
            mlflow.log_input(cv_dataset, context="training")

            pipeline = Pipeline([("preprocessor", preprocessor), ("regressor", exp["model"])])

            # Log params
            model_params = exp["model"].get_params()
            mlflow.log_params({k: v for k, v in model_params.items() if not callable(v) and k != "n_jobs"})
            mlflow.log_param("train_size", len(X_train))
            mlflow.log_param("test_size", len(X_test))
            mlflow.log_param("n_features", X_train.shape[1])

            pipeline.fit(X_train, y_train)

            y_train_pred = pipeline.predict(X_train)
            y_test_pred = pipeline.predict(X_test)

            metrics = {
                "train_rmse": round(rmse(y_train, y_train_pred), 2),
                "test_rmse": round(rmse(y_test, y_test_pred), 2),
                "train_mae": round(mean_absolute_error(y_train, y_train_pred), 2),
                "test_mae": round(mean_absolute_error(y_test, y_test_pred), 2),
                "train_r2": round(r2_score(y_train, y_train_pred), 4),
                "test_r2": round(r2_score(y_test, y_test_pred), 4),
            }

            mlflow.log_metrics(metrics)

            print(f"   Test RMSE: ${metrics['test_rmse']:,.0f}, R²: {metrics['test_r2']:.4f}")

    print("\n CarVision experiments complete!")


# =============================================================================
# NLPINSIGHT EXPERIMENTS
# =============================================================================


def run_nlpinsight_experiments():
    """Run NLPInsight experiments: TF-IDF + sklearn baselines for sentiment analysis."""
    from sklearn.feature_extraction.text import TfidfVectorizer

    print("\n" + "=" * 60)
    print(" NLPINSIGHT EXPERIMENTS")
    print("=" * 60)

    mlflow.set_experiment("NLPInsight-Analyzer")

    # Load Financial PhraseBank data
    data_path = BASE_DIR / "NLPInsight-Analyzer/data/raw/train.csv"
    if not data_path.exists():
        print(f"  Data not found: {data_path}")
        print("   Run: python scripts/download_financial_phrasebank.py")
        return

    df = pd.read_csv(data_path)
    print(f" Loaded {len(df)} rows ({df['label'].nunique()} classes)")

    # Create MLflow dataset for logging
    nl_dataset = from_pandas(df, source=str(data_path), name="financial_phrasebank", targets="label_id")

    X = df["text"]
    y = df["label_id"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    experiments = [
        {
            "run_name": "NL-1_Baseline_LogReg_TfIdf",
            "tags": {"run_type": "baseline", "project": "nlpinsight"},
            "model": LogisticRegression(max_iter=1000, random_state=42, multi_class="multinomial"),
            "description": "TF-IDF + Logistic Regression baseline for 3-class sentiment",
        },
        {
            "run_name": "NL-2_GradientBoosting_TfIdf",
            "tags": {"run_type": "tuned", "project": "nlpinsight"},
            "model": GradientBoostingClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42),
            "description": "TF-IDF + Gradient Boosting for sentiment analysis",
        },
        {
            "run_name": "NL-3_RandomForest_TfIdf",
            "tags": {"run_type": "alternative", "project": "nlpinsight"},
            "model": RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1),
            "description": "TF-IDF + Random Forest for comparison",
        },
    ]

    tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), sublinear_tf=True)

    for exp in experiments:
        print(f"\n Running: {exp['run_name']}")

        with mlflow.start_run(run_name=exp["run_name"]):
            mlflow.set_tags(exp["tags"])
            mlflow.set_tag("mlflow.note.content", exp["description"])
            mlflow.set_tag("framework", "scikit-learn")
            mlflow.set_tag("task", "multiclass_classification")
            mlflow.log_input(nl_dataset, context="training")

            pipeline = Pipeline([("tfidf", tfidf), ("classifier", exp["model"])])

            model_params = exp["model"].get_params()
            mlflow.log_params({k: v for k, v in model_params.items() if not callable(v) and k != "n_jobs"})
            mlflow.log_param("train_size", len(X_train))
            mlflow.log_param("test_size", len(X_test))
            mlflow.log_param("tfidf_max_features", 5000)
            mlflow.log_param("num_classes", 3)

            pipeline.fit(X_train, y_train)

            y_train_pred = pipeline.predict(X_train)
            y_test_pred = pipeline.predict(X_test)

            metrics = {
                "train_accuracy": round(accuracy_score(y_train, y_train_pred), 4),
                "test_accuracy": round(accuracy_score(y_test, y_test_pred), 4),
                "train_f1_macro": round(f1_score(y_train, y_train_pred, average="macro"), 4),
                "test_f1_macro": round(f1_score(y_test, y_test_pred, average="macro"), 4),
                "test_precision_macro": round(precision_score(y_test, y_test_pred, average="macro"), 4),
                "test_recall_macro": round(recall_score(y_test, y_test_pred, average="macro"), 4),
            }

            mlflow.log_metrics(metrics)

            print(f"   Test Accuracy: {metrics['test_accuracy']:.4f}, F1-macro: {metrics['test_f1_macro']:.4f}")

    print("\n NLPInsight experiments complete!")


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
    run_nlpinsight_experiments()

    print("\n" + "=" * 60)
    print("🎉 ALL EXPERIMENTS COMPLETE!")
    print("=" * 60)
    print(f"\n👉 View results at: {MLFLOW_URI}")
    print("\nExperiments created:")
    print("  • BankChurn-Predictor (3 runs)")
    print("  • CarVision-Market-Intelligence (3 runs)")
    print("  • NLPInsight-Analyzer (3 runs)")


if __name__ == "__main__":
    main()
