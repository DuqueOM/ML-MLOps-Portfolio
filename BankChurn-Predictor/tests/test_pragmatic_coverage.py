"""Pragmatic tests to reach 70% coverage threshold."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.bankchurn.config import BankChurnConfig
from src.bankchurn.evaluation import ModelEvaluator
from src.bankchurn.prediction import ChurnPredictor
from src.bankchurn.training import ChurnTrainer


@pytest.fixture
def cfg():
    """Quick config."""
    p = Path(__file__).parent.parent / "configs" / "config.yaml"
    return BankChurnConfig.from_yaml(p)


@pytest.fixture
def simple_model():
    """Simple fitted model."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler

    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.choice([0, 1], 100)

    scaler = StandardScaler().fit(X)
    model = RandomForestClassifier(n_estimators=5, random_state=42).fit(scaler.transform(X), y)

    return model, scaler


def test_trainer_load_nonexistent_raises(cfg):
    """Test file not found."""
    t = ChurnTrainer(cfg)
    with pytest.raises(FileNotFoundError):
        t.load_data("/tmp/does_not_exist_123456.csv")


def test_trainer_save_creates_dirs(cfg, tmp_path):
    """Test save_model creates parent dirs."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler

    t = ChurnTrainer(cfg)
    t.model_ = RandomForestClassifier(n_estimators=3, random_state=42)
    t.preprocessor_ = StandardScaler()

    # Fit on dummy data
    X = np.random.randn(10, 3)
    y = np.random.choice([0, 1], 10)
    t.preprocessor_.fit(X)
    t.model_.fit(t.preprocessor_.transform(X), y)

    # Save to nested path
    nested = tmp_path / "models" / "v1"
    t.save_model(nested / "m.pkl", nested / "p.pkl")

    assert (nested / "m.pkl").exists()


def test_evaluator_evaluate_computes_all_metrics(cfg, simple_model):
    """Test evaluate computes full metrics dict."""
    model, scaler = simple_model

    ev = ModelEvaluator(model, scaler)

    X_test = pd.DataFrame(np.random.randn(30, 5))
    y_test = pd.Series(np.random.choice([0, 1], 30))

    metrics = ev.evaluate(X_test, y_test)

    assert "accuracy" in metrics
    assert metrics["accuracy"] >= 0
    assert metrics["accuracy"] <= 1


def test_predictor_predict_single_row(cfg, simple_model):
    """Test prediction on single row."""
    model, scaler = simple_model

    pred = ChurnPredictor(model, scaler)

    X = pd.DataFrame(np.random.randn(1, 5))
    result = pred.predict(X)

    assert len(result) == 1


def test_predictor_predict_no_proba(cfg, simple_model):
    """Test prediction without probabilities."""
    model, scaler = simple_model

    pred = ChurnPredictor(model, scaler)

    X = pd.DataFrame(np.random.randn(5, 5))
    result = pred.predict(X, include_proba=False)

    assert isinstance(result, pd.DataFrame)


def test_predictor_predict_custom_threshold(cfg, simple_model):
    """Test prediction with custom threshold."""
    model, scaler = simple_model

    pred = ChurnPredictor(model, scaler)

    X = pd.DataFrame(np.random.randn(5, 5))
    result = pred.predict(X, threshold=0.3)

    assert len(result) == 5


def test_trainer_random_state_used(cfg):
    """Test random state is used."""
    t1 = ChurnTrainer(cfg, random_state=42)
    t2 = ChurnTrainer(cfg, random_state=99)

    assert t1.random_state == 42
    assert t2.random_state == 99


def test_trainer_prepare_removes_target(cfg):
    """Test prepare removes target from X."""
    t = ChurnTrainer(cfg)

    data = pd.DataFrame({"a": [1, 2], "b": [3, 4], "Exited": [0, 1]})

    X, y = t.prepare_features(data)

    assert "Exited" not in X.columns
    assert len(y) == 2


def test_evaluator_stores_model_and_preprocessor(cfg, simple_model):
    """Test evaluator stores artifacts."""
    model, scaler = simple_model

    ev = ModelEvaluator(model, scaler)

    assert ev.model is model
    assert ev.preprocessor is scaler


def test_predictor_stores_model_and_preprocessor(cfg, simple_model):
    """Test predictor stores artifacts."""
    model, scaler = simple_model

    pred = ChurnPredictor(model, scaler)

    assert pred.model is model
    assert pred.preprocessor is scaler


def test_config_loads_successfully(cfg):
    """Test config loads all sections."""
    assert cfg is not None
    assert cfg.data is not None
    assert cfg.model is not None
    assert cfg.mlflow is not None


def test_trainer_build_model_returns_pipeline(cfg):
    """Test build_model returns sklearn-compatible object."""
    t = ChurnTrainer(cfg)
    m = t.build_model()

    assert hasattr(m, "fit")
    assert hasattr(m, "predict")


def test_evaluator_initial_metrics_empty(cfg, simple_model):
    """Test evaluator starts with empty metrics."""
    model, scaler = simple_model
    ev = ModelEvaluator(model, scaler)

    assert ev.metrics_ == {}


def test_predictor_from_files_loads(cfg, simple_model, tmp_path):
    """Test from_files class method."""
    import joblib

    model, scaler = simple_model

    m_path = tmp_path / "m.pkl"
    s_path = tmp_path / "s.pkl"

    joblib.dump(model, m_path)
    joblib.dump(scaler, s_path)

    pred = ChurnPredictor.from_files(m_path, s_path)

    assert pred is not None
    assert pred.model is not None


def test_evaluator_from_files_loads(cfg, simple_model, tmp_path):
    """Test from_files class method for evaluator."""
    import joblib

    model, scaler = simple_model

    m_path = tmp_path / "m.pkl"
    s_path = tmp_path / "s.pkl"

    joblib.dump(model, m_path)
    joblib.dump(scaler, s_path)

    ev = ModelEvaluator.from_files(m_path, s_path)

    assert ev is not None
    assert ev.model is not None
