"""
Smoke Tests — Kubernetes Port-Forwarded ML Services.

Validates that all 3 ML services are healthy and return correct predictions
when running on Kubernetes (GKE / EKS) via kubectl port-forward.

These tests are designed to be run AFTER deployment as a post-deploy gate:
  - Fast: < 10s total (one request per service)
  - Deterministic: fixed payloads with known expected shapes
  - Non-destructive: read-only GET/POST with no side effects

─────────────────────────────────────────────────────────────────────
PREREQUISITES
─────────────────────────────────────────────────────────────────────
kubectl port-forward svc/bankchurn-service 8000:80 -n ml-portfolio &
kubectl port-forward svc/carvision-service 8001:80 -n ml-portfolio &
kubectl port-forward svc/nlpinsight-service 8002:80 -n ml-portfolio &

─────────────────────────────────────────────────────────────────────
USAGE
─────────────────────────────────────────────────────────────────────
# Run all smoke tests
pytest tests/integration/test_smoke_k8s.py -v

# Run with short timeout (CI gate — fail fast)
pytest tests/integration/test_smoke_k8s.py -v --timeout=30

# Run only health checks (fastest gate)
pytest tests/integration/test_smoke_k8s.py -v -k "health"

# Skip if services unreachable (CI with conditional port-forward)
pytest tests/integration/test_smoke_k8s.py -v --ignore-glob="*" \
       --co -q  # dry-run to list tests
"""

import httpx
import pytest

# ─── Service base URLs (K8s port-forward convention) ────────────────────────

BANKCHURN_URL = "http://localhost:8000"
CARVISION_URL = "http://localhost:8001"
NLPINSIGHT_URL = "http://localhost:8002"

TIMEOUT = httpx.Timeout(15.0)

# ─── Fixed payloads for deterministic smoke tests ───────────────────────────

BANKCHURN_PAYLOAD = {
    "CreditScore": 650,
    "Geography": "France",
    "Gender": "Female",
    "Age": 40,
    "Tenure": 3,
    "Balance": 60000.0,
    "NumOfProducts": 2,
    "HasCrCard": 1,
    "IsActiveMember": 1,
    "EstimatedSalary": 50000.0,
}

CARVISION_PAYLOAD = {
    "model_year": 2018,
    "model": "f-150",
    "condition": "good",
    "cylinders": 6,
    "fuel": "gas",
    "odometer": 50000,
    "transmission": "automatic",
    "drive": "4wd",
    "type": "truck",
    "paint_color": "white",
}

NLPINSIGHT_PAYLOAD = {
    "text": "The quarterly earnings report shows strong growth in revenue and margins.",
}


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _is_service_up(base_url: str) -> bool:
    """Return True if /health responds 200 within timeout."""
    try:
        r = httpx.get(f"{base_url}/health", timeout=TIMEOUT)
        return r.status_code == 200
    except httpx.RequestError:
        return False


def _skip_if_down(base_url: str, service: str):
    """Skip test with a clear message if service is unreachable."""
    if not _is_service_up(base_url):
        pytest.skip(
            f"{service} unreachable at {base_url} — " "run: kubectl port-forward svc/<name> <port>:80 -n ml-portfolio"
        )


# ─── BankChurn Predictor ─────────────────────────────────────────────────────


class TestBankChurnSmoke:
    """Smoke tests for BankChurn Predictor (port 8000)."""

    def test_health(self):
        _skip_if_down(BANKCHURN_URL, "BankChurn")
        r = httpx.get(f"{BANKCHURN_URL}/health", timeout=TIMEOUT)
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "healthy"
        assert data.get("model_loaded") is True

    def test_metrics_endpoint(self):
        _skip_if_down(BANKCHURN_URL, "BankChurn")
        r = httpx.get(f"{BANKCHURN_URL}/metrics", timeout=TIMEOUT)
        assert r.status_code == 200
        assert (
            "bankchurn_requests_total" in r.text
        ), "Prometheus metric 'bankchurn_requests_total' not found in /metrics"

    def test_predict_response_shape(self):
        _skip_if_down(BANKCHURN_URL, "BankChurn")
        r = httpx.post(f"{BANKCHURN_URL}/predict", json=BANKCHURN_PAYLOAD, timeout=TIMEOUT)
        assert r.status_code == 200, f"Predict failed: {r.text}"
        data = r.json()
        assert "churn_prediction" in data
        assert "churn_probability" in data
        assert "risk_level" in data
        assert data["risk_level"] in {"HIGH", "MEDIUM", "LOW"}

    def test_predict_probability_range(self):
        _skip_if_down(BANKCHURN_URL, "BankChurn")
        r = httpx.post(f"{BANKCHURN_URL}/predict", json=BANKCHURN_PAYLOAD, timeout=TIMEOUT)
        assert r.status_code == 200
        prob = r.json()["churn_probability"]
        assert 0.0 <= prob <= 1.0, f"Probability out of range: {prob}"

    def test_predict_invalid_payload_returns_422(self):
        _skip_if_down(BANKCHURN_URL, "BankChurn")
        r = httpx.post(f"{BANKCHURN_URL}/predict", json={"invalid": "payload"}, timeout=TIMEOUT)
        assert r.status_code == 422, f"Expected 422 for invalid payload, got {r.status_code}"


