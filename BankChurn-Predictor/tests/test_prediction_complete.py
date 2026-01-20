"""Complete tests for ChurnPredictor to improve coverage."""

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.bankchurn.prediction import ChurnPredictor


@pytest.fixture
def trained_pipeline():
    """Create a trained Pipeline model."""
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.choice([0, 1], 100)

    pipeline = Pipeline(
        [
            ("preprocessor", StandardScaler()),
            ("clf", RandomForestClassifier(n_estimators=10, random_state=42)),
        ]
    )
    pipeline.fit(X, y)
    return pipeline


@pytest.fixture
def fitted_preprocessor():
    """Create fitted preprocessor."""
    np.random.seed(42)
    X = np.random.randn(100, 5)
    preprocessor = StandardScaler()
    preprocessor.fit(X)
    return preprocessor


@pytest.fixture
def prediction_data():
    """Create data for predictions."""
    np.random.seed(42)
    return pd.DataFrame(np.random.randn(20, 5), columns=[f"f{i}" for i in range(5)])


# ===== Tests for predict_batch =====


def test_predict_batch_with_csv_files(trained_pipeline, tmp_path):
    """Test predict_batch reads CSV, predicts, and saves results."""
    predictor = ChurnPredictor(trained_pipeline)

    # Create input CSV
    input_csv = tmp_path / "input.csv"
    input_data = pd.DataFrame(np.random.randn(10, 5), columns=[f"f{i}" for i in range(5)])
    input_data.to_csv(input_csv, index=False)

    # Run predict_batch
    output_csv = tmp_path / "output.csv"
    result = predictor.predict_batch(input_csv, output_csv, include_proba=True)

    # Verify output CSV exists
    assert output_csv.exists()

    # Verify result DataFrame
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 10
    assert "prediction" in result.columns

    # Verify saved CSV can be read
    saved_data = pd.read_csv(output_csv)
    assert len(saved_data) == 10
    assert "prediction" in saved_data.columns


def test_predict_batch_creates_output_directory(trained_pipeline, tmp_path):
    """Test predict_batch creates output directory if it doesn't exist."""
    predictor = ChurnPredictor(trained_pipeline)

    # Create input CSV
    input_csv = tmp_path / "input.csv"
    input_data = pd.DataFrame(np.random.randn(5, 5), columns=[f"f{i}" for i in range(5)])
    input_data.to_csv(input_csv, index=False)

    # Output in non-existent directory
    output_csv = tmp_path / "subdir" / "nested" / "output.csv"
    predictor.predict_batch(input_csv, output_csv)

    # Verify directory was created
    assert output_csv.parent.exists()
    assert output_csv.exists()


def test_predict_batch_file_not_found(trained_pipeline, tmp_path):
    """Test predict_batch raises FileNotFoundError for missing input."""
    predictor = ChurnPredictor(trained_pipeline)

    nonexistent_csv = tmp_path / "nonexistent.csv"
    output_csv = tmp_path / "output.csv"

    with pytest.raises(FileNotFoundError, match="Input file not found"):
        predictor.predict_batch(nonexistent_csv, output_csv)


def test_predict_batch_without_proba(trained_pipeline, tmp_path):
    """Test predict_batch without probabilities."""
    predictor = ChurnPredictor(trained_pipeline)

    # Create input CSV
    input_csv = tmp_path / "input.csv"
    input_data = pd.DataFrame(np.random.randn(5, 5), columns=[f"f{i}" for i in range(5)])
    input_data.to_csv(input_csv, index=False)

    # Run without probabilities
    output_csv = tmp_path / "output.csv"
    result = predictor.predict_batch(input_csv, output_csv, include_proba=False)

    assert isinstance(result, pd.DataFrame)
    assert "prediction" in result.columns


def test_predict_batch_with_custom_threshold(trained_pipeline, tmp_path):
    """Test predict_batch with custom threshold."""
    predictor = ChurnPredictor(trained_pipeline)

    # Create input CSV
    input_csv = tmp_path / "input.csv"
    input_data = pd.DataFrame(np.random.randn(5, 5), columns=[f"f{i}" for i in range(5)])
    input_data.to_csv(input_csv, index=False)

    # Run with custom threshold
    output_csv = tmp_path / "output.csv"
    result = predictor.predict_batch(input_csv, output_csv, threshold=0.7)

    assert isinstance(result, pd.DataFrame)
    assert "prediction" in result.columns


# ===== Tests for explain_prediction =====


def test_explain_prediction_basic(trained_pipeline, prediction_data):
    """Test explain_prediction returns dict with expected keys."""
    predictor = ChurnPredictor(trained_pipeline)

    result = predictor.explain_prediction(prediction_data, sample_idx=0)

    assert isinstance(result, dict)
    assert "sample_idx" in result
    assert "prediction" in result
    assert "probability" in result
    assert "input_features" in result
    assert result["sample_idx"] == 0
    assert result["prediction"] in [0, 1]
    assert isinstance(result["input_features"], dict)


def test_explain_prediction_different_indices(trained_pipeline, prediction_data):
    """Test explain_prediction works with different sample indices."""
    predictor = ChurnPredictor(trained_pipeline)

    # Test first sample
    result_0 = predictor.explain_prediction(prediction_data, sample_idx=0)
    assert result_0["sample_idx"] == 0

    # Test middle sample
    result_5 = predictor.explain_prediction(prediction_data, sample_idx=5)
    assert result_5["sample_idx"] == 5

    # Test last sample
    result_last = predictor.explain_prediction(prediction_data, sample_idx=len(prediction_data) - 1)
    assert result_last["sample_idx"] == len(prediction_data) - 1


