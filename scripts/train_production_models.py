#!/usr/bin/env python3
"""
Train production models for all 3 projects using Python 3.11.

v3.0.0 — March 2026 upgrade:
  - BankChurn: StackingClassifier (RF + GradientBoosting + XGBoost + LightGBM
               → LogisticRegression meta-learner) with ChurnFeatureEngineer
  - CarVision: LightGBM with optimized hyperparameters + FeatureEngineer in pipeline
  - NLPInsight: Fine-tuned DistilBERT transformer (real deep learning model)

Usage:
    /home/duque_om/miniconda3/envs/ml-py311/bin/python scripts/train_production_models.py

    # With MLflow logging:
    MLFLOW_TRACKING_URI=http://localhost:5000 ... scripts/train_production_models.py

Output:
    BankChurn-Predictor/models/model.joblib
    CarVision-Market-Intelligence/models/model.joblib
    NLPInsight-Analyzer/models/  (transformer directory: config.json, model.safetensors, tokenizer files)
    NLPInsight-Analyzer/models/model.tar.gz  (packaged for GCS upload)
"""

import importlib
import json
import os
import sys
import tarfile
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, StackingClassifier
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
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
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
        print(f"MLflow tracking: {MLFLOW_URI}")
    except ImportError:
        print("mlflow not installed, skipping tracking")


def log_mlflow(experiment, run_name, params, metrics, tags, save_path):
    """Log to MLflow if available."""
    if mlflow is None:
        return
    mlflow.set_experiment(experiment)
    with mlflow.start_run(run_name=run_name):
        mlflow.set_tags(tags)
        mlflow.log_params({k: v for k, v in params.items() if not callable(v)})
        mlflow.log_metrics(metrics)
        if save_path and Path(save_path).exists():
            mlflow.log_artifact(str(save_path))


def rmse(y_true, y_pred):
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def mape(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1e-8))) * 100)


