"""Tests for CLI module."""

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from src.bankchurn import cli
from src.bankchurn.cli import create_parser, evaluate_command, predict_command, setup_logging, train_command


def test_main_help():
    """Test that main.py runs and shows help."""
    # Assuming main.py is in the project root, two levels up from here if tests are in tests/
    # But wait, where is test_cli.py? It is in tests/.
    # Where is main.py? In root.

    # We can find main.py relative to this file
    root_dir = Path(__file__).parent.parent
    main_path = root_dir / "main.py"

    if not main_path.exists():
        pytest.skip("main.py not found")

    result = subprocess.run([sys.executable, str(main_path), "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "BankChurn Predictor" in result.stdout


@pytest.fixture
def mock_args():
    args = MagicMock()
    args.config = "configs/config.yaml"
    args.input = "data/raw/Churn.csv"
    args.model = "models/model.pkl"
    args.preprocessor = "models/preprocessor.pkl"
    args.metrics_output = "metrics.json"
    args.no_cv = True
    args.seed = 42
    args.output = "predictions.csv"
    args.threshold = 0.5
    args.no_proba = False
    args.fairness_features = "Gender"
    return args


@pytest.fixture
def mock_data():
    return pd.DataFrame(
        {
            "Exited": [0, 1] * 50,
            "CreditScore": np.random.randint(300, 850, 100),
            "Geography": ["France"] * 100,
            "Gender": ["Male"] * 100,
            "Age": np.random.randint(18, 90, 100),
            "Tenure": np.random.randint(0, 10, 100),
            "Balance": np.random.uniform(0, 200000, 100),
            "NumOfProducts": np.random.randint(1, 4, 100),
            "HasCrCard": np.random.randint(0, 2, 100),
            "IsActiveMember": np.random.randint(0, 2, 100),
            "EstimatedSalary": np.random.uniform(0, 200000, 100),
        }
    )


def test_cli_module_has_functions():
    """Test that CLI module has expected functions."""
    assert hasattr(cli, "setup_logging")
    assert hasattr(cli, "train_command")
    assert callable(cli.setup_logging)
    assert callable(cli.train_command)


def test_train_command_signature():
    """Test train_command has expected signature."""
    import inspect

    sig = inspect.signature(cli.train_command)
    params = list(sig.parameters.keys())
    assert "args" in params


def test_cli_has_main_function():
    """Test CLI has main entry point."""
    assert hasattr(cli, "train_command") or hasattr(cli, "main")


def test_setup_logging_default(tmp_path):
    """Test setup_logging with default parameters."""
    log_file = tmp_path / "default.log"
    setup_logging(log_file=str(log_file))
    assert log_file.parent.exists()


def test_setup_logging_custom_level(tmp_path):
    """Test setup_logging with custom level."""
    log_file = tmp_path / "custom.log"
    setup_logging(log_file=str(log_file), level=logging.DEBUG)
    assert log_file.parent.exists()


def test_train_command_exists():
    """Test that train_command function exists."""
    assert callable(train_command)


def test_cli_imports():
    """Test that CLI module imports correctly."""
    # Verify key imports
    assert hasattr(cli, "ChurnTrainer")
    assert hasattr(cli, "ModelEvaluator")
    assert hasattr(cli, "ChurnPredictor")
    assert hasattr(cli, "BankChurnConfig")


def test_cli_logging_handlers(tmp_path):
    """Test that logging creates both file and stream handlers."""
    log_file = tmp_path / "test.log"
    setup_logging(log_file=str(log_file))

    logger = logging.getLogger(__name__)
    logger.info("Test message")
    assert log_file.exists()


def test_parser_creation():
    parser = create_parser()
    assert isinstance(parser, argparse.ArgumentParser)


@patch("src.bankchurn.cli.BankChurnConfig")
@patch("src.bankchurn.cli.ChurnTrainer")
def test_train_command(mock_trainer_cls, mock_config_cls, mock_args, mock_data):
    # Setup mocks
    mock_config = MagicMock()
    mock_config.mlflow.enabled = False
    mock_config_cls.from_yaml.return_value = mock_config

    mock_trainer = mock_trainer_cls.return_value
    mock_trainer.load_data.return_value = mock_data
    mock_trainer.prepare_features.return_value = (
        mock_data.drop("Exited", axis=1),
        mock_data["Exited"],
    )
    mock_trainer.train.return_value = (MagicMock(), {"f1": 0.8})

    # Run
    exit_code = train_command(mock_args)

    # Verify
    assert exit_code == 0
    mock_trainer.train.assert_called_once()
    mock_trainer.save_model.assert_called_once()


@patch("src.bankchurn.cli.BankChurnConfig")
@patch("src.bankchurn.cli.ModelEvaluator")
@patch("pandas.read_csv")
def test_evaluate_command(mock_read_csv, mock_evaluator_cls, mock_config_cls, mock_args, mock_data):
    # Setup mocks
    mock_config = MagicMock()
    mock_config.data.target_column = "Exited"
    mock_config_cls.from_yaml.return_value = mock_config

    mock_read_csv.return_value = mock_data

    mock_evaluator = mock_evaluator_cls.from_files.return_value
    mock_evaluator.evaluate.return_value = {"accuracy": 0.9}
    mock_evaluator.compute_fairness_metrics.return_value = {"Gender": {}}

    # Run
    exit_code = evaluate_command(mock_args)

    # Verify
    assert exit_code == 0
    mock_evaluator.evaluate.assert_called_once()
    mock_evaluator.compute_fairness_metrics.assert_called_once()


@patch("src.bankchurn.cli.ChurnPredictor")
@patch("pandas.read_csv")
def test_predict_command(mock_read_csv, mock_predictor_cls, mock_args, mock_data):
    # Setup mocks
    mock_read_csv.return_value = mock_data.drop("Exited", axis=1)

    mock_predictor = mock_predictor_cls.from_files.return_value
    mock_predictor.predict_batch.return_value = pd.DataFrame({"prediction": [0] * 100})

    # Run
    exit_code = predict_command(mock_args)

    # Verify
    assert exit_code == 0
    mock_predictor.predict_batch.assert_called_once()
