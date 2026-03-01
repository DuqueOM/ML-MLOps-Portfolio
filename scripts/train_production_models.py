#!/usr/bin/env python3
"""
Train production models for all 3 projects using Python 3.11.

This script trains the BEST model configuration for each project
(matching what run_experiments.py identifies as champion) and saves
to the standard path: <project>/models/model.joblib

Usage:
    # With py3.11 conda env (recommended — matches Docker):
    /home/duque_om/miniconda3/envs/ml-py311/bin/python scripts/train_production_models.py

    # With MLflow logging (start MLflow first):
    MLFLOW_TRACKING_URI=http://localhost:5000 /path/to/python scripts/train_production_models.py

Output:
    BankChurn-Predictor/models/model.joblib
    CarVision-Market-Intelligence/models/model.joblib
    NLPInsight-Analyzer/models/model.joblib
"""

import json
import os
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, VotingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
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
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE_DIR = Path(__file__).parent.parent

# Optional MLflow
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "")
mlflow = None
if MLFLOW_URI:
    try:
        import mlflow as _mlflow

        _mlflow.set_tracking_uri(MLFLOW_URI)
        mlflow = _mlflow
        print(f"📡 MLflow tracking: {MLFLOW_URI}")
    except ImportError:
        print("⚠️  mlflow not installed, skipping tracking")


def log_mlflow(experiment, run_name, params, metrics, tags, pipeline, save_path):
    """Log to MLflow if available."""
    if mlflow is None:
        return
    mlflow.set_experiment(experiment)
    with mlflow.start_run(run_name=run_name):
        mlflow.set_tags(tags)
        mlflow.log_params({k: v for k, v in params.items() if not callable(v)})
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(str(save_path))


def rmse(y_true, y_pred):
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


# =============================================================================
# BANKCHURN — VotingClassifier (LR + RF) with balanced weights
# =============================================================================
def train_bankchurn():
    print("\n" + "=" * 60)
    print("🏦 BANKCHURN — Production Model Training")
    print("=" * 60)

    data_path = BASE_DIR / "BankChurn-Predictor/data/raw/Churn_Modelling.csv"
    if not data_path.exists():
        data_path = BASE_DIR / "BankChurn-Predictor/data/raw/Churn.csv"
    if not data_path.exists():
        print("❌ No data file found")
        return None

    df = pd.read_csv(data_path)
    print(f"📊 Loaded {len(df)} rows from {data_path.name}")

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

    preprocessor = ColumnTransformer(
        [
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
                        ("onehot", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore")),
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

    # Production model: VotingClassifier (matches model_card.md)
    pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "classifier",
                VotingClassifier(
                    estimators=[
                        ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=42)),
                        (
                            "rf",
                            RandomForestClassifier(
                                n_estimators=100,
                                max_depth=10,
                                min_samples_split=10,
                                min_samples_leaf=5,
                                class_weight="balanced",
                                random_state=42,
                                n_jobs=-1,
                            ),
                        ),
                    ],
                    voting="soft",
                    weights=[1, 2],
                ),
            ),
        ]
    )

    t0 = time.time()
    pipeline.fit(X_train, y_train)
    train_time = time.time() - t0

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    metrics = {
        "test_accuracy": round(accuracy_score(y_test, y_pred), 4),
        "test_f1": round(f1_score(y_test, y_pred), 4),
        "test_precision": round(precision_score(y_test, y_pred), 4),
        "test_recall": round(recall_score(y_test, y_pred), 4),
        "test_roc_auc": round(roc_auc_score(y_test, y_proba), 4),
        "train_time_seconds": round(train_time, 2),
    }

    # Cross-validation
    cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring="roc_auc", n_jobs=-1)
    metrics["cv_auc_mean"] = round(cv_scores.mean(), 4)
    metrics["cv_auc_std"] = round(cv_scores.std(), 4)

    save_dir = BASE_DIR / "BankChurn-Predictor/models"
    save_dir.mkdir(exist_ok=True)
    save_path = save_dir / "model.joblib"
    joblib.dump(pipeline, save_path)

    print(f"✅ Model saved: {save_path} ({save_path.stat().st_size / 1024:.0f} KB)")
    print(
        f"   AUC: {metrics['test_roc_auc']:.4f} | F1: {metrics['test_f1']:.4f} | "
        f"Precision: {metrics['test_precision']:.4f} | Recall: {metrics['test_recall']:.4f}"
    )
    print(f"   CV AUC: {metrics['cv_auc_mean']:.4f} ± {metrics['cv_auc_std']:.4f}")

    log_mlflow(
        "BankChurn-Predictor",
        "BC-Production_VotingClassifier",
        {
            "model": "VotingClassifier(LR+RF)",
            "voting": "soft",
            "weights": "[1,2]",
            "train_size": len(X_train),
            "test_size": len(X_test),
        },
        metrics,
        {
            "run_type": "production",
            "project": "bankchurn",
            "framework": "scikit-learn",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        },
        pipeline,
        save_path,
    )

    return metrics


