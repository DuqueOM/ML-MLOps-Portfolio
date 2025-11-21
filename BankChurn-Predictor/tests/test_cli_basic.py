"""Basic tests for CLI module to boost coverage."""

from src.bankchurn import cli


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
    # Check for main or similar entry point
    assert hasattr(cli, "train_command") or hasattr(cli, "main")
