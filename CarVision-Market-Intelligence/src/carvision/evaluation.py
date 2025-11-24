"""
Model evaluation utilities.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.carvision.data import clean_data, infer_feature_types, load_data, split_data


def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def mape(y_true, y_pred) -> float:
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    # Avoid division by zero
    return float(np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100)


def evaluate_model(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate model performance against baseline and calculate metrics."""
    paths = cfg["paths"]
    tr = cfg["training"]
    prep = cfg["preprocessing"]
    seed = cfg.get("seed", 42)

    # Load and clean
    df = clean_data(load_data(paths["data_path"]))

    # Infer features to ensure consistent splitting/types
    num_cols, cat_cols = infer_feature_types(
        df,
        target=tr["target"],
        numeric_features=prep.get("numeric_features"),
        categorical_features=prep.get("categorical_features"),
        drop_columns=prep.get("drop_columns"),
    )
    feature_cols = num_cols + cat_cols

    # Split
    X_train, X_val, X_test, y_train, y_val, y_test, _ = split_data(
        df,
        target=tr["target"],
        test_size=tr["test_size"],
        val_size=tr["val_size"],
        seed=seed,
        shuffle=tr["shuffle"],
    )

    # Load model
    model = joblib.load(paths["model_path"])
    y_pred = model.predict(X_test)

    metrics = {
        "rmse": rmse(y_test, y_pred),
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "mape": mape(y_test, y_pred),
        "r2": float(r2_score(y_test, y_pred)),
    }

    # Baseline
    dummy = DummyRegressor(strategy=tr.get("baseline", "median").replace("dummy_", ""))
    # Fit on train+val to be fair comparison against model trained on train (and validated on val)
    # Or just train? Usually baseline is fit on training data.
    # The original code fit on pd.concat([X_train, X_val]).
    dummy.fit(pd.concat([X_train, X_val]), pd.concat([y_train, y_val]))
    yb = dummy.predict(X_test)
    baseline_metrics = {
        "rmse": rmse(y_test, yb),
        "mae": float(mean_absolute_error(y_test, yb)),
        "mape": mape(y_test, yb),
        "r2": float(r2_score(y_test, yb)),
    }

    # Artifacts
    artifacts_dir = Path(paths["artifacts_dir"])
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Bootstrap
    bootstrap_results = None
    boot_cfg = cfg.get("evaluation", {}).get("bootstrap", {})
    if boot_cfg.get("enabled", False):
        bootstrap_results = _run_bootstrap(
            y_test,
            y_pred,
            yb,
            n_resamples=int(boot_cfg.get("n_resamples", 200)),
            random_state=int(boot_cfg.get("random_state", seed)),
        )

    # Temporal (Backtesting)
    temporal_results = None
    if "model_year" in df.columns:
        temporal_results = _run_temporal_backtest(
            df,
            model,
            tr["target"],
            feature_cols,
            test_size=cfg.get("evaluation", {}).get("temporal", {}).get("test_size", 0.2),
            artifacts_dir=artifacts_dir,
        )

    # Save results
    with open(paths["metrics_path"], "w") as f:
        json.dump(metrics, f, indent=2)
    with open(paths["baseline_metrics_path"], "w") as f:
        json.dump(baseline_metrics, f, indent=2)
    if bootstrap_results:
        with open(artifacts_dir / "metrics_bootstrap.json", "w") as f:
            json.dump(bootstrap_results, f, indent=2)
    if temporal_results:
        with open(artifacts_dir / "metrics_temporal.json", "w") as f:
            json.dump(temporal_results, f, indent=2)

    return {
        "model": metrics,
        "baseline": baseline_metrics,
        "bootstrap": bootstrap_results,
        "temporal": temporal_results,
    }


def _run_bootstrap(y_true, y_model, y_base, n_resamples: int, random_state: int) -> Dict[str, Any]:
    rng = np.random.default_rng(random_state)
    y_true = np.array(y_true)
    y_model = np.array(y_model)
    y_base = np.array(y_base)

    deltas = []
    n_samples = len(y_true)

    for _ in range(n_resamples):
        idx = rng.choice(n_samples, size=n_samples, replace=True)
        # Calculate metric (RMSE)
        rmse_m = rmse(y_true[idx], y_model[idx])
        rmse_b = rmse(y_true[idx], y_base[idx])
        deltas.append(rmse_m - rmse_b)

    deltas_arr = np.array(deltas)
    ci_low, ci_high = np.percentile(deltas_arr, [2.5, 97.5])

    # P-value: 2 * min(prop > 0, prop < 0)
    # H0: delta = 0.
    p_val = 2 * min(np.mean(deltas_arr > 0), np.mean(deltas_arr < 0))

    return {
        "delta_rmse_mean": float(deltas_arr.mean()),
        "delta_rmse_ci95": [float(ci_low), float(ci_high)],
        "p_value_two_sided": float(p_val),
    }


def _run_temporal_backtest(
    df: pd.DataFrame, model: Any, target: str, feature_cols: List[str], test_size: float, artifacts_dir: Path
) -> Dict[str, Any]:
    df_sorted = df.sort_values("model_year")
    n_test = max(1, int(len(df_sorted) * test_size))
    df_temp = df_sorted.tail(n_test)

    X_temp = df_temp[feature_cols]
    y_temp = df_temp[target]

    # Align columns if needed (add missing as nan)
    # The model pipeline usually handles this if robust, but let's ensure structure
    # Actually, clean_data and infer_feature_types should have aligned us.

    y_pred = model.predict(X_temp)

    metrics = {
        "rmse": rmse(y_temp, y_pred),
        "mae": float(mean_absolute_error(y_temp, y_pred)),
        "mape": mape(y_temp, y_pred),
        "r2": float(r2_score(y_temp, y_pred)),
        "n_samples": len(df_temp),
    }

    # Segment analysis
    rows = []
    for col in ["condition", "type", "model_year"]:
        if col not in df_temp:
            continue
        for val, group in df_temp.groupby(col):
            if len(group) < 30:
                continue

            y_g_pred = model.predict(group[feature_cols])
            rows.append(
                {"segment_col": col, "segment_val": str(val), "n": len(group), "rmse": rmse(group[target], y_g_pred)}
            )

    if rows:
        pd.DataFrame(rows).to_csv(artifacts_dir / "error_by_segment.csv", index=False)

    return metrics
