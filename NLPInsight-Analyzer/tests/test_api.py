"""Tests for NLPInsight FastAPI application."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client_no_model():
    """FastAPI test client without model loaded."""
    with patch("app.fastapi_app.predictor", None):
        from app.fastapi_app import app

        yield TestClient(app)


@pytest.fixture
def mock_predictor():
    """Mock SentimentPredictor."""
    pred = MagicMock()
    pred.model_path = "/models"
    pred.device = "cpu"
    pred.id2label = {0: "negative", 1: "positive"}
    pred.label2id = {"negative": 0, "positive": 1}
    pred.predict.return_value = {
        "label": "positive",
        "confidence": 0.95,
        "all_scores": {"negative": 0.05, "positive": 0.95},
    }
    pred.predict_batch.return_value = [
        {
            "label": "positive",
            "confidence": 0.95,
            "all_scores": {"negative": 0.05, "positive": 0.95},
        },
        {
            "label": "negative",
            "confidence": 0.88,
            "all_scores": {"negative": 0.88, "positive": 0.12},
        },
    ]
    return pred


@pytest.fixture
def client_with_model(mock_predictor):
    """FastAPI test client with mock model loaded."""
    with patch("app.fastapi_app.predictor", mock_predictor):
        from app.fastapi_app import app

        yield TestClient(app)


class TestHealthEndpoint:
    def test_health_no_model(self, client_no_model):
        resp = client_no_model.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "degraded"
        assert data["model_loaded"] is False

    def test_health_with_model(self, client_with_model):
        resp = client_with_model.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True


class TestPredictEndpoint:
    def test_predict_no_model(self, client_no_model):
        resp = client_no_model.post("/predict", json={"text": "hello"})
        assert resp.status_code == 503

    def test_predict_success(self, client_with_model, mock_predictor):
        resp = client_with_model.post("/predict", json={"text": "Great product!"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["prediction"]["label"] == "positive"
        assert data["prediction"]["confidence"] > 0
        assert "inference_time_ms" in data
        mock_predictor.predict.assert_called_once()

    def test_predict_empty_text(self, client_with_model):
        resp = client_with_model.post("/predict", json={"text": ""})
        assert resp.status_code == 422

    def test_predict_whitespace_only(self, client_with_model):
        resp = client_with_model.post("/predict", json={"text": "   "})
        assert resp.status_code == 422


class TestBatchEndpoint:
    def test_batch_predict(self, client_with_model, mock_predictor):
        resp = client_with_model.post(
            "/predict_batch",
            json={"texts": [{"text": "Great!"}, {"text": "Terrible!"}]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 2
        assert len(data["predictions"]) == 2

    def test_batch_no_model(self, client_no_model):
        resp = client_no_model.post(
            "/predict_batch",
            json={"texts": [{"text": "hello"}]},
        )
        assert resp.status_code == 503

    def test_batch_empty_list(self, client_with_model):
        resp = client_with_model.post("/predict_batch", json={"texts": []})
        assert resp.status_code == 422


class TestModelInfoEndpoint:
    def test_model_info(self, client_with_model):
        resp = client_with_model.get("/model_info")
        assert resp.status_code == 200
        data = resp.json()
        assert "labels" in data
        assert "num_labels" in data

    def test_model_info_no_model(self, client_no_model):
        resp = client_no_model.get("/model_info")
        assert resp.status_code == 503


class TestMetricsEndpoint:
    def test_metrics(self, client_with_model):
        resp = client_with_model.get("/metrics")
        assert resp.status_code == 200
