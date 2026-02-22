"""
Training pipeline logic.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

import joblib
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from src.telecom.data import build_preprocessor, get_features_target, load_dataset
from src.telecom.models_advanced import build_model as build_advanced_model
from src.telecom.models_advanced import get_available_models

logger = logging.getLogger(__name__)


def ensure_dirs(paths) -> None:
    """Create necessary directories from PathsConfig."""
    Path(paths.artifacts_dir).mkdir(parents=True, exist_ok=True)
    if paths.model_export_path:
        Path(paths.model_export_path).parent.mkdir(parents=True, exist_ok=True)


def build_model(model_cfg, seed: int) -> Any:
    """Build a sklearn-compatible classifier from ModelConfig or dict.

    Uses the advanced model factory which supports gradient_boosting,
    random_forest, logistic_regression, xgboost, lightgbm, and neural_network.

    Parameters
    ----------
    model_cfg : ModelConfig or dict
        Model configuration (Pydantic model or dict for backward compatibility)
    seed : int
        Random seed

    Returns
    -------
    classifier
        Sklearn-compatible classifier instance
    """
    if isinstance(model_cfg, dict):
        name = model_cfg.get("name", "gradient_boosting").lower()
        params: Dict[str, Any] = model_cfg.get("params", {})
    else:
        name = model_cfg.name.lower()
        params = dict(model_cfg.params)

    # Normalize legacy name
    if name == "logreg":
        name = "logistic_regression"

    return build_advanced_model(name, params=params, seed=seed)


def train_model(cfg: Any) -> Dict[str, float]:
    logger.info("Starting training...")
    ensure_dirs(cfg.paths)
    seed = int(cfg.random_seed)

    df = load_dataset(cfg.paths.data_csv)
    X, y = get_features_target(df, cfg.features, cfg.target)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=float(cfg.split.test_size),
        stratify=y if cfg.split.stratify else None,
        random_state=seed,
    )

    preprocessor = build_preprocessor(cfg.features)
    clf = build_model(cfg.model, seed)

    pipeline = Pipeline(steps=[("preprocess", preprocessor), ("clf", clf)])

    model_name = cfg.model.name if hasattr(cfg.model, "name") else cfg.model.get("name", "unknown")
    logger.info(f"Training model: {model_name}")
    pipeline.fit(X_train, y_train)

    # Evaluate primary model
    y_pred = pipeline.predict(X_test)
    acc = float(accuracy_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred, average="weighted"))
    try:
        y_proba = pipeline.predict_proba(X_test)[:, 1]
        auc = float(roc_auc_score(y_test, y_proba))
    except Exception:
        auc = None

    metrics = {"model": model_name, "accuracy": acc, "f1": f1}
    if auc is not None:
        metrics["roc_auc"] = auc
    logger.info(f"Primary model metrics: {metrics}")

    # Model comparison if configured
    compare_list = getattr(cfg.model, "compare_models", []) or []
    comparison_results: Dict[str, Any] = {}
    fitted_pipelines: Dict[str, Pipeline] = {}
    if compare_list:
        available = get_available_models()
        for cmp_name in compare_list:
            if not available.get(cmp_name, False):
                logger.warning(f"Model '{cmp_name}' not available, skipping")
                continue
            try:
                cmp_clf = build_advanced_model(cmp_name, seed=seed)
                cmp_pipe = Pipeline(steps=[("preprocess", build_preprocessor(cfg.features)), ("clf", cmp_clf)])
                cmp_pipe.fit(X_train, y_train)
                cmp_pred = cmp_pipe.predict(X_test)
                cmp_acc = float(accuracy_score(y_test, cmp_pred))
                cmp_f1 = float(f1_score(y_test, cmp_pred, average="weighted"))
                cmp_metrics: Dict[str, Any] = {"accuracy": cmp_acc, "f1": cmp_f1}
                try:
                    cmp_proba = cmp_pipe.predict_proba(X_test)[:, 1]
                    cmp_metrics["roc_auc"] = float(roc_auc_score(y_test, cmp_proba))
                except Exception:
                    pass
                comparison_results[cmp_name] = cmp_metrics
                fitted_pipelines[cmp_name] = cmp_pipe
                logger.info(f"  {cmp_name}: acc={cmp_acc:.4f}, f1={cmp_f1:.4f}")
            except Exception as e:
                logger.error(f"  {cmp_name} failed: {e}")
                comparison_results[cmp_name] = {"error": str(e)}

    if comparison_results:
        metrics["model_comparison"] = comparison_results

    # Auto-select best model based on F1 score
    if comparison_results:
        primary_f1 = f1
        best_name = model_name
        best_f1 = primary_f1
        for cmp_name, cmp_m in comparison_results.items():
            if "error" not in cmp_m and cmp_m.get("f1", 0) > best_f1:
                best_f1 = cmp_m["f1"]
                best_name = cmp_name

        if best_name != model_name and best_name in fitted_pipelines:
            logger.info(
                f"Auto-selection: {best_name} (F1={best_f1:.4f}) beats "
                f"{model_name} (F1={primary_f1:.4f}). Switching model."
            )
            pipeline = fitted_pipelines[best_name]
            metrics["model"] = best_name
            metrics["f1"] = best_f1
            metrics["accuracy"] = comparison_results[best_name]["accuracy"]
            if "roc_auc" in comparison_results[best_name]:
                metrics["roc_auc"] = comparison_results[best_name]["roc_auc"]
            metrics["auto_selected"] = True
            metrics["original_model"] = model_name
        else:
            logger.info(f"Auto-selection: keeping {model_name} (F1={primary_f1:.4f}) as best model.")
            metrics["auto_selected"] = False

    # Save pipeline
    model_path = Path(cfg.paths.model_path)
    joblib.dump(pipeline, model_path, compress=3)
    size_mb = model_path.stat().st_size / (1024 * 1024)
    logger.info(f"Pipeline saved to {model_path} ({size_mb:.2f} MB)")

    # Save metrics
    metrics_path = Path(cfg.paths.metrics_path)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {k: v for k, v in metrics.items() if not isinstance(v, dict)}
    with open(metrics_path, "w") as f:
        json.dump(serializable, f, indent=2)

    if comparison_results:
        comp_path = metrics_path.parent / "model_comparison.json"
        with open(comp_path, "w") as f:
            json.dump(comparison_results, f, indent=2)

    return metrics
