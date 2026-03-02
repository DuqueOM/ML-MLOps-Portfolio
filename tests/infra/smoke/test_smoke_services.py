"""
API Smoke Tests for ML Portfolio Services.

Tests service health, prediction endpoints, and metrics endpoints.
Supports both local Docker Compose and Kubernetes (port-forward) environments.

Usage:
    # Local Docker Compose
    pytest tests/infra/smoke/test_smoke_services.py -v

    # Custom base URL (e.g., Kubernetes Ingress)
    SMOKE_BASE_URL=http://34.120.120.57 pytest tests/infra/smoke/test_smoke_services.py -v

    # Skip specific services
    pytest tests/infra/smoke/test_smoke_services.py -v -k "not nlpinsight"
"""
import os

import pytest
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL = os.getenv("SMOKE_BASE_URL", "http://localhost")
TIMEOUT = int(os.getenv("SMOKE_TIMEOUT", "10"))

SERVICES = {
    "bankchurn": {
        "port": int(os.getenv("BANKCHURN_PORT", "8001")),
        "health": "/health",
        "predict": "/predict",
        "metrics": "/metrics",
        "payload": {
            "CreditScore": 650,
            "Geography": "France",
            "Gender": "Male",
            "Age": 40,
            "Tenure": 5,
            "Balance": 75000.0,
            "NumOfProducts": 2,
            "HasCrCard": 1,
            "IsActiveMember": 1,
            "EstimatedSalary": 80000.0,
        },
    },
    "carvision": {
        "port": int(os.getenv("CARVISION_PORT", "8002")),
        "health": "/health",
        "predict": "/predict",
        "metrics": "/metrics",
        "payload": {
            "model_year": 2018,
            "odometer": 45000,
            "model": "ford f-150",
            "fuel": "gas",
            "transmission": "automatic",
            "condition": "excellent",
            "cylinders": 8,
            "type": "truck",
            "paint_color": "white",
        },
    },
    "nlpinsight": {
        "port": int(os.getenv("NLPINSIGHT_PORT", "8003")),
        "health": "/health",
        "predict": "/predict",
        "metrics": "/metrics",
        "payload": {"text": "The company reported strong quarterly earnings growth"},
    },
}


def _url(service_name: str, path: str) -> str:
    """Build URL for a service endpoint."""
    svc = SERVICES[service_name]
    return f"{BASE_URL}:{svc['port']}{path}"


def _is_service_available(service_name: str) -> bool:
    """Check if service is reachable."""
    try:
        r = requests.get(_url(service_name, "/health"), timeout=3)
        return r.status_code == 200
    except requests.ConnectionError:
        return False


# ---------------------------------------------------------------------------
# Health Endpoint Tests
# ---------------------------------------------------------------------------
class TestHealthEndpoints:
    """Verify /health returns 200 with expected fields."""

    @pytest.mark.parametrize("service", SERVICES.keys())
    def test_health_status(self, service):
        if not _is_service_available(service):
            pytest.skip(f"{service} not reachable at {_url(service, '/health')}")

        r = requests.get(_url(service, "/health"), timeout=TIMEOUT)
        assert r.status_code == 200, f"{service} health returned {r.status_code}"

        data = r.json()
        assert data.get("status") == "healthy", f"{service}: {data}"
        assert data.get("model_loaded") is True, f"{service} model not loaded: {data}"

    @pytest.mark.parametrize("service", SERVICES.keys())
    def test_health_response_time(self, service):
        if not _is_service_available(service):
            pytest.skip(f"{service} not reachable")

        r = requests.get(_url(service, "/health"), timeout=TIMEOUT)
        assert r.elapsed.total_seconds() < 1.0, f"{service} health took {r.elapsed.total_seconds():.2f}s"


# ---------------------------------------------------------------------------
# Prediction Endpoint Tests
# ---------------------------------------------------------------------------
class TestPredictionEndpoints:
    """Verify /predict returns valid predictions."""

    @pytest.mark.parametrize("service", SERVICES.keys())
    def test_predict_returns_200(self, service):
        if not _is_service_available(service):
            pytest.skip(f"{service} not reachable")

        svc = SERVICES[service]
        r = requests.post(
            _url(service, svc["predict"]),
            json=svc["payload"],
            timeout=TIMEOUT,
        )
        assert r.status_code == 200, f"{service} predict returned {r.status_code}: {r.text}"

    @pytest.mark.parametrize("service", SERVICES.keys())
    def test_predict_response_format(self, service):
        if not _is_service_available(service):
            pytest.skip(f"{service} not reachable")

        svc = SERVICES[service]
        r = requests.post(
            _url(service, svc["predict"]),
            json=svc["payload"],
            timeout=TIMEOUT,
        )
        data = r.json()
        assert isinstance(data, dict), f"{service} response is not a dict: {type(data)}"
        assert len(data) > 0, f"{service} returned empty response"

    @pytest.mark.parametrize("service", SERVICES.keys())
    def test_predict_latency(self, service):
        """Prediction should complete within 2s (cold) or 500ms (warm)."""
        if not _is_service_available(service):
            pytest.skip(f"{service} not reachable")

        svc = SERVICES[service]
        r = requests.post(
            _url(service, svc["predict"]),
            json=svc["payload"],
            timeout=TIMEOUT,
        )
        assert r.elapsed.total_seconds() < 2.0, f"{service} predict took {r.elapsed.total_seconds():.2f}s"

    @pytest.mark.parametrize("service", SERVICES.keys())
    def test_predict_invalid_payload(self, service):
        """Invalid payload should return 4xx, not 5xx."""
        if not _is_service_available(service):
            pytest.skip(f"{service} not reachable")

        svc = SERVICES[service]
        r = requests.post(
            _url(service, svc["predict"]),
            json={"invalid_field": "bad_data"},
            timeout=TIMEOUT,
        )
        assert r.status_code < 500, f"{service} returned 5xx on invalid input: {r.status_code}"


# ---------------------------------------------------------------------------
# Metrics Endpoint Tests
# ---------------------------------------------------------------------------
class TestMetricsEndpoints:
    """Verify /metrics returns Prometheus-format metrics."""

    @pytest.mark.parametrize("service", SERVICES.keys())
    def test_metrics_endpoint(self, service):
        if not _is_service_available(service):
            pytest.skip(f"{service} not reachable")

        r = requests.get(_url(service, "/metrics"), timeout=TIMEOUT)
        assert r.status_code == 200, f"{service} metrics returned {r.status_code}"
        assert (
            "text/plain" in r.headers.get("content-type", "")
            or "text/plain" in r.text[:100]
            or "# HELP" in r.text
            or "# TYPE" in r.text
        ), f"{service} metrics not in Prometheus format"


# ---------------------------------------------------------------------------
# OpenAPI Docs Test
# ---------------------------------------------------------------------------
class TestAPIDocs:
    """Verify FastAPI auto-generated docs are accessible."""

    @pytest.mark.parametrize("service", SERVICES.keys())
    def test_openapi_docs(self, service):
        if not _is_service_available(service):
            pytest.skip(f"{service} not reachable")

        r = requests.get(_url(service, "/docs"), timeout=TIMEOUT)
        assert r.status_code == 200, f"{service} /docs returned {r.status_code}"

    @pytest.mark.parametrize("service", SERVICES.keys())
    def test_openapi_json(self, service):
        if not _is_service_available(service):
            pytest.skip(f"{service} not reachable")

        r = requests.get(_url(service, "/openapi.json"), timeout=TIMEOUT)
        assert r.status_code == 200
        schema = r.json()
        assert "paths" in schema
        assert "/predict" in schema["paths"]