def test_explain_prediction_with_non_pipeline_model(fitted_preprocessor, prediction_data):
    """Test explain_prediction with non-Pipeline model."""
    # Create and train a non-Pipeline model
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.choice([0, 1], 100)

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    X_transformed = fitted_preprocessor.transform(X)
    model.fit(X_transformed, y)

    predictor = ChurnPredictor(model, fitted_preprocessor)

    result = predictor.explain_prediction(prediction_data, sample_idx=0)

    assert isinstance(result, dict)
    assert "prediction" in result
    assert "probability" in result


# ===== Tests for edge cases =====


def test_predict_without_preprocessor_raises(prediction_data):
    """Test error when using non-Pipeline model without preprocessor."""
    # Create model without Pipeline
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.choice([0, 1], 100)

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)

    # Create predictor without preprocessor
    predictor = ChurnPredictor(model, preprocessor=None)

    # Should raise ValueError
    with pytest.raises(ValueError, match="Preprocessor required"):
        predictor.predict(prediction_data)


def test_from_files_missing_preprocessor(trained_pipeline, tmp_path):
    """Test from_files handles missing preprocessor gracefully."""
    model_path = tmp_path / "model.pkl"
    joblib.dump(trained_pipeline, model_path)

    # Call with non-existent preprocessor path
    nonexistent_preprocessor = tmp_path / "nonexistent.pkl"
    predictor = ChurnPredictor.from_files(model_path, nonexistent_preprocessor)

    # Should load model successfully
    assert predictor.model is not None
    # Preprocessor should be extracted from Pipeline
    assert predictor.preprocessor is not None


def test_from_files_without_preprocessor_path(trained_pipeline, tmp_path):
    """Test from_files works without preprocessor path for Pipeline models."""
    model_path = tmp_path / "model.pkl"
    joblib.dump(trained_pipeline, model_path)

    # Load without preprocessor path
    predictor = ChurnPredictor.from_files(model_path, preprocessor_path=None)

    assert predictor.model is not None
    # Should extract preprocessor from Pipeline
    assert predictor.preprocessor is not None


def test_predict_with_pipeline_extracts_preprocessor():
    """Test that Pipeline model automatically extracts preprocessor."""
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.choice([0, 1], 100)

    # Create Pipeline with named 'preprocessor' step
    pipeline = Pipeline(
        [
            ("preprocessor", StandardScaler()),
            ("clf", RandomForestClassifier(n_estimators=10, random_state=42)),
        ]
    )
    pipeline.fit(X, y)

    # Create predictor without explicit preprocessor
    predictor = ChurnPredictor(pipeline, preprocessor=None)

    # Should have extracted preprocessor
    assert predictor.preprocessor is not None
    assert isinstance(predictor.preprocessor, StandardScaler)


def test_predict_multiclass():
    """Test predictions with multi-class model."""
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.choice([0, 1, 2], 100)  # 3 classes

    model = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(n_estimators=10, random_state=42)),
        ]
    )
    model.fit(X, y)

    predictor = ChurnPredictor(model)

    # Make predictions
    test_data = pd.DataFrame(np.random.randn(5, 5), columns=[f"f{i}" for i in range(5)])
    result = predictor.predict(test_data, include_proba=True)

    # Should have probability columns for each class
    assert "prediction" in result.columns
    assert "probability_class_0" in result.columns
    assert "probability_class_1" in result.columns
    assert "probability_class_2" in result.columns


def test_predict_without_proba_support():
    """Test graceful handling when model doesn't support predict_proba."""
    from sklearn.svm import LinearSVC

    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.choice([0, 1], 100)

    # LinearSVC doesn't have predict_proba by default
    model = Pipeline([("scaler", StandardScaler()), ("clf", LinearSVC(random_state=42, max_iter=1000))])
    model.fit(X, y)

    predictor = ChurnPredictor(model)

    # Should work without crashing
    test_data = pd.DataFrame(np.random.randn(5, 5), columns=[f"f{i}" for i in range(5)])
    result = predictor.predict(test_data, include_proba=True)

    # Should have predictions but no probabilities
    assert "prediction" in result.columns
    # Should not have probability column since model doesn't support it
    assert "probability" not in result.columns or result["probability"].isna().all()


def test_init_extracts_preprocessor_from_pipeline():
    """Test that __init__ extracts preprocessor from Pipeline automatically."""
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.choice([0, 1], 100)

    pipeline = Pipeline(
        [
            ("preprocessor", StandardScaler()),
            ("clf", RandomForestClassifier(n_estimators=10, random_state=42)),
        ]
    )
    pipeline.fit(X, y)

    # Create predictor with Pipeline but no explicit preprocessor
    predictor = ChurnPredictor(pipeline)

    # Should have extracted the preprocessor
    assert predictor.preprocessor is not None
    assert isinstance(predictor.preprocessor, StandardScaler)


def test_init_handles_pipeline_without_preprocessor_step():
    """Test __init__ handles Pipeline without 'preprocessor' step gracefully."""
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.choice([0, 1], 100)

    # Pipeline without 'preprocessor' step name
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(n_estimators=10, random_state=42)),
        ]
    )
    pipeline.fit(X, y)

    # Should not crash
    predictor = ChurnPredictor(pipeline)

    # preprocessor might be None or extracted differently
    assert predictor.model is not None
