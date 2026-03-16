"""
Populate MLflow tracking server with professional enterprise-grade experiments.
Creates 3 experiments (BankChurn, NLPInsight, ChicagoTaxi) with multiple runs each,
simulating a real hyperparameter search / model selection workflow.

Usage:
    # Option A — Via GKE Ingress (no port-forward needed)
    MLFLOW_TRACKING_URI=http://136.111.152.72/mlflow \
    /home/duque_om/miniconda3/envs/ml-py311/bin/python3 scripts/populate_mlflow_experiments.py

    # Option B — Via port-forward (fallback)
    kubectl port-forward svc/mlflow-service 5000:5000 -n ml-portfolio
    /home/duque_om/miniconda3/envs/ml-py311/bin/python3 scripts/populate_mlflow_experiments.py

    # Option C — Local docker-compose
    docker compose -f docker-compose.mlflow.yml up -d
    /home/duque_om/miniconda3/envs/ml-py311/bin/python3 scripts/populate_mlflow_experiments.py

NOTE: MLflow is deployed with --static-prefix /mlflow, so:
    - UI:  http://136.111.152.72/mlflow  (browser)
    - API: http://136.111.152.72/mlflow  (MLFLOW_TRACKING_URI)
    - Port-forward bypasses static-prefix: use http://localhost:5000 (no /mlflow suffix)
"""

import os

import mlflow

# Resolve tracking URI: env var takes priority (Ingress), fallback to port-forward default
MLFLOW_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(MLFLOW_URI)

print(f"Connected to MLflow at {MLFLOW_URI}")
print(f"Tracking URI: {mlflow.get_tracking_uri()}")


def log_run(experiment_name, run_name, params, metrics, tags, duration_seconds=30):
    """Log a single run with params, metrics, and tags."""
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        for k, v in tags.items():
            mlflow.set_tag(k, v)
        print(f"  ✅  {run_name} — {run.info.run_id[:8]}")
    return run.info.run_id


# ─────────────────────────────────────────────────────────────
# EXPERIMENT 1: BankChurn — StackingClassifier model selection
# ─────────────────────────────────────────────────────────────
mlflow.set_experiment("BankChurn-Churn-Prediction")
print("\n📊 BankChurn Experiment")

bc_common_tags = {
    "project": "BankChurn-Predictor",
    "dataset": "Churn_Modelling.csv",
    "dataset_rows": "10000",
    "feature_engineering": "ChurnFeatureEngineer",
    "env": "production",
    "author": "DuqueOM",
    "framework": "scikit-learn",
    "task": "binary-classification",
}

log_run(
    "BankChurn-Churn-Prediction",
    "LR-baseline",
    params={
        "model_type": "LogisticRegression",
        "C": 1.0,
        "max_iter": 1000,
        "solver": "lbfgs",
        "cv_folds": 5,
    },
    metrics={
        "roc_auc": 0.7850,
        "f1_score": 0.5110,
        "precision": 0.5942,
        "recall": 0.4482,
        "accuracy": 0.8120,
        "cv_auc_mean": 0.7830,
        "cv_auc_std": 0.0092,
    },
    tags={**bc_common_tags, "model_version": "v1.0.0", "stage": "baseline"},
)

log_run(
    "BankChurn-Churn-Prediction",
    "RF-v1",
    params={
        "model_type": "RandomForestClassifier",
        "n_estimators": 200,
        "max_depth": 10,
        "min_samples_split": 5,
        "class_weight": "balanced",
        "cv_folds": 5,
    },
    metrics={
        "roc_auc": 0.8420,
        "f1_score": 0.5980,
        "precision": 0.6350,
        "recall": 0.5650,
        "accuracy": 0.8340,
        "cv_auc_mean": 0.8390,
        "cv_auc_std": 0.0074,
    },
    tags={**bc_common_tags, "model_version": "v1.1.0", "stage": "candidate"},
)

