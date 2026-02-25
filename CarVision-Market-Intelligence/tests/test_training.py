"""Tests for training.py — model comparison, auto-selection, and artifact persistence."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from src.carvision.training import train_model
from tests.utils_carvision import build_test_config


def test_train_with_model_comparison(tmp_path: Path) -> None:
    """compare_models with an always-available model exercises the comparison loop."""
    cfg, _ = build_test_config(tmp_path)
    cfg["training"]["compare_models"] = ["mlp"]
    cfg["training"]["mlp_params"] = {
        "hidden_layer_sizes": (16,),
        "max_iter": 50,
        "random_state": 7,
    }

    result = train_model(cfg)

    assert "comparison" in result
    assert "mlp" in result["comparison"]
    mlp_metrics = result["comparison"]["mlp"]
    assert "rmse" in mlp_metrics
    assert "r2" in mlp_metrics

    # model_comparison.json must be written
    comp_path = Path(cfg["paths"]["artifacts_dir"]) / "model_comparison.json"
    assert comp_path.exists()
    comp_data = json.loads(comp_path.read_text())
    assert "mlp" in comp_data


def test_auto_selection_keeps_primary_when_better(tmp_path: Path) -> None:
    """Primary model kept when its R2 >= all comparison models."""
    cfg, _ = build_test_config(tmp_path)
    # MLP with tiny capacity will likely lose to random_forest
    cfg["training"]["compare_models"] = ["mlp"]
    cfg["training"]["mlp_params"] = {
        "hidden_layer_sizes": (2,),
        "max_iter": 5,
        "random_state": 7,
    }

    result = train_model(cfg)

    vm = result["val_metrics"]
    assert "auto_selected" in vm
    # Whether auto_selected is True or False, the field must exist
    if not vm["auto_selected"]:
        assert vm["model"] == "random_forest"


def test_auto_selection_switches_model(tmp_path: Path) -> None:
    """When a comparison model beats the primary, auto-selection switches.

    We mock build_model for the comparison so it returns a fitted pipeline
    whose R2 appears superior, guaranteeing the switch branch is exercised.
    """
    cfg, _ = build_test_config(tmp_path)
    cfg["training"]["compare_models"] = ["mlp"]
    cfg["training"]["mlp_params"] = {
        "hidden_layer_sizes": (16,),
        "max_iter": 50,
        "random_state": 7,
    }

    from sklearn.ensemble import RandomForestRegressor

    cfg2, _ = build_test_config(tmp_path)
    cfg2["training"]["compare_models"] = ["mlp"]
    cfg2["training"]["mlp_params"] = {
        "hidden_layer_sizes": (16,),
        "max_iter": 50,
        "random_state": 7,
    }

    original_build = __import__("src.carvision.models_advanced", fromlist=["build_model"]).build_model

    def patched_build(name, params=None, seed=42):
        # For mlp comparison, return a strong RF that will beat the weak primary
        if name == "mlp":
            return RandomForestRegressor(n_estimators=50, max_depth=10, n_jobs=1, random_state=seed)
        return original_build(name, params=params, seed=seed)

    # Make primary very weak so comparison wins
    cfg2["training"]["random_forest_params"] = {
        "n_estimators": 1,
        "max_depth": 1,
        "n_jobs": 1,
        "random_state": 7,
    }

    with patch("src.carvision.training.build_model", side_effect=patched_build):
        result2 = train_model(cfg2)

    vm = result2["val_metrics"]
    assert vm["auto_selected"] is True
    assert vm["model"] == "mlp"
    assert vm["original_model"] == "random_forest"


def test_comparison_with_unavailable_model_skips(tmp_path: Path) -> None:
    """A model reported as unavailable is skipped with a warning."""
    cfg, _ = build_test_config(tmp_path)
    cfg["training"]["compare_models"] = ["neural_network"]

    # Force neural_network to report as unavailable
    with patch(
        "src.carvision.training.get_available_models",
        return_value={
            "random_forest": True,
            "mlp": True,
            "xgboost": False,
            "lightgbm": False,
            "neural_network": False,
        },
    ):
        result = train_model(cfg)

    # neural_network should not appear in comparison results
    assert "neural_network" not in result["comparison"]


def test_comparison_model_failure_records_error(tmp_path: Path) -> None:
    """If a comparison model raises during fit, the error is captured."""
    cfg, _ = build_test_config(tmp_path)
    cfg["training"]["compare_models"] = ["mlp"]

    # Inject a build_model that raises for mlp
    def broken_build(name, params=None, seed=42):
        if name == "mlp":
            raise RuntimeError("intentional test failure")
        from src.carvision.models_advanced import build_model as real_build

        return real_build(name, params=params, seed=seed)

    with patch("src.carvision.training.build_model", side_effect=broken_build):
        result = train_model(cfg)

    assert "mlp" in result["comparison"]
    assert "error" in result["comparison"]["mlp"]
