import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from src.telecom.training import build_model, build_preprocessor


@pytest.fixture
def synthetic_data():
    np.random.seed(42)
    data = pd.DataFrame(
        {
            "calls": np.random.uniform(10, 100, 50),
            "minutes": np.random.uniform(100, 1000, 50),
            "messages": np.random.randint(0, 100, 50),
            "mb_used": np.random.uniform(1000, 30000, 50),
            "is_ultra": np.random.randint(0, 2, 50),
        }
    )
    return data


def test_pipeline_structure(synthetic_data):
    """Ensure the pipeline is built with expected steps."""
    features = ["calls", "minutes", "messages", "mb_used"]

    # Test Preprocessor
    preprocessor = build_preprocessor(features)
    X = synthetic_data[features]
    X_transformed = preprocessor.fit_transform(X)
    assert X_transformed.shape == X.shape

    # Test Model Build
    model_cfg = {"name": "random_forest", "params": {"n_estimators": 10}}
    clf = build_model(model_cfg, seed=42)

    # Full Integration
    pipeline = Pipeline(steps=[("preprocess", preprocessor), ("clf", clf)])
    pipeline.fit(X, synthetic_data["is_ultra"])

    preds = pipeline.predict(X)
    assert len(preds) == 50


def test_model_determinism(synthetic_data):
    """Ensure training is deterministic with fixed seed."""
    features = ["calls", "minutes", "messages", "mb_used"]
    model_cfg = {"name": "random_forest", "params": {"n_estimators": 10}}

    results = []
    for _ in range(2):
        clf = build_model(model_cfg, seed=42)
        clf.fit(synthetic_data[features], synthetic_data["is_ultra"])
        results.append(clf.predict(synthetic_data[features]))

    np.testing.assert_array_equal(results[0], results[1])
