from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

import main as carvision_module
from tests.utils_carvision import build_test_config


def _run_cli(monkeypatch: pytest.MonkeyPatch, *args: object) -> None:
    argv = ["main.py", *[str(arg) for arg in args]]
    monkeypatch.setattr(sys, "argv", argv)
    carvision_module.main()


def test_cli_train_eval_predict_modes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    cfg, data_csv = build_test_config(tmp_path)
    # Entrenar una vez para generar artefactos reales reutilizables durante el CLI.
    train_result = carvision_module.train_model(cfg)
    assert "val_metrics" in train_result

    config_path = tmp_path / "config_cli.yaml"
    config_path.write_text(yaml.safe_dump(cfg))

    payload = pd.read_csv(data_csv).iloc[0].to_dict()
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps(payload))

    train_calls: list[dict] = []
    eval_calls: list[dict] = []

    def fake_train_model(cfg_in: dict) -> dict:
        train_calls.append(cfg_in)
        return train_result

    def fake_eval_model(cfg_in: dict) -> dict:
        eval_calls.append(cfg_in)
        return {"rmse": 123.0}

    monkeypatch.setattr(carvision_module, "train_model", fake_train_model)
    monkeypatch.setattr(carvision_module, "eval_model", fake_eval_model)
    monkeypatch.chdir(tmp_path)

    _run_cli(monkeypatch, "--mode", "train", "--config", config_path)
    capsys.readouterr()
    assert train_calls, "train_model no fue invocado desde el CLI"

    _run_cli(monkeypatch, "--mode", "eval", "--config", config_path)
    capsys.readouterr()
    assert eval_calls, "eval_model no fue invocado desde el CLI"

    _run_cli(
        monkeypatch,
        "--mode",
        "predict",
        "--config",
        config_path,
        "--input_json",
        payload_path,
    )
    predict_output = capsys.readouterr().out.strip()
    parsed = json.loads(predict_output)
    assert "prediction" in parsed


def test_cli_analysis_report_export_dashboard(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    dummy_df = pd.DataFrame(
        {
            "price": [10000, 15000, 20000],
            "model_year": [2015, 2016, 2017],
            "odometer": [50000, 40000, 30000],
            "condition": ["good", "excellent", "fair"],
            "model": ["ford focus", "honda civic", "audi a4"],
            "fuel": ["gas", "gas", "diesel"],
        }
    )
    csv_path = tmp_path / "analysis_input.csv"
    dummy_df.to_csv(csv_path, index=False)

    class DummyAnalyzer:
        def __init__(self, df: pd.DataFrame):
            self.df = df
            self.analysis_results = {
                "opportunities": [
                    {
                        "category": "Budget",
                        "count": 5,
                        "avg_price": 12000,
                        "potential_value": 1500,
                    }
                ],
                "market_by_brand": {
                    "volume": {"Ford": 10},
                    "pricing": {"mean": {"Ford": 15000}},
                },
                "depreciation": {"annual_rate": {"avg": 0.1}},
            }

        def generate_executive_summary(self) -> dict:
            return {
                "kpis": {
                    "total_vehicles": 3,
                    "average_price": 15000,
                    "total_market_value": 45000,
                    "total_opportunities": 5,
                    "potential_arbitrage_value": 1500,
                },
                "insights": {
                    "most_popular_brand": "Ford",
                    "highest_value_brand": "Ford",
                    "avg_depreciation_rate": 0.1,
                },
                "recommendations": ["rec1", "rec2"],
            }

    # Mock functions instead of class
    monkeypatch.setattr(carvision_module, "load_data", lambda x: dummy_df.copy())
    monkeypatch.setattr(carvision_module, "clean_data", lambda x: x)
    monkeypatch.setattr(carvision_module, "MarketAnalyzer", DummyAnalyzer)

    import subprocess

    dashboard_calls: list[list[str]] = []

    def fake_run(cmd: list[str], *_, **__):
        dashboard_calls.append(cmd)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)

    _run_cli(monkeypatch, "--mode", "analysis", "--input", csv_path)
    capsys.readouterr()

    report_base = tmp_path / "market_report"
    _run_cli(monkeypatch, "--mode", "report", "--input", csv_path, "--output", report_base)
    capsys.readouterr()
    assert (report_base.with_suffix(".html")).exists()

    export_path = tmp_path / "export_data"
    _run_cli(
        monkeypatch,
        "--mode",
        "export",
        "--input",
        csv_path,
        "--output",
        export_path,
        "--format",
        "json",
    )
    capsys.readouterr()
    assert (export_path.with_suffix(".json")).exists()

    _run_cli(monkeypatch, "--mode", "dashboard", "--port", 7777)
    capsys.readouterr()
    assert dashboard_calls, "Se esperaba que dashboard ejecutara subprocess.run"
