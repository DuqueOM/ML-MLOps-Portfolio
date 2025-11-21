"""Final tests to push BankChurn to 70%+ coverage."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

from src.bankchurn.config import BankChurnConfig
from src.bankchurn.evaluation import ModelEvaluator
from src.bankchurn.prediction import ChurnPredictor
from src.bankchurn.training import ChurnTrainer


@pytest.fixture
def config():
    """Load valid config."""
    config_path = Path(__file__).parent.parent / "configs" / "config.yaml"
    return BankChurnConfig.from_yaml(config_path)


def test_trainer_attributes_initialization(config):
    """Test that trainer initializes all attributes correctly."""
    trainer = ChurnTrainer(config, random_state=99)

    assert trainer.config is not None
    assert trainer.random_state == 99
    assert trainer.model_ is None
    assert trainer.preprocessor_ is None
    assert trainer.train_score_ is None
    assert trainer.test_score_ is None


def test_trainer_load_data_path_handling(config, tmp_path):
    """Test that trainer handles Path objects correctly."""
    # Create sample data
    data = pd.DataFrame({"feature": [1, 2, 3], "Exited": [0, 1, 0]})

    # Test with string path
    str_path = str(tmp_path / "test.csv")
    data.to_csv(str_path, index=False)

    trainer = ChurnTrainer(config)
    loaded = trainer.load_data(str_path)
    assert len(loaded) == 3

    # Test with Path object
    path_obj = tmp_path / "test2.csv"
    data.to_csv(path_obj, index=False)
    loaded2 = trainer.load_data(path_obj)
    assert len(loaded2) == 3


def test_evaluator_metrics_storage(config):
    """Test that evaluator stores metrics correctly."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler

    # Create simple model
    model = RandomForestClassifier(n_estimators=5, random_state=42)
    preprocessor = StandardScaler()

    # Fit on dummy data
    X_train = np.random.randn(50, 3)
    y_train = np.random.choice([0, 1], 50)

    preprocessor.fit(X_train)
    model.fit(preprocessor.transform(X_train), y_train)

    # Create evaluator
    evaluator = ModelEvaluator(model, preprocessor)

    # Initial state
    assert evaluator.metrics_ == {}

    # Evaluate
    X_test = pd.DataFrame(np.random.randn(20, 3), columns=["f1", "f2", "f3"])
    y_test = pd.Series(np.random.choice([0, 1], 20))

    metrics = evaluator.evaluate(X_test, y_test)

    # Check metrics stored
    assert len(metrics) > 0
    assert "accuracy" in metrics


def test_predictor_returns_dataframe_with_predictions(config):
    """Test that predictor returns proper DataFrame."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler

    # Create and fit model
    model = RandomForestClassifier(n_estimators=5, random_state=42)
    preprocessor = StandardScaler()

    X = np.random.randn(50, 3)
    y = np.random.choice([0, 1], 50)

    preprocessor.fit(X)
    model.fit(preprocessor.transform(X), y)

    # Create predictor
    predictor = ChurnPredictor(model, preprocessor)

    # Make predictions
    X_new = pd.DataFrame(np.random.randn(10, 3), columns=["f1", "f2", "f3"])
    result = predictor.predict(X_new)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 10


def test_config_has_all_sections(config):
    """Test that config has all required sections."""
    assert hasattr(config, "data")
    assert hasattr(config, "model")
    assert hasattr(config, "mlflow")

    # Check data config
    assert hasattr(config.data, "target_column")

    # Check model config
    assert hasattr(config.model, "random_state")


def test_trainer_prepare_features_drops_target(config):
    """Test that prepare_features properly separates X and y."""
    data = pd.DataFrame({"f1": [1, 2, 3, 4, 5], "f2": ["a", "b", "c", "d", "e"], "Exited": [0, 1, 0, 1, 0]})

    trainer = ChurnTrainer(config)
    X, y = trainer.prepare_features(data)

    # X should not have target
    assert "Exited" not in X.columns

    # y should be the target
    assert len(y) == 5
    assert y.name == "Exited"


def test_trainer_build_preprocessor_returns_transformer(config):
    """Test that build_preprocessor returns ColumnTransformer."""
    from sklearn.compose import ColumnTransformer

    X = pd.DataFrame({"num": [1.0, 2.0, 3.0], "cat": ["A", "B", "C"]})

    trainer = ChurnTrainer(config)
    preprocessor = trainer.build_preprocessor(X)

    assert isinstance(preprocessor, ColumnTransformer)


def test_model_evaluator_from_files_loads_artifacts(tmp_path):
    """Test loading evaluator from saved files."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler

    # Create and save artifacts
    model = RandomForestClassifier(n_estimators=5)
    preprocessor = StandardScaler()

    X = np.random.randn(30, 3)
    y = np.random.choice([0, 1], 30)

    preprocessor.fit(X)
    model.fit(preprocessor.transform(X), y)

    model_path = tmp_path / "model.pkl"
    preprocessor_path = tmp_path / "preprocessor.pkl"

    joblib.dump(model, model_path)
    joblib.dump(preprocessor, preprocessor_path)

    # Load via from_files
    evaluator = ModelEvaluator.from_files(model_path, preprocessor_path)

    assert evaluator is not None
    assert evaluator.model is not None
    assert evaluator.preprocessor is not None