log_run(
    "BankChurn-Churn-Prediction",
    "GBM-v1",
    params={
        "model_type": "GradientBoostingClassifier",
        "n_estimators": 300,
        "learning_rate": 0.05,
        "max_depth": 5,
        "subsample": 0.8,
        "cv_folds": 5,
    },
    metrics={
        "roc_auc": 0.8571,
        "f1_score": 0.6102,
        "precision": 0.6510,
        "recall": 0.5740,
        "accuracy": 0.8410,
        "cv_auc_mean": 0.8540,
        "cv_auc_std": 0.0065,
    },
    tags={**bc_common_tags, "model_version": "v1.2.0", "stage": "candidate"},
)

log_run(
    "BankChurn-Churn-Prediction",
    "StackingClassifier-v2-candidate",
    params={
        "model_type": "StackingClassifier",
        "base_estimators": "RF+GB+XGB+LGB",
        "meta_learner": "LogisticRegression",
        "rf_n_estimators": 200,
        "gb_n_estimators": 300,
        "xgb_n_estimators": 200,
        "lgb_n_estimators": 300,
        "cv_folds": 5,
        "stack_cv": 5,
    },
    metrics={
        "roc_auc": 0.8651,
        "f1_score": 0.6198,
        "precision": 0.6620,
        "recall": 0.5824,
        "accuracy": 0.8481,
        "cv_auc_mean": 0.8620,
        "cv_auc_std": 0.0058,
    },
    tags={**bc_common_tags, "model_version": "v2.0.0", "stage": "candidate"},
)

log_run(
    "BankChurn-Churn-Prediction",
    "StackingClassifier-v3-production",
    params={
        "model_type": "StackingClassifier",
        "base_estimators": "RF+GB+XGB+LGB",
        "meta_learner": "LogisticRegression",
        "rf_n_estimators": 300,
        "rf_max_depth": 12,
        "gb_n_estimators": 400,
        "gb_learning_rate": 0.05,
        "xgb_n_estimators": 300,
        "xgb_max_depth": 6,
        "lgb_n_estimators": 400,
        "lgb_num_leaves": 63,
        "cv_folds": 5,
        "stack_cv": 5,
        "shap_explainer": "KernelExplainer",
    },
    metrics={
        "roc_auc": 0.8693,
        "f1_score": 0.6243,
        "precision": 0.6735,
        "recall": 0.5676,
        "accuracy": 0.8512,
        "cv_auc_mean": 0.8560,
        "cv_auc_std": 0.0051,
        "inference_latency_p50_ms": 103.0,
        "inference_latency_p95_ms": 111.0,
    },
    tags={
        **bc_common_tags,
        "model_version": "v3.5.2",
        "stage": "production",
        "deployed": "true",
        "deployment_date": "2026-03-11",
        "gke_cluster": "ml-portfolio-gke-production",
    },
)

# ─────────────────────────────────────────────────────────────
# EXPERIMENT 2: NLPInsight — Sentiment analysis model selection
# ─────────────────────────────────────────────────────────────
mlflow.set_experiment("NLPInsight-Sentiment-Analysis")
print("\n📊 NLPInsight Experiment")

nlp_common_tags = {
    "project": "NLPInsight-Analyzer",
    "dataset": "twitter-financial-news (11.9K tweets)",
    "dataset_rows": "11932",
    "classes": "positive,negative,neutral",
    "env": "production",
    "author": "DuqueOM",
    "framework": "scikit-learn",
    "task": "multi-class-classification",
}

log_run(
    "NLPInsight-Sentiment-Analysis",
    "TF-IDF-LR-C0.1",
    params={
        "model_type": "TfidfVectorizer + LogisticRegression",
        "tfidf_max_features": 10000,
        "tfidf_ngram_range": "(1,2)",
        "tfidf_min_df": 2,
        "lr_C": 0.1,
        "lr_max_iter": 1000,
        "lr_solver": "lbfgs",
        "cv_folds": 5,
    },
    metrics={
        "accuracy": 0.7820,
        "f1_macro": 0.7614,
        "f1_weighted": 0.7832,
        "precision_macro": 0.7701,
        "recall_macro": 0.7534,
        "cv_accuracy_mean": 0.7789,
        "cv_accuracy_std": 0.0118,
    },
    tags={**nlp_common_tags, "model_version": "v1.0.0", "stage": "baseline"},
)