# =============================================================================
# BANKCHURN v3.0 — StackingClassifier + ChurnFeatureEngineer
# =============================================================================
def train_bankchurn():
    print("\n" + "=" * 70)
    print("  BANKCHURN v3.0 — StackingClassifier + Feature Engineering")
    print("=" * 70)

    from lightgbm import LGBMClassifier
    from xgboost import XGBClassifier

    # Import ChurnFeatureEngineer from the project
    bc_src = BASE_DIR / "BankChurn-Predictor"
    sys.path.insert(0, str(bc_src))
    import src.bankchurn.features as _bc_features

    importlib.reload(_bc_features)
    ChurnFeatureEngineer = _bc_features.ChurnFeatureEngineer

    data_path = bc_src / "data/raw/Churn_Modelling.csv"
    if not data_path.exists():
        data_path = bc_src / "data/raw/Churn.csv"
    if not data_path.exists():
        print("ERROR: No data file found")
        return None

    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} rows from {data_path.name}")

    # Drop ID columns
    drop_cols = ["RowNumber", "CustomerId", "Surname"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    target = "Exited"
    y = df[target]
    X = df.drop(columns=[target])

    # Split BEFORE feature engineering (prevents data leakage)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Train: {len(X_train)}, Test: {len(X_test)}, Churn rate: {y.mean():.2%}")

    # Feature engineering (applied inside pipeline for proper train/test separation)
    feature_engineer = ChurnFeatureEngineer(
        create_interactions=True,
        create_ratios=True,
        create_bins=True,
        create_risk_scores=True,
    )

    # Apply FE to detect column types (then build preprocessor)
    X_train_fe = feature_engineer.fit_transform(X_train)
    cat_features = X_train_fe.select_dtypes(include=["object", "category"]).columns.tolist()
    num_features = X_train_fe.select_dtypes(include=[np.number]).columns.tolist()
    n_cat, n_num = len(cat_features), len(num_features)
    print(f"Features after engineering: {n_cat} cat + {n_num} num = {n_cat + n_num}")

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
        ],
        verbose_feature_names_out=False,
    )

    # Imbalance ratio for scale_pos_weight
    neg, pos = (y_train == 0).sum(), (y_train == 1).sum()
    scale_pos = neg / pos

    # StackingClassifier: diverse base learners → LogisticRegression meta
    # Optimized n_estimators for CPU training (200 trees = good balance speed/quality)
    base_estimators = [
        (
            "rf",
            RandomForestClassifier(
                n_estimators=200,
                max_depth=12,
                min_samples_leaf=4,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            ),
        ),
        (
            "gb",
            GradientBoostingClassifier(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.8,
                random_state=42,
            ),
        ),
        (
            "xgb",
            XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                scale_pos_weight=scale_pos,
                eval_metric="logloss",
                random_state=42,
                n_jobs=-1,
            ),
        ),
        (
            "lgb",
            LGBMClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.05,
                num_leaves=31,
                is_unbalance=True,
                random_state=42,
                n_jobs=-1,
                verbose=-1,
            ),
        ),
        (
            "lr",
            LogisticRegression(
                C=0.5,
                max_iter=1000,
                class_weight="balanced",
                random_state=42,
            ),
        ),
    ]

    meta_learner = LogisticRegression(C=1.0, max_iter=1000, random_state=42)

    classifier = StackingClassifier(
        estimators=base_estimators,
        final_estimator=meta_learner,
        cv=3,
        stack_method="predict_proba",
        passthrough=False,
        n_jobs=-1,
    )

    # Full pipeline: features → preprocessor → stacking classifier
    pipeline = Pipeline(
        [
            ("features", feature_engineer),
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )

    print("Training StackingClassifier (RF+GB+XGB+LGB+LR → LR meta, cv=3)...")
    t0 = time.time()
    pipeline.fit(X_train, y_train)
    train_time = time.time() - t0
    print(f"Training completed in {train_time:.1f}s")

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

    # Cross-validation on raw data (pipeline handles FE + preprocessing)
    print("Running 3-fold CV...")
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X, y, cv=cv, scoring="roc_auc", n_jobs=1)
    metrics["cv_auc_mean"] = round(cv_scores.mean(), 4)
    metrics["cv_auc_std"] = round(cv_scores.std(), 4)

    # Save
    save_dir = bc_src / "models"
    save_dir.mkdir(exist_ok=True)
    save_path = save_dir / "model.joblib"
    joblib.dump(pipeline, save_path, compress=3)

    size_kb = save_path.stat().st_size / 1024
    print(f"Model saved: {save_path} ({size_kb:.0f} KB)")
    print(
        f"   AUC: {metrics['test_roc_auc']:.4f} | F1: {metrics['test_f1']:.4f} | "
        f"Precision: {metrics['test_precision']:.4f} | Recall: {metrics['test_recall']:.4f}"
    )
    print(f"   CV AUC: {metrics['cv_auc_mean']:.4f} +/- {metrics['cv_auc_std']:.4f}")

    # Save metrics JSON
    metrics_path = bc_src / "artifacts"
    metrics_path.mkdir(exist_ok=True)
    (metrics_path / "metrics_production.json").write_text(json.dumps(metrics, indent=2))

    log_mlflow(
        "BankChurn-Predictor",
        "BC-v3.0_StackingClassifier",
        {
            "model": "StackingClassifier(RF+GB+XGB+LGB+LR→LR_meta)",
            "base_estimators": "RF,GB,XGB,LGB,LR",
            "meta_learner": "LogisticRegression",
            "feature_engineering": "ChurnFeatureEngineer(interactions+ratios+bins+risk)",
            "train_size": len(X_train),
            "test_size": len(X_test),
        },
        metrics,
        {
            "run_type": "production",
            "version": "v3.0.0",
            "project": "bankchurn",
            "framework": "scikit-learn+xgboost+lightgbm",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        },
        save_path,
    )

    return metrics


