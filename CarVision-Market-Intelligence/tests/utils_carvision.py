from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import yaml


def _create_synthetic_dataset(destination: Path, *, include_condition: bool = True, n_rows: int = 240) -> Path:
    rng = np.random.default_rng(42)
    data = {
        "price": rng.integers(5000, 40000, size=n_rows),
        "model_year": rng.choice([2014, 2015, 2016, 2017], size=n_rows),
        "odometer": rng.integers(5000, 150000, size=n_rows),
        "fuel": rng.choice(["gas", "diesel"], size=n_rows),
        "model": rng.choice(["ford focus", "honda civic", "audi a4"], size=n_rows),
        "type": rng.choice(["sedan", "SUV"], size=n_rows),
        "cylinders": rng.choice(["4 cylinders", "6 cylinders"], size=n_rows),
        "transmission": rng.choice(["automatic", "manual"], size=n_rows),
        "drive": rng.choice(["fwd", "4wd"], size=n_rows),
        "size": rng.choice(["compact", "full-size"], size=n_rows),
        "paint_color": rng.choice(["black", "white", "silver"], size=n_rows),
    }
    if include_condition:
        data["condition"] = rng.choice(["excellent", "good", "fair"], size=n_rows)
    df = pd.DataFrame(data)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destination, index=False)
    return destination


def build_test_config(
    tmp_path: Path,
    *,
    include_condition: bool = True,
    bootstrap_enabled: bool = True,
    temporal_size: float = 1.0,
) -> Tuple[dict, Path]:
    project_root = Path(__file__).resolve().parents[1]
    cfg_path = project_root / "configs" / "config.yaml"
    cfg = yaml.safe_load(cfg_path.read_text())

    data_csv = tmp_path / "synthetic_dataset.csv"
    _create_synthetic_dataset(
        data_csv,
        include_condition=include_condition,
        n_rows=max(60, int(temporal_size * 240)),
    )

    artifacts_dir = tmp_path / "artifacts"
    cfg_paths = cfg.get("paths", {})
    cfg["paths"] = {
        **cfg_paths,
        "data_path": str(data_csv),
        "artifacts_dir": str(artifacts_dir),
        "model_path": str(artifacts_dir / "model.joblib"),
        "metrics_path": str(artifacts_dir / "metrics.json"),
        "baseline_metrics_path": str(artifacts_dir / "baseline.json"),
        "split_indices_path": str(artifacts_dir / "split_indices.json"),
        "model_export_path": str(artifacts_dir / "model_export.pkl"),
    }

    rf_params = cfg["training"].get("random_forest_params", {}).copy()
    rf_params.update({"n_estimators": 20, "max_depth": 5, "n_jobs": 1})
    cfg["training"]["random_forest_params"] = rf_params
    cfg["seed"] = 7

    eval_cfg = cfg.setdefault("evaluation", {})
    bootstrap_cfg = eval_cfg.setdefault("bootstrap", {})
    bootstrap_cfg["enabled"] = bootstrap_enabled
    bootstrap_cfg.setdefault("n_resamples", 50)
    bootstrap_cfg.setdefault("random_state", 42)

    temporal_cfg = eval_cfg.setdefault("temporal", {})
    temporal_cfg["test_size"] = temporal_size

    return cfg, data_csv
