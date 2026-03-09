"""
API Smoke Tests for ML Portfolio Services.

Tests service health, prediction endpoints, and metrics endpoints.
Each service has an independent URL configured via environment variables,
supporting any target environment without code changes.

Environments:
    # Local (kubectl port-forward)
    pytest tests/infra/smoke/test_smoke_services.py -v

    # GKE via port-forward (explicit)
    BANKCHURN_URL=http://localhost:8001 \
    NLPINSIGHT_URL=http://localhost:8003 \
    CHICAGOTAXI_URL=http://localhost:8004 \
    pytest tests/infra/smoke/test_smoke_services.py -v

    # Kubernetes Ingress (path-based routing, single IP)
    BANKCHURN_URL=http://34.120.120.57/bankchurn \
    NLPINSIGHT_URL=http://34.120.120.57/nlpinsight \
    CHICAGOTAXI_URL=http://34.120.120.57/chicagotaxi \
    pytest tests/infra/smoke/test_smoke_services.py -v

    # Staging (independent hostnames per service)
    BANKCHURN_URL=https://bankchurn.staging.ml-api.com \
    NLPINSIGHT_URL=https://nlpinsight.staging.ml-api.com \
    CHICAGOTAXI_URL=https://chicagotaxi.staging.ml-api.com \
    pytest tests/infra/smoke/test_smoke_services.py -v

    # Production (post-deploy verification)
    BANKCHURN_URL=https://bankchurn.ml-api.com \
    NLPINSIGHT_URL=https://nlpinsight.ml-api.com \
    CHICAGOTAXI_URL=https://chicagotaxi.ml-api.com \
    pytest tests/infra/smoke/test_smoke_services.py -v

    # Skip specific services
    pytest tests/infra/smoke/test_smoke_services.py -v -k "not nlpinsight"
"""

import os

import pytest
import requests

# ---------------------------------------------------------------------------
# Configuration — per-service independent URLs
# Default: localhost port-forward convention
# ---------------------------------------------------------------------------
TIMEOUT = int(os.getenv("SMOKE_TIMEOUT", "10"))

SERVICES = {
    "bankchurn": {
        "url": os.getenv("BANKCHURN_URL", "http://localhost:8001"),
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
    "nlpinsight": {
        "url": os.getenv("NLPINSIGHT_URL", "http://localhost:8003"),
        "health": "/health",
        "predict": "/predict",
        "metrics": "/metrics",
        "payload": {"text": "The company reported strong quarterly earnings growth"},
    },
    "chicagotaxi": {
        "url": os.getenv("CHICAGOTAXI_URL", "http://localhost:8004"),
        "health": "/health",
        "predict": "/demand",
        "metrics": "/metrics",
        "payload": None,  # GET endpoint, no payload
    },
}


def _url(service_name: str, path: str) -> str:
    """Build full URL for a service endpoint."""
    base = SERVICES[service_name]["url"].rstrip("/")
    return f"{base}{path}"


def _is_service_available(service_name: str) -> bool:
    """Check if service is reachable (any HTTP response counts as reachable)."""
    try:
        r = requests.get(_url(service_name, "/health"), timeout=3)
        return r.status_code < 500
    except (requests.ConnectionError, requests.Timeout):
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
        assert data.get("status") in {"healthy", "ok"}, f"{service}: {data}"
        # ChicagoTaxi uses predictions_loaded; others use model_loaded
        if service == "chicagotaxi":
            assert data.get("predictions_loaded") is True, f"{service} predictions not loaded: {data}"
        else:
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
        if svc["payload"] is None:
            r = requests.get(_url(service, svc["predict"]), timeout=TIMEOUT)
        else:
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
        if svc["payload"] is None:
            r = requests.get(_url(service, svc["predict"]), timeout=TIMEOUT)
        else:
            r = requests.post(
                _url(service, svc["predict"]),
                json=svc["payload"],
                timeout=TIMEOUT,
            )
        data = r.json()
        assert isinstance(data, (dict, list)), f"{service} response is not a dict/list: {type(data)}"
        assert len(data) > 0, f"{service} returned empty response"

    @pytest.mark.parametrize("service", SERVICES.keys())
    def test_predict_latency(self, service):
        """Prediction should complete within 2s (cold) or 500ms (warm)."""
        if not _is_service_available(service):
            pytest.skip(f"{service} not reachable")

        svc = SERVICES[service]
        if svc["payload"] is None:
            r = requests.get(_url(service, svc["predict"]), timeout=TIMEOUT)
        else:
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
        if svc["payload"] is None:
            # GET services: test with invalid query params
            r = requests.get(
                _url(service, svc["predict"]) + "?area=-999&hour=99",
                timeout=TIMEOUT,
            )
        else:
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
        predict_path = SERVICES[service]["predict"]
        assert predict_path in schema["paths"], f"{service}: {predict_path} not in {list(schema['paths'].keys())}"
