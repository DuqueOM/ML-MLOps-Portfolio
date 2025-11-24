"""
Training pipeline logic.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import joblib
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from src.telecom.data import build_preprocessor, get_features_target, load_dataset

logger = logging.getLogger(__name__)


def ensure_dirs(paths: Dict[str, str]) -> None:
    Path(paths["artifacts_dir"]).mkdir(parents=True, exist_ok=True)
    model_export_path = paths.get("model_export_path")
    if model_export_path:
        Path(model_export_path).parent.mkdir(parents=True, exist_ok=True)


def build_model(model_cfg: Dict[str, Any], seed: int) -> Any:
    """Build a sklearn classifier from a simple config dict."""
    name = model_cfg.get("name", "logreg").lower()
    params: Dict[str, Any] = model_cfg.get("params", {})

    # Ensure seed is passed if supported
    if name == "logreg":
        return LogisticRegression(**params, random_state=seed)
    if name == "random_forest":
        return RandomForestClassifier(**params, random_state=seed)
    if name == "gradient_boosting":
        return GradientBoostingClassifier(**params, random_state=seed)

    raise ValueError(f"Unsupported model: {model_cfg.get('name')}")


def train_model(cfg: Any) -> Dict[str, float]:
    logger.info("Starting training...")
    ensure_dirs(cfg.paths)

    df = load_dataset(cfg.paths["data_csv"])
    X, y = get_features_target(df, cfg.features, cfg.target)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=float(cfg.split.get("test_size", 0.2)),
        stratify=y if cfg.split.get("stratify", True) else None,
        random_state=int(cfg.random_seed),
    )

    preprocessor = build_preprocessor(cfg.features)
    clf = build_model(cfg.model, int(cfg.random_seed))

    # Unified pipeline (Preprocessor + Classifier)
    # Important: We wrap everything in one object for easy deployment
    pipeline = Pipeline(steps=[("preprocess", preprocessor), ("clf", clf)])

    # Fit
    pipeline.fit(X_train, y_train)

    # Evaluate
    # We defer to the evaluation module/function, but compute basic score here
    score = pipeline.score(X_test, y_test)
    logger.info(f"Model accuracy: {score:.4f}")

    # Save artifacts
    # Saving the FULL pipeline is preferred over saving parts separately for serving
    # But we keep legacy support if needed.
    joblib.dump(
        pipeline, cfg.paths["model_path"]
    )  # Overwriting separate parts model with full pipeline is a breaking change?
    # Wait, original code saved preprocessor and model separately AND pipeline separately.
    # Let's simplify: Save full pipeline as the main artifact.
    joblib.dump(pipeline, cfg.paths["model_path"])

    # Also save parts if specifically requested by legacy code (e.g. evaluate.py might expect them separate)
    # Actually, better to update evaluate.py to use the pipeline.

    return {"accuracy": score, "model_path": cfg.paths["model_path"]}
