#!/usr/bin/env python3
"""
Model Promotion Script for MLflow Model Registry.

This script:
1. Reads training metrics from artifacts/metrics.json
2. Validates metrics against thresholds
3. Registers model to MLflow Model Registry
4. Optionally promotes to Production stage

Usage:
    python scripts/promote_model.py --project bankchurn --min-f1 0.60 --min-auc 0.80
    python scripts/promote_model.py --project bankchurn --promote

Environment:
    MLFLOW_TRACKING_URI: MLflow server URI (default: file:./mlruns)
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Project configurations
PROJECT_CONFIGS = {
    "bankchurn": {
        "dir": "BankChurn-Predictor",
        "model_name": "BankChurn-Classifier",
        "model_path": "models/best_model.pkl",
        "metrics_path": "artifacts/metrics.json",
        "default_thresholds": {"f1": 0.50, "auc": 0.75},
    },
    "carvision": {
        "dir": "CarVision-Market-Intelligence",
        "model_name": "CarVision-Regressor",
        "model_path": "artifacts/model.joblib",
        "metrics_path": "artifacts/metrics.json",
        "default_thresholds": {"r2": 0.70, "rmse": 6000},
    },
    "telecom": {
        "dir": "TelecomAI-Customer-Intelligence",
        "model_name": "TelecomAI-Classifier",
        "model_path": "artifacts/model.joblib",
        "metrics_path": "artifacts/metrics.json",
        "default_thresholds": {"accuracy": 0.75, "f1": 0.50},
    },
}


def load_metrics(metrics_path: Path) -> dict:
    """Load metrics from JSON file."""
    if not metrics_path.exists():
        logger.warning(f"Metrics file not found: {metrics_path}")
        return {}

    with open(metrics_path) as f:
        return json.load(f)


def validate_metrics(metrics: dict, thresholds: dict) -> tuple[bool, list[str]]:
    """
    Validate metrics against thresholds.

    Returns:
        Tuple of (passed, list of failure messages)
    """
    failures = []

    # Map common metric names
    metric_mapping = {
        "f1": ["test_f1", "f1_score", "f1"],
        "auc": ["test_auc", "test_roc_auc", "auc_roc", "auc"],
        "accuracy": ["test_accuracy", "accuracy"],
        "r2": ["test_r2", "r2_score", "r2"],
        "rmse": ["test_rmse", "rmse"],
    }

    for threshold_name, threshold_value in thresholds.items():
        metric_found = False
        for possible_name in metric_mapping.get(threshold_name, [threshold_name]):
            if possible_name in metrics:
                actual_value = metrics[possible_name]
                metric_found = True

                # For RMSE, lower is better
                if threshold_name == "rmse":
                    if actual_value > threshold_value:
                        failures.append(f"{threshold_name}: {actual_value:.4f} > {threshold_value} (threshold)")
                else:
                    if actual_value < threshold_value:
                        failures.append(f"{threshold_name}: {actual_value:.4f} < {threshold_value} (threshold)")
                break

        if not metric_found:
            logger.warning(f"Metric '{threshold_name}' not found in metrics")

    return len(failures) == 0, failures


def register_model(project_config: dict, metrics: dict, promote: bool = False) -> bool:
    """Register model to MLflow Model Registry."""
    try:
        import mlflow
        from mlflow.tracking import MlflowClient
    except ImportError:
        logger.error("MLflow not installed. Run: pip install mlflow")
        return False

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
    mlflow.set_tracking_uri(tracking_uri)

    model_name = project_config["model_name"]
    model_path = Path(project_config["dir"]) / project_config["model_path"]

    if not model_path.exists():
        logger.error(f"Model file not found: {model_path}")
        return False

    logger.info(f"Registering model to MLflow: {model_name}")
    logger.info(f"Tracking URI: {tracking_uri}")

    try:
        # Start a run to log the model
        with mlflow.start_run(run_name=f"register_{model_name}") as run:
            # Log metrics
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    mlflow.log_metric(key, value)

            # Log model
            mlflow.sklearn.log_model(
                sk_model=None,  # We'll use log_artifact instead
                artifact_path="model",
                registered_model_name=model_name,
            )

            # Log the actual model file
            mlflow.log_artifact(str(model_path))

            logger.info(f"Model registered: {model_name}")
            logger.info(f"Run ID: {run.info.run_id}")

        if promote:
            # Get the latest version and promote to Production
            client = MlflowClient()
            versions = client.search_model_versions(f"name='{model_name}'")

            if versions:
                latest_version = max(versions, key=lambda v: int(v.version))
                client.transition_model_version_stage(
                    name=model_name,
                    version=latest_version.version,
                    stage="Production",
                    archive_existing_versions=True,
                )
                logger.info(f"Model {model_name} v{latest_version.version} promoted to Production")

        return True

    except Exception as e:
        logger.error(f"Failed to register model: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Register and promote models to MLflow Model Registry")
    parser.add_argument(
        "--project",
        required=True,
        choices=list(PROJECT_CONFIGS.keys()),
        help="Project to process",
    )
    parser.add_argument(
        "--min-f1",
        type=float,
        default=None,
        help="Minimum F1 score threshold",
    )
    parser.add_argument(
        "--min-auc",
        type=float,
        default=None,
        help="Minimum AUC-ROC threshold",
    )
    parser.add_argument(
        "--min-r2",
        type=float,
        default=None,
        help="Minimum R² threshold (for regression)",
    )
    parser.add_argument(
        "--promote",
        action="store_true",
        help="Promote to Production if metrics pass",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only validate metrics, don't register",
    )

    args = parser.parse_args()

    config = PROJECT_CONFIGS[args.project]
    project_dir = Path(config["dir"])
    metrics_path = project_dir / config["metrics_path"]

    # Load metrics
    logger.info(f"Loading metrics from: {metrics_path}")
    metrics = load_metrics(metrics_path)

    if not metrics:
        logger.error("No metrics found. Train the model first.")
        sys.exit(1)

    logger.info(f"Metrics loaded: {json.dumps(metrics, indent=2)}")

    # Build thresholds from args or defaults
    thresholds = config["default_thresholds"].copy()
    if args.min_f1 is not None:
        thresholds["f1"] = args.min_f1
    if args.min_auc is not None:
        thresholds["auc"] = args.min_auc
    if args.min_r2 is not None:
        thresholds["r2"] = args.min_r2

    # Validate metrics
    logger.info(f"Validating against thresholds: {thresholds}")
    passed, failures = validate_metrics(metrics, thresholds)

    if not passed:
        logger.warning("Metrics validation failed:")
        for failure in failures:
            logger.warning(f"  - {failure}")
        if not args.dry_run:
            logger.info("Model will be registered but NOT promoted to Production")
    else:
        logger.info("✅ All metrics passed validation!")

    if args.dry_run:
        logger.info("Dry run complete. No changes made.")
        sys.exit(0 if passed else 1)

    # Register model
    success = register_model(
        config,
        metrics,
        promote=args.promote and passed,
    )

    if success:
        logger.info("✅ Model registration complete!")
        if args.promote and passed:
            logger.info("✅ Model promoted to Production!")
    else:
        logger.error("❌ Model registration failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