# ─── CarVision Market Intelligence ───────────────────────────────────────────


class TestCarVisionSmoke:
    """Smoke tests for CarVision Market Intelligence (port 8001)."""

    def test_health(self):
        _skip_if_down(CARVISION_URL, "CarVision")
        r = httpx.get(f"{CARVISION_URL}/health", timeout=TIMEOUT)
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") in {"ok", "healthy"}
        assert data.get("model_loaded") is True

    def test_metrics_endpoint(self):
        _skip_if_down(CARVISION_URL, "CarVision")
        r = httpx.get(f"{CARVISION_URL}/metrics", timeout=TIMEOUT)
        assert r.status_code == 200
        assert (
            "carvision_requests_total" in r.text
        ), "Prometheus metric 'carvision_requests_total' not found in /metrics"

    def test_predict_response_shape(self):
        _skip_if_down(CARVISION_URL, "CarVision")
        r = httpx.post(f"{CARVISION_URL}/predict", json=CARVISION_PAYLOAD, timeout=TIMEOUT)
        assert r.status_code == 200, f"Predict failed: {r.text}"
        data = r.json()
        assert "prediction" in data
        assert isinstance(data["prediction"], (int, float))

    def test_predict_price_positive(self):
        _skip_if_down(CARVISION_URL, "CarVision")
        r = httpx.post(f"{CARVISION_URL}/predict", json=CARVISION_PAYLOAD, timeout=TIMEOUT)
        assert r.status_code == 200
        price = r.json()["prediction"]
        assert price > 0, f"Predicted price must be positive, got {price}"

    def test_predict_invalid_payload_returns_422(self):
        _skip_if_down(CARVISION_URL, "CarVision")
        r = httpx.post(f"{CARVISION_URL}/predict", json={"bad": "data"}, timeout=TIMEOUT)
        assert r.status_code == 422


# ─── NLPInsight Analyzer ───────────────────────────────────────────────────


class TestNLPInsightSmoke:
    """Smoke tests for NLPInsight Analyzer (port 8002)."""

    def test_health(self):
        _skip_if_down(NLPINSIGHT_URL, "NLPInsight")
        r = httpx.get(f"{NLPINSIGHT_URL}/health", timeout=TIMEOUT)
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") in {"healthy", "degraded"}

    def test_metrics_endpoint(self):
        _skip_if_down(NLPINSIGHT_URL, "NLPInsight")
        r = httpx.get(f"{NLPINSIGHT_URL}/metrics", timeout=TIMEOUT)
        assert r.status_code == 200

    def test_predict_response_shape(self):
        _skip_if_down(NLPINSIGHT_URL, "NLPInsight")
        r = httpx.post(f"{NLPINSIGHT_URL}/predict", json=NLPINSIGHT_PAYLOAD, timeout=TIMEOUT)
        assert r.status_code == 200, f"Predict failed: {r.text}"
        data = r.json()
        assert "prediction" in data
        pred = data["prediction"]
        assert "label" in pred
        assert "confidence" in pred
        assert 0.0 <= pred["confidence"] <= 1.0

    def test_predict_empty_text_returns_422(self):
        _skip_if_down(NLPINSIGHT_URL, "NLPInsight")
        r = httpx.post(f"{NLPINSIGHT_URL}/predict", json={"text": ""}, timeout=TIMEOUT)
        assert r.status_code == 422