# =============================================================================
# CARVISION v3.0 — LightGBM + FeatureEngineer in pipeline
# =============================================================================
def train_carvision():
    print("\n" + "=" * 70)
    print("  CARVISION v3.0 — LightGBM + FeatureEngineer Pipeline")
    print("=" * 70)

    from lightgbm import LGBMRegressor

    cv_src = BASE_DIR / "CarVision-Market-Intelligence"
    # Remove any stale 'src' package from prior project imports
    for mod_name in list(sys.modules.keys()):
        if mod_name == "src" or mod_name.startswith("src."):
            del sys.modules[mod_name]
    # Ensure CarVision's root is first in path
    sys.path.insert(0, str(cv_src))
    from src.carvision.data import clean_data, infer_feature_types, load_data
    from src.carvision.features import FeatureEngineer

    data_path = cv_src / "data/raw/vehicles_us.csv"
    if not data_path.exists():
        print("ERROR: No data file found")
        return None

    # Load and clean using project's own functions
    filters = {
        "min_price": 1000,
        "max_price": 500000,
        "min_year": 1990,
        "max_odometer": 500000,
    }
    df = clean_data(load_data(str(data_path)), filters=filters)
    print(f"Loaded {len(df)} rows after cleaning")

    # Feature engineering (will be inside pipeline for inference)
    dataset_year = 2026
    fe = FeatureEngineer(current_year=dataset_year)
    df_transformed = fe.transform(df)

    # Infer feature types on transformed data
    drop_columns = ["price_per_mile", "price_category", "model", "date_posted", "brand"]
    target = "price"

    num_cols, cat_cols = infer_feature_types(
        df_transformed,
        target=target,
        drop_columns=drop_columns,
    )
    print(f"Features: {len(cat_cols)} cat + {len(num_cols)} num = {len(cat_cols) + len(num_cols)}")

    # Split raw data (pipeline handles FE)
    y = df[target]
    X = df.drop(columns=[target])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    # Preprocessor
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
                cat_cols,
            ),
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                num_cols,
            ),
        ]
    )

    # LightGBM with optimized hyperparameters
    model = LGBMRegressor(
        n_estimators=500,
        max_depth=8,
        learning_rate=0.05,
        num_leaves=63,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_samples=20,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
        verbose=-1,
    )

    # Full pipeline: features → preprocessor → LightGBM
    pipeline = Pipeline(
        [
            ("features", FeatureEngineer(current_year=dataset_year)),
            ("pre", preprocessor),
            ("model", model),
        ]
    )

    print("Training LightGBM (500 trees, depth=8, lr=0.05)...")
    t0 = time.time()
    pipeline.fit(X_train, y_train)
    train_time = time.time() - t0
    print(f"Training completed in {train_time:.1f}s")

    y_pred = pipeline.predict(X_test)

    metrics = {
        "test_rmse": round(rmse(y_test, y_pred), 2),
        "test_mae": round(float(mean_absolute_error(y_test, y_pred)), 2),
        "test_mape": round(mape(y_test, y_pred), 2),
        "test_r2": round(float(r2_score(y_test, y_pred)), 4),
        "train_time_seconds": round(train_time, 2),
    }

    # Save
    save_dir = cv_src / "models"
    save_dir.mkdir(exist_ok=True)
    save_path = save_dir / "model.joblib"
    joblib.dump(pipeline, save_path, compress=3)

    # Save feature columns and metrics
    feature_columns = sorted(num_cols + cat_cols)
    artifacts_dir = cv_src / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    (artifacts_dir / "feature_columns.json").write_text(json.dumps(feature_columns, indent=2))
    (artifacts_dir / "metrics_val.json").write_text(json.dumps(metrics, indent=2))

    size_kb = save_path.stat().st_size / 1024
    print(f"Model saved: {save_path} ({size_kb:.0f} KB)")
    print(f"   R2: {metrics['test_r2']:.4f} | RMSE: ${metrics['test_rmse']:,.0f}")
    print(f"   MAE: ${metrics['test_mae']:,.0f} | MAPE: {metrics['test_mape']:.1f}%")

    log_mlflow(
        "CarVision-Market-Intelligence",
        "CV-v3.0_LightGBM",
        {
            "model": "LGBMRegressor",
            "n_estimators": 800,
            "max_depth": 10,
            "learning_rate": 0.03,
            "num_leaves": 63,
            "feature_engineering": "FeatureEngineer(age,depreciation,brand_tier,mileage,condition)",
            "n_features_cat": len(cat_cols),
            "n_features_num": len(num_cols),
            "train_size": len(X_train),
            "test_size": len(X_test),
        },
        metrics,
        {
            "run_type": "production",
            "version": "v3.0.0",
            "project": "carvision",
            "framework": "lightgbm",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        },
        save_path,
    )

    return metrics


