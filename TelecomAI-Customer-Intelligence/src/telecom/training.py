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


def ensure_dirs(paths) -> None:
    """Create necessary directories from PathsConfig."""
    Path(paths.artifacts_dir).mkdir(parents=True, exist_ok=True)
    if paths.model_export_path:
        Path(paths.model_export_path).parent.mkdir(parents=True, exist_ok=True)


def build_model(model_cfg, seed: int) -> Any:
    """Build a sklearn classifier from ModelConfig or dict.

    Parameters
    ----------
    model_cfg : ModelConfig or dict
        Model configuration (Pydantic model or dict for backward compatibility)
    seed : int
        Random seed

    Returns
    -------
    classifier
        Sklearn classifier instance
    """
    # Support both Pydantic ModelConfig and dict for backward compatibility
    if isinstance(model_cfg, dict):
        name = model_cfg.get("name", "logreg").lower()
        params: Dict[str, Any] = model_cfg.get("params", {})
    else:
        # Pydantic ModelConfig
        name = model_cfg.name.lower()
        params = model_cfg.params

    # Ensure seed is passed if supported
    if name == "logreg" or name == "logistic_regression":
        return LogisticRegression(**params, random_state=seed)
    if name == "random_forest":
        return RandomForestClassifier(**params, random_state=seed)
    if name == "gradient_boosting":
        return GradientBoostingClassifier(**params, random_state=seed)

    raise ValueError(f"Unsupported model: {name}")


def train_model(cfg: Any) -> Dict[str, float]:
    logger.info("Starting training...")
    ensure_dirs(cfg.paths)

    df = load_dataset(cfg.paths.data_csv)
    X, y = get_features_target(df, cfg.features, cfg.target)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=float(cfg.split.test_size),
        stratify=y if cfg.split.stratify else None,
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

    # Save artifacts with compression
    # Saving the FULL pipeline is preferred over saving parts separately for serving
    model_path = Path(cfg.paths.model_path)
    joblib.dump(pipeline, model_path, compress=3)
    size_mb = model_path.stat().st_size / (1024 * 1024)
    logger.info(f"Pipeline saved to {model_path} ({size_mb:.2f} MB)")

    # Also save parts if specifically requested by legacy code (e.g. evaluate.py might expect them separate)
    # Actually, better to update evaluate.py to use the pipeline.

    return {"accuracy": score, "model_path": cfg.paths.model_path}
