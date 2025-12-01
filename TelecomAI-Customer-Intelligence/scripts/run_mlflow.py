"""TelecomAI MLflow logging script.

This script registers experiment runs to MLflow, logging:
- Training parameters from config
- Model metrics (accuracy, precision, recall, F1, ROC-AUC)
- Business metrics (estimated revenue impact)
- Artifacts (metrics.json, config, plots) - best effort

Usage:
    export MLFLOW_TRACKING_URI=http://localhost:5000
    python scripts/run_mlflow.py

Environment variables:
    MLFLOW_TRACKING_URI: MLflow server URI (default: file:./mlruns)
    MLFLOW_EXPERIMENT: Experiment name (default: TelecomAI)
    TC_ARPU_USD: Average Revenue Per User for business metrics (default: 65)
    TC_RETENTION_RATE: Estimated retention rate for detected churners (default: 0.25)
"""

from __future__ import annotations

import json
import os
from pathlib import Path

try:
    import mlflow  # type: ignore
except ImportError:  # pragma: no cover
    mlflow = None  # type: ignore


def load_metrics(metrics_path: Path) -> dict[str, float]:
    """Load metrics from JSON file."""
    if not metrics_path.exists():
        return {}
    try:
        return json.loads(metrics_path.read_text())
    except Exception:
        return {}


def compute_business_metrics(metrics: dict[str, float]) -> dict[str, float]:
    """Compute business impact metrics from model performance.

    Assumes a telecom churn scenario where:
    - ARPU (Average Revenue Per User) represents monthly value
    - Retention campaigns can save a fraction of detected churners
    - False negatives represent lost revenue opportunities
    """
    recall = metrics.get("recall", 0.0)
    precision = metrics.get("precision", 0.0)

    # Configurable business parameters
    arpu = float(os.getenv("TC_ARPU_USD", "65"))  # Monthly ARPU
    retention_rate = float(os.getenv("TC_RETENTION_RATE", "0.25"))

    # Hypothetical customer base for demo (1000 customers, 26% churn rate from Telco dataset)
    total_customers = 1000
    churn_rate = 0.26
    churners = int(total_customers * churn_rate)

    # Business impact calculations
    detected_churners = int(churners * recall)
    saved_customers = int(detected_churners * retention_rate)
    saved_revenue_monthly = saved_customers * arpu
    saved_revenue_annual = saved_revenue_monthly * 12

    # False positive cost (unnecessary retention offers)
    if precision > 0:
        false_positives = int(detected_churners * (1 - precision) / precision)
    else:
        false_positives = 0
    retention_offer_cost = 20  # Cost per retention offer
    wasted_cost = false_positives * retention_offer_cost

    return {
        "biz_detected_churners": float(detected_churners),
        "biz_saved_customers": float(saved_customers),
        "biz_saved_revenue_monthly_usd": saved_revenue_monthly,
        "biz_saved_revenue_annual_usd": saved_revenue_annual,
        "biz_false_positives": float(false_positives),
        "biz_wasted_retention_cost_usd": float(wasted_cost),
        "biz_net_benefit_annual_usd": saved_revenue_annual - (wasted_cost * 12),
    }


def main() -> None:
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
    experiment = os.getenv("MLFLOW_EXPERIMENT", "TelecomAI")

    # Load metrics
    metrics_path = Path("artifacts/metrics.json")
    metrics = load_metrics(metrics_path)

    # Compute business metrics
    business_metrics = compute_business_metrics(metrics) if metrics else {}

    if mlflow is None:
        print("MLflow not installed; skipping logging.")
        print("Metrics:", metrics)
        print("Business metrics:", business_metrics)
        return

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment)

    with mlflow.start_run(run_name="demo-logging"):
        # Log parameters
        mlflow.log_params(
            {
                "run_type": "demo",
                "project": "TelecomAI-Customer-Intelligence",
                "model": "gradient_boosting",
                "note": "TelecomAI MLflow demo logging",
            }
        )

        # Log model metrics
        if metrics:
            mlflow.log_metrics(metrics)

        # Log business metrics
        if business_metrics:
            mlflow.log_metrics(business_metrics)

        # Log artifacts (best-effort: remote artifact stores may not be writable)
        artifacts_to_log = [
            Path("artifacts/metrics.json"),
            Path("configs/config.yaml"),
            Path("artifacts/confusion_matrix.png"),
            Path("artifacts/roc_curve.png"),
        ]

        for artifact_path in artifacts_to_log:
            if artifact_path.exists():
                try:
                    mlflow.log_artifact(str(artifact_path))
                except PermissionError:
                    print(f"Skipping artifact {artifact_path}: permission denied while logging to MLflow.")
                except Exception as exc:  # pragma: no cover
                    print(f"Skipping artifact {artifact_path} due to: {exc}")

        print(f"Logged TelecomAI run to {tracking_uri} in experiment '{experiment}'")
        print(f"🏃 View run at: {tracking_uri}/#/experiments")


if __name__ == "__main__":
    main()