# =============================================================================
# CARVISION — RandomForestRegressor (tuned)
# =============================================================================
def train_carvision():
    print("\n" + "=" * 60)
    print("🚗 CARVISION — Production Model Training")
    print("=" * 60)

    data_path = BASE_DIR / "CarVision-Market-Intelligence/data/raw/vehicles_us.csv"
    if not data_path.exists():
        print("❌ No data file found")
        return None

    df = pd.read_csv(data_path)

    # Clean data (matching data.py clean_data filters)
    df = df[(df["price"] >= 1000) & (df["price"] <= 100000)]
    if "year" in df.columns and "model_year" not in df.columns:
        df["model_year"] = df["year"]
    df = df[df["model_year"] >= 1990]
    df = df.dropna(subset=["price"])

    print(f"📊 Loaded {len(df)} rows after cleaning")

    cat_features = ["fuel", "transmission", "type"]
    num_features = ["model_year", "odometer"]

    X = df[cat_features + num_features].copy()
    for col in cat_features:
        X[col] = X[col].fillna("unknown")
    for col in num_features:
        X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0)
    y = df["price"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    preprocessor = ColumnTransformer(
        [
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
                        ("onehot", OneHotEncoder(sparse_output=False, handle_unknown="ignore")),
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

    pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=100,
                    max_depth=12,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    t0 = time.time()
    pipeline.fit(X_train, y_train)
    train_time = time.time() - t0

    y_pred = pipeline.predict(X_test)

    metrics = {
        "test_rmse": round(rmse(y_test, y_pred), 2),
        "test_mae": round(mean_absolute_error(y_test, y_pred), 2),
        "test_r2": round(r2_score(y_test, y_pred), 4),
        "train_time_seconds": round(train_time, 2),
    }

    save_dir = BASE_DIR / "CarVision-Market-Intelligence/models"
    save_dir.mkdir(exist_ok=True)
    save_path = save_dir / "model.joblib"
    joblib.dump(pipeline, save_path)

    # Save feature columns for API compatibility
    feature_columns = cat_features + num_features
    artifacts_dir = BASE_DIR / "CarVision-Market-Intelligence/artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    (artifacts_dir / "feature_columns.json").write_text(json.dumps(feature_columns))

    print(f"✅ Model saved: {save_path} ({save_path.stat().st_size / 1024:.0f} KB)")
    print(f"   R²: {metrics['test_r2']:.4f} | RMSE: ${metrics['test_rmse']:,.0f} | MAE: ${metrics['test_mae']:,.0f}")

    log_mlflow(
        "CarVision-Market-Intelligence",
        "CV-Production_RandomForest",
        {
            "model": "RandomForestRegressor",
            "n_estimators": 100,
            "max_depth": 12,
            "train_size": len(X_train),
            "test_size": len(X_test),
        },
        metrics,
        {
            "run_type": "production",
            "project": "carvision",
            "framework": "scikit-learn",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        },
        pipeline,
        save_path,
    )

    return metrics


# =============================================================================
# NLPINSIGHT — TF-IDF + LogisticRegression (sklearn backend)
# =============================================================================
def train_nlpinsight():
    print("\n" + "=" * 60)
    print("📝 NLPINSIGHT — Production Model Training")
    print("=" * 60)

    data_path = BASE_DIR / "NLPInsight-Analyzer/data/raw/train.csv"
    if not data_path.exists():
        print("❌ No data file found")
        return None

    df = pd.read_csv(data_path)
    print(f"📊 Loaded {len(df)} rows ({df['label'].nunique()} classes)")

    X = df["text"]
    y = df["label_id"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2), sublinear_tf=True)),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )

    t0 = time.time()
    pipeline.fit(X_train, y_train)
    train_time = time.time() - t0

    y_pred = pipeline.predict(X_test)

    metrics = {
        "test_accuracy": round(accuracy_score(y_test, y_pred), 4),
        "test_f1_macro": round(f1_score(y_test, y_pred, average="macro"), 4),
        "test_precision_macro": round(precision_score(y_test, y_pred, average="macro"), 4),
        "test_recall_macro": round(recall_score(y_test, y_pred, average="macro"), 4),
        "train_time_seconds": round(train_time, 2),
    }

    save_dir = BASE_DIR / "NLPInsight-Analyzer/models"
    save_dir.mkdir(exist_ok=True)
    save_path = save_dir / "model.joblib"
    joblib.dump(pipeline, save_path)

    print(f"✅ Model saved: {save_path} ({save_path.stat().st_size / 1024:.0f} KB)")
    print(f"   Accuracy: {metrics['test_accuracy']:.4f} | F1-macro: {metrics['test_f1_macro']:.4f}")

    log_mlflow(
        "NLPInsight-Analyzer",
        "NL-Production_TfIdf_LogReg",
        {
            "model": "LogisticRegression",
            "tfidf_max_features": 5000,
            "train_size": len(X_train),
            "test_size": len(X_test),
            "num_classes": 3,
        },
        metrics,
        {
            "run_type": "production",
            "project": "nlpinsight",
            "framework": "scikit-learn",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        },
        pipeline,
        save_path,
    )

    return metrics


# =============================================================================
# MAIN
# =============================================================================
def main():
    print("=" * 60)
    print("🚀 ML-MLOps Portfolio — Production Model Training")
    print(f"   Python {sys.version}")
    print(f"   sklearn {__import__('sklearn').__version__}")
    print("=" * 60)

    results = {}
    results["bankchurn"] = train_bankchurn()
    results["carvision"] = train_carvision()
    results["nlpinsight"] = train_nlpinsight()

    print("\n" + "=" * 60)
    print("📊 TRAINING SUMMARY")
    print("=" * 60)
    for name, m in results.items():
        if m:
            print(f"  ✅ {name}: {m}")
        else:
            print(f"  ❌ {name}: FAILED")

    # Verify all models exist
    expected = [
        "BankChurn-Predictor/models/model.joblib",
        "CarVision-Market-Intelligence/models/model.joblib",
        "NLPInsight-Analyzer/models/model.joblib",
    ]
    print("\n📦 Model artifacts:")
    for p in expected:
        full = BASE_DIR / p
        if full.exists():
            print(f"  ✅ {p} ({full.stat().st_size / 1024:.0f} KB)")
        else:
            print(f"  ❌ {p} — MISSING")


if __name__ == "__main__":
    main()
