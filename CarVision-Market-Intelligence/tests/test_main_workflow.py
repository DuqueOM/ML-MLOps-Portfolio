from __future__ import annotations

import json
from pathlib import Path

import pytest
from main import main as carvision_main
from main import train_model
from tests.utils_carvision import build_test_config


def test_train_and_evaluate_pipeline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg, _ = build_test_config(tmp_path)

    result = train_model(cfg)
    assert "val_metrics" in result

    metrics_path = Path(cfg["paths"]["metrics_path"])
    metrics_path.write_text(json.dumps({"rmse": 1.23}))

    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(json.dumps(cfg))

    monkeypatch.setattr("sys.argv", ["main.py", "--mode", "eval", "--config", str(cfg_path)])
    with pytest.raises(SystemExit) as exc:
        carvision_main()
    assert exc.value.code == 1