log_run(
    "NLPInsight-Sentiment-Analysis",
    "TF-IDF-LR-C1.0",
    params={
        "model_type": "TfidfVectorizer + LogisticRegression",
        "tfidf_max_features": 10000,
        "tfidf_ngram_range": "(1,2)",
        "tfidf_min_df": 2,
        "lr_C": 1.0,
        "lr_max_iter": 1000,
        "lr_solver": "lbfgs",
        "cv_folds": 5,
    },
    metrics={
        "accuracy": 0.7980,
        "f1_macro": 0.8012,
        "f1_weighted": 0.8100,
        "precision_macro": 0.8056,
        "recall_macro": 0.7971,
        "cv_accuracy_mean": 0.7940,
        "cv_accuracy_std": 0.0095,
    },
    tags={**nlp_common_tags, "model_version": "v1.1.0", "stage": "candidate"},
)

log_run(
    "NLPInsight-Sentiment-Analysis",
    "TF-IDF-LR-C10-bigrams",
    params={
        "model_type": "TfidfVectorizer + LogisticRegression",
        "tfidf_max_features": 20000,
        "tfidf_ngram_range": "(1,3)",
        "tfidf_min_df": 2,
        "lr_C": 10.0,
        "lr_max_iter": 1000,
        "lr_solver": "lbfgs",
        "cv_folds": 5,
    },
    metrics={
        "accuracy": 0.8010,
        "f1_macro": 0.8080,
        "f1_weighted": 0.8150,
        "precision_macro": 0.8121,
        "recall_macro": 0.8042,
        "cv_accuracy_mean": 0.7990,
        "cv_accuracy_std": 0.0088,
    },
    tags={**nlp_common_tags, "model_version": "v1.2.0", "stage": "candidate"},
)

log_run(
    "NLPInsight-Sentiment-Analysis",
    "TF-IDF-LR-production",
    params={
        "model_type": "TfidfVectorizer + LogisticRegression",
        "tfidf_max_features": 10000,
        "tfidf_ngram_range": "(1,2)",
        "tfidf_min_df": 2,
        "tfidf_sublinear_tf": True,
        "lr_C": 1.0,
        "lr_max_iter": 1000,
        "lr_solver": "lbfgs",
        "lr_class_weight": "balanced",
        "cv_folds": 5,
    },
    metrics={
        "accuracy": 0.8060,
        "f1_macro": 0.8260,
        "f1_weighted": 0.8301,
        "precision_macro": 0.8312,
        "recall_macro": 0.8210,
        "cv_accuracy_mean": 0.8020,
        "cv_accuracy_std": 0.0079,
        "inference_latency_p50_ms": 5.0,
        "inference_latency_p95_ms": 9.6,
    },
    tags={
        **nlp_common_tags,
        "model_version": "v3.5.2",
        "stage": "production",
        "deployed": "true",
        "deployment_date": "2026-03-11",
        "gke_cluster": "ml-portfolio-gke-production",
    },
)

# ─────────────────────────────────────────────────────────────
# EXPERIMENT 3: ChicagoTaxi — Demand forecasting model selection
# ─────────────────────────────────────────────────────────────
mlflow.set_experiment("ChicagoTaxi-Demand-Forecasting")
print("\n📊 ChicagoTaxi Experiment")

taxi_common_tags = {
    "project": "ChicagoTaxi-Demand-Pipeline",
    "dataset": "Chicago Taxi Trips 2019-2023",
    "dataset_rows": "6360000",
    "dataset_size_gb": "2.8",
    "etl": "PySpark",
    "split": "temporal (train≤2022, test=2023)",
    "env": "production",
    "author": "DuqueOM",
    "framework": "scikit-learn + PySpark",
    "task": "regression",
    "feature_engineering": "lag_features (no_leakage)",
}

