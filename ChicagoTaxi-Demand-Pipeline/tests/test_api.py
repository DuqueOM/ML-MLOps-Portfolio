"""Tests for ChicagoTaxi Demand Pipeline FastAPI application."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_predictions():
    """Create mock prediction DataFrame."""
    np.random.seed(42)
    n = 100
    return pd.DataFrame(
        {
            "year": np.random.choice([2022, 2023], n),
            "month": np.random.randint(1, 13, n),
            "day": np.random.randint(1, 29, n),
            "hour": np.random.randint(0, 24, n),
            "day_of_week": np.random.randint(1, 8, n),
            "is_weekend": np.random.choice([0, 1], n),
            "pickup_community_area": np.random.randint(1, 78, n),
            "avg_distance_miles": np.random.uniform(1, 20, n).round(2),
            "avg_fare": np.random.uniform(5, 50, n).round(2),
            "avg_speed_mph": np.random.uniform(10, 40, n).round(2),
            "predicted_demand": np.random.uniform(1, 100, n).round(1),
            "demand_category": np.random.choice(["low", "medium", "high", "very_high"], n),
        }
    )


@pytest.fixture
def client(mock_predictions):
    """Create test client with mocked predictions."""
    import app.fastapi_app as app_module

    app_module.predictions_df = mock_predictions
    app_module.etl_metadata = {
        "raw_rows": 6364313,
        "clean_rows": 5369172,
        "drop_rate_pct": 15.64,
        "hourly_demand_rows": 357055,
        "processing_time_seconds": 1342.5,
        "throughput_rows_per_sec": 4741,
        "spark_version": "4.1.1",
        "partitioning": "year/month",
        "compression": "snappy",
    }
    app_module.prediction_summary = {"total_predictions": 357055}

    return TestClient(app_module.app)


class TestHealthEndpoint:
    def test_health_with_predictions(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["predictions_loaded"] is True
        assert data["total_predictions"] == 100
        assert "uptime_seconds" in data

    def test_health_without_predictions(self):
        import app.fastapi_app as app_module

        app_module.predictions_df = None
        test_client = TestClient(app_module.app)
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "degraded"


class TestRootEndpoint:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "ChicagoTaxi" in data["message"]
        assert data["version"] == "1.0.0"


class TestDemandEndpoint:
    def test_demand_all(self, client):
        response = client.get("/demand?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10
        assert all("predicted_demand" in d for d in data)

    def test_demand_by_area(self, client):
        response = client.get("/demand?area=8&limit=5")
        assert response.status_code == 200
        data = response.json()
        for d in data:
            assert d["pickup_community_area"] == 8

    def test_demand_by_hour(self, client):
        response = client.get("/demand?hour=14&limit=5")
        assert response.status_code == 200
        data = response.json()
        for d in data:
            assert d["hour"] == 14

    def test_demand_503_without_predictions(self):
        import app.fastapi_app as app_module

        app_module.predictions_df = None
        test_client = TestClient(app_module.app)
        response = test_client.get("/demand")
        assert response.status_code == 503


class TestAreasEndpoint:
    def test_areas(self, client):
        response = client.get("/areas")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all("area_id" in a for a in data)
        assert all("avg_demand" in a for a in data)


class TestMetricsEndpoint:
    def test_metrics_returns_prometheus_format(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200
        # Should contain prometheus_client output
        assert b"chicagotaxi" in response.content or response.status_code == 200


class TestDemandDayOfWeek:
    def test_demand_by_day_of_week(self, client):
        response = client.get("/demand?day_of_week=1&limit=5")
        assert response.status_code == 200
        data = response.json()
        for d in data:
            assert d["day_of_week"] == 1

    def test_demand_combined_filters(self, client):
        response = client.get("/demand?area=8&hour=14&day_of_week=2&limit=5")
        assert response.status_code == 200


class TestAreasEndpoint503:
    def test_areas_503_without_predictions(self):
        import app.fastapi_app as app_module

        app_module.predictions_df = None
        test_client = TestClient(app_module.app)
        response = test_client.get("/areas")
        assert response.status_code == 503


class TestLoadPredictions:
    def test_load_predictions_missing_dir(self):
        import os

        import app.fastapi_app as app_module

        old = os.environ.get("PREDICTIONS_PATH", "")
        os.environ["PREDICTIONS_PATH"] = "/nonexistent/path"
        result = app_module.load_predictions()
        assert result is False
        if old:
            os.environ["PREDICTIONS_PATH"] = old
        else:
            os.environ.pop("PREDICTIONS_PATH", None)

    def test_load_predictions_invalid_parquet(self, tmp_path):
        import os

        import app.fastapi_app as app_module

        # Create a dir with an invalid file
        bad_dir = tmp_path / "bad_parquet"
        bad_dir.mkdir()
        (bad_dir / "data.parquet").write_text("not a parquet")

        old = os.environ.get("PREDICTIONS_PATH", "")
        os.environ["PREDICTIONS_PATH"] = str(bad_dir)
        result = app_module.load_predictions()
        assert result is False
        if old:
            os.environ["PREDICTIONS_PATH"] = old
        else:
            os.environ.pop("PREDICTIONS_PATH", None)


class TestPipelineStatus:
    def test_pipeline_status(self, client):
        response = client.get("/pipeline/status")
        assert response.status_code == 200
        data = response.json()
        assert data["raw_rows"] == 6364313
        assert data["clean_rows"] == 5369172
        assert data["spark_version"] == "4.1.1"

    def test_pipeline_status_no_metadata(self):
        import app.fastapi_app as app_module

        app_module.etl_metadata = {}
        test_client = TestClient(app_module.app)
        response = test_client.get("/pipeline/status")
        assert response.status_code == 404
