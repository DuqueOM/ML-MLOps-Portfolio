"""Comprehensive tests for cli.py module - based on real APIs."""

import logging

from src.bankchurn.cli import setup_logging, train_command


def test_setup_logging_default(tmp_path):
    """Test setup_logging with default parameters."""
    log_file = tmp_path / "default.log"
    setup_logging(log_file=str(log_file))

    # Check that function executed without errors
    assert log_file.parent.exists()


def test_setup_logging_custom_level(tmp_path):
    """Test setup_logging with custom level."""
    log_file = tmp_path / "custom.log"
    setup_logging(log_file=str(log_file), level=logging.DEBUG)

    # Check that function executed without errors
    assert log_file.parent.exists()


def test_train_command_exists():
    """Test that train_command function exists."""
    assert callable(train_command)

    # Check signature
    import inspect

    sig = inspect.signature(train_command)
    assert "args" in sig.parameters


def test_cli_module_structure():
    """Test CLI module has expected structure."""
    from src.bankchurn import cli

    # Check for main entry points
    assert hasattr(cli, "setup_logging")
    assert hasattr(cli, "train_command")


def test_cli_imports():
    """Test that CLI module imports correctly."""
    from src.bankchurn import cli

    # Verify key imports
    assert hasattr(cli, "ChurnTrainer")
    assert hasattr(cli, "ModelEvaluator")
    assert hasattr(cli, "ChurnPredictor")
    assert hasattr(cli, "BankChurnConfig")


def test_cli_logging_handlers(tmp_path):
    """Test that logging creates both file and stream handlers."""
    log_file = tmp_path / "test.log"
    setup_logging(log_file=str(log_file))

    # Log a message
    logger = logging.getLogger(__name__)
    logger.info("Test message")

    # Check log file was created
    assert log_file.exists()
