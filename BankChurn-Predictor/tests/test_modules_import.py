"""Simple import and structural tests to boost coverage."""


def test_training_module_imports():
    """Test training module imports."""
    from src.bankchurn import training

    assert training is not None
    assert hasattr(training, "ChurnTrainer")


def test_evaluation_module_imports():
    """Test evaluation module imports."""
    from src.bankchurn import evaluation

    assert evaluation is not None
    assert hasattr(evaluation, "ModelEvaluator")


def test_prediction_module_imports():
    """Test prediction module imports."""
    from src.bankchurn import prediction

    assert prediction is not None
    assert hasattr(prediction, "ChurnPredictor")


def test_cli_module_imports():
    """Test CLI module imports."""
    from src.bankchurn import cli

    assert cli is not None
    assert hasattr(cli, "setup_logging")


def test_config_module_imports():
    """Test config module imports."""
    from src.bankchurn import config

    assert config is not None
    assert hasattr(config, "BankChurnConfig")


def test_models_module_imports():
    """Test models module imports."""
    from src.bankchurn import models

    assert models is not None
    assert hasattr(models, "ResampleClassifier")