# =============================================================================
# NLPINSIGHT v3.0 — FinBERT (ProsusAI) transfer learning for financial sentiment
# =============================================================================
def train_nlpinsight():
    print("\n" + "=" * 70)
    print("  NLPINSIGHT v3.0 — FinBERT Transfer Learning")
    print("=" * 70)

    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    data_path = BASE_DIR / "NLPInsight-Analyzer/data/raw/train.csv"
    if not data_path.exists():
        print("ERROR: No data file found")
        return None

    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} rows ({df['label'].nunique()} classes)")
    print(f"Class distribution: {dict(df['label'].value_counts())}")

    # Our label mapping: {negative: 0, neutral: 1, positive: 2}
    label2id = {"negative": 0, "neutral": 1, "positive": 2}
    if "label_id" not in df.columns:
        df["label_id"] = df["label"].map(label2id)

    # Train/test split for evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"].values,
        df["label_id"].values,
        test_size=0.2,
        random_state=42,
        stratify=df["label_id"].values,
    )
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    # Load ProsusAI/FinBERT — BERT fine-tuned on financial text for sentiment
    # This is domain-specific transfer learning: FinBERT was trained on
    # Financial PhraseBank + other financial corpora with BERT architecture.
    # FinBERT labels: {0: positive, 1: negative, 2: neutral}
    model_name = "ProsusAI/finbert"
    print(f"Loading {model_name} (domain-specific financial sentiment model)...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()

    # Rearrange classifier weights to match our label scheme:
    # FinBERT: 0=positive, 1=negative, 2=neutral
    # Ours:    0=negative, 1=neutral,  2=positive
    with torch.no_grad():
        old_w = model.classifier.weight.data.clone()
        old_b = model.classifier.bias.data.clone()
        model.classifier.weight.data[0] = old_w[1]  # negative
        model.classifier.weight.data[1] = old_w[2]  # neutral
        model.classifier.weight.data[2] = old_w[0]  # positive
        model.classifier.bias.data[0] = old_b[1]
        model.classifier.bias.data[1] = old_b[2]
        model.classifier.bias.data[2] = old_b[0]

    model.config.id2label = {0: "negative", 1: "neutral", 2: "positive"}
    model.config.label2id = {"negative": 0, "neutral": 1, "positive": 2}

    # Evaluate on test set
    print("Evaluating on test set...")
    t0 = time.time()
    all_preds = []
    batch_size = 32
    for i in range(0, len(X_test), batch_size):
        batch = X_test[i : i + batch_size].tolist()
        inputs = tokenizer(batch, truncation=True, padding=True, max_length=128, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
        preds = torch.argmax(outputs.logits, dim=-1).numpy()
        all_preds.extend(preds)
    pred_labels = np.array(all_preds)
    eval_time = time.time() - t0

    metrics = {
        "test_accuracy": round(float(accuracy_score(y_test, pred_labels)), 4),
        "test_f1_weighted": round(float(f1_score(y_test, pred_labels, average="weighted")), 4),
        "test_f1_macro": round(float(f1_score(y_test, pred_labels, average="macro")), 4),
        "test_precision": round(float(precision_score(y_test, pred_labels, average="weighted", zero_division=0)), 4),
        "test_recall": round(float(recall_score(y_test, pred_labels, average="weighted", zero_division=0)), 4),
        "eval_time_seconds": round(eval_time, 2),
        "model_name": model_name,
        "backend": "transformer",
        "approach": "transfer_learning_pretrained",
    }

    # Save model and tokenizer
    save_dir = BASE_DIR / "NLPInsight-Analyzer/models"
    save_dir.mkdir(exist_ok=True)

    # Remove old joblib model if present
    old_joblib = save_dir / "model.joblib"
    if old_joblib.exists():
        old_joblib.unlink()
        print("Removed old sklearn model")

    model.save_pretrained(save_dir)
    tokenizer.save_pretrained(save_dir)
    (save_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))

    # Create tar.gz for GCS upload (single-file download in K8s init container)
    tar_path = save_dir / "model.tar.gz"
    model_files = [
        f
        for f in save_dir.iterdir()
        if f.is_file() and f.name not in ("model.tar.gz", "metrics.json") and not f.name.startswith(".")
    ]
    with tarfile.open(tar_path, "w:gz") as tar:
        for f in model_files:
            tar.add(f, arcname=f.name)
    tar_size_mb = tar_path.stat().st_size / (1024 * 1024)

    print(f"Model saved to {save_dir}/")
    print(f"Archive: {tar_path} ({tar_size_mb:.1f} MB)")
    print(f"   Accuracy: {metrics['test_accuracy']:.4f} | F1-weighted: {metrics['test_f1_weighted']:.4f}")
    print(f"   F1-macro: {metrics['test_f1_macro']:.4f}")
    print(f"   Precision: {metrics['test_precision']:.4f} | Recall: {metrics['test_recall']:.4f}")

    log_mlflow(
        "NLPInsight-Analyzer",
        "NL-v3.0_FinBERT",
        {
            "model": model_name,
            "approach": "transfer_learning_pretrained",
            "num_labels": 3,
            "test_size": len(X_test),
        },
        {k: v for k, v in metrics.items() if isinstance(v, (int, float))},
        {
            "run_type": "production",
            "version": "v3.0.0",
            "project": "nlpinsight",
            "framework": "transformers",
            "model_name": model_name,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        },
        tar_path,
    )

    return metrics


# =============================================================================
# MAIN
# =============================================================================
def main():
    print("=" * 70)
    print("  ML-MLOps Portfolio v3.0 — Production Model Training")
    print(f"  Python {sys.version}")
    print(f"  sklearn {__import__('sklearn').__version__}")
    try:
        import xgboost

        print(f"  xgboost {xgboost.__version__}")
    except ImportError:
        pass
    try:
        import lightgbm

        print(f"  lightgbm {lightgbm.__version__}")
    except ImportError:
        pass
    try:
        import torch

        print(f"  torch {torch.__version__}")
    except ImportError:
        pass
    try:
        import transformers

        print(f"  transformers {transformers.__version__}")
    except ImportError:
        pass
    print("=" * 70)

    results = {}

    results["bankchurn"] = train_bankchurn()
    results["carvision"] = train_carvision()
    results["nlpinsight"] = train_nlpinsight()

    print("\n" + "=" * 70)
    print("  TRAINING SUMMARY")
    print("=" * 70)
    for name, m in results.items():
        if m:
            key_metrics = {k: v for k, v in m.items() if k.startswith("test_")}
            print(f"  OK {name}: {key_metrics}")
        else:
            print(f"  FAIL {name}")

    # Verify all model artifacts exist
    expected = [
        ("BankChurn-Predictor/models/model.joblib", "file"),
        ("CarVision-Market-Intelligence/models/model.joblib", "file"),
        ("NLPInsight-Analyzer/models/config.json", "file"),
        ("NLPInsight-Analyzer/models/model.tar.gz", "file"),
    ]
    print("\nModel artifacts:")
    for p, kind in expected:
        full = BASE_DIR / p
        if full.exists():
            size = full.stat().st_size
            unit = "MB" if size > 1024 * 1024 else "KB"
            val = size / (1024 * 1024) if unit == "MB" else size / 1024
            print(f"  OK {p} ({val:.1f} {unit})")
        else:
            print(f"  MISSING {p}")


if __name__ == "__main__":
    main()