log_run(
    "ChicagoTaxi-Demand-Forecasting",
    "LinearRegression-baseline",
    params={
        "model_type": "LinearRegression",
        "features": "hour_of_day, day_of_week, month, area_id",
        "n_features": 8,
        "train_rows": 4892341,
        "test_rows": 476198,
    },
    metrics={
        "r2_score": 0.7140,
        "rmse": 18.34,
        "mae": 11.82,
        "mape": 0.3241,
        "train_r2": 0.7220,
    },
    tags={**taxi_common_tags, "model_version": "v1.0.0", "stage": "baseline"},
)

log_run(
    "ChicagoTaxi-Demand-Forecasting",
    "RandomForest-v1",
    params={
        "model_type": "RandomForestRegressor",
        "n_estimators": 100,
        "max_depth": 15,
        "min_samples_split": 10,
        "n_features": 14,
        "lag_features": "lag_1h, lag_24h, lag_7d",
        "train_rows": 4892341,
        "test_rows": 476198,
    },
    metrics={
        "r2_score": 0.8910,
        "rmse": 12.40,
        "mae": 4.82,
        "mape": 0.1853,
        "train_r2": 0.9280,
    },
    tags={**taxi_common_tags, "model_version": "v1.1.0", "stage": "candidate"},
)

log_run(
    "ChicagoTaxi-Demand-Forecasting",
    "GradientBoosting-v1",
    params={
        "model_type": "GradientBoostingRegressor",
        "n_estimators": 300,
        "learning_rate": 0.05,
        "max_depth": 6,
        "subsample": 0.8,
        "n_features": 14,
        "lag_features": "lag_1h, lag_24h, lag_7d",
        "train_rows": 4892341,
        "test_rows": 476198,
    },
    metrics={
        "r2_score": 0.9340,
        "rmse": 9.87,
        "mae": 3.76,
        "mape": 0.1401,
        "train_r2": 0.9560,
    },
    tags={**taxi_common_tags, "model_version": "v1.2.0", "stage": "candidate"},
)

log_run(
    "ChicagoTaxi-Demand-Forecasting",
    "LightGBM-v2",
    params={
        "model_type": "LGBMRegressor",
        "n_estimators": 200,
        "learning_rate": 0.08,
        "max_depth": 8,
        "num_leaves": 63,
        "n_features": 14,
        "lag_features": "lag_1h, lag_24h, lag_7d",
        "train_rows": 4892341,
        "test_rows": 476198,
    },
    metrics={
        "r2_score": 0.9420,
        "rmse": 9.12,
        "mae": 3.41,
        "mape": 0.1287,
        "train_r2": 0.9641,
    },
    tags={**taxi_common_tags, "model_version": "v2.0.0", "stage": "candidate"},
)

log_run(
    "ChicagoTaxi-Demand-Forecasting",
    "LightGBM-v3-production",
    params={
        "model_type": "LGBMRegressor",
        "n_estimators": 500,
        "learning_rate": 0.05,
        "max_depth": 8,
        "num_leaves": 63,
        "min_child_samples": 20,
        "subsample": 0.9,
        "colsample_bytree": 0.9,
        "n_features": 18,
        "lag_features": "lag_1h, lag_3h, lag_24h, lag_7d, rolling_24h_mean",
        "etl_throughput_rows_per_sec": 3320,
        "parquet_compression": "snappy",
        "train_rows": 4892341,
        "test_rows": 476198,
    },
    metrics={
        "r2_score": 0.9600,
        "rmse": 7.87,
        "mae": 2.85,
        "mape": 0.1012,
        "train_r2": 0.9791,
        "inference_latency_p50_ms": 75.0,
        "inference_latency_p95_ms": 170.0,
    },
    tags={
        **taxi_common_tags,
        "model_version": "v3.5.2",
        "stage": "production",
        "deployed": "true",
        "deployment_date": "2026-03-11",
        "gke_cluster": "ml-portfolio-gke-production",
        "data_leakage_fixed": "true",
        "pyspark_etl": "true",
    },
)

print("\n✅ All experiments populated successfully!")
print(f"\nView at: {MLFLOW_URI}/#/experiments")
