import time

import pytest
import requests

# Configuration
BASE_URLS = {
    "bankchurn": "http://localhost:8001",
    "carvision": "http://localhost:8002",
    "nlpinsight": "http://localhost:8003",
    "chicagotaxi": "http://localhost:8004",
    "mlflow": "http://localhost:5000",
}


def wait_for_service(url: str, timeout: int = 120):
    """Wait for service to become healthy."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False


def _model_loaded(url: str) -> bool:
    """Return True if the service reports model_loaded=true."""
    try:
        resp = requests.get(f"{url}/health", timeout=5)
        data = resp.json()
        return data.get("model_loaded", False) is True
    except Exception:
        return False


@pytest.mark.parametrize("service,url", BASE_URLS.items())
def test_service_health(service, url):
    """Verify service health check endpoint."""
    if service == "mlflow":
        # MLflow standard health check might differ, usually /health
        pass

    assert wait_for_service(url), f"Service {service} at {url} is not healthy"
    response = requests.get(f"{url}/health")
    assert response.status_code == 200
    # MLflow returns text usually, others return JSON
    if service != "mlflow":
        data = response.json()
        assert data.get("status") in ["ok", "healthy", "degraded"]


def test_bankchurn_prediction():
    url = BASE_URLS["bankchurn"]
    if not _model_loaded(url):
        pytest.skip("BankChurn model not loaded (models downloaded at runtime via Init Container)")
    payload = {
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
    response = requests.post(f"{url}/predict", json=payload)
    assert response.status_code == 200, f"BankChurn failed: {response.text}"
    data = response.json()
    assert "churn_prediction" in data
    assert "churn_probability" in data


def test_carvision_prediction():
    url = BASE_URLS["carvision"]
    if not _model_loaded(url):
        pytest.skip("CarVision model not loaded (models downloaded at runtime via Init Container)")
    # Payload matched to CarVision's VehicleFeatures
    payload = {
        "model_year": 2015,
        "model": "ford f-150",
        "condition": "good",
        "cylinders": 6.0,
        "fuel": "gas",
        "odometer": 50000.0,
        "transmission": "automatic",
        "drive": "4wd",
        "type": "truck",
        "paint_color": "white",
    }
    response = requests.post(f"{url}/predict", json=payload)
    assert response.status_code == 200, f"CarVision failed: {response.text}"
    data = response.json()
    assert "predicted_price" in data
    assert isinstance(data["predicted_price"], (int, float))


def test_nlpinsight_prediction():
    url = BASE_URLS["nlpinsight"]
    if not _model_loaded(url):
        pytest.skip("NLPInsight model not loaded (models downloaded at runtime via Init Container)")
    payload = {"text": "Revenue growth exceeded expectations this quarter."}
    response = requests.post(f"{url}/predict", json=payload)
    assert response.status_code == 200, f"NLPInsight failed: {response.text}"
    data = response.json()
    assert "prediction" in data
    assert data["prediction"]["label"] in ["negative", "neutral", "positive"]
    assert "confidence" in data["prediction"]


def test_chicagotaxi_demand():
    url = BASE_URLS["chicagotaxi"]
    try:
        health = requests.get(f"{url}/health", timeout=5)
        if health.status_code != 200:
            pytest.skip("ChicagoTaxi not reachable")
        if not health.json().get("predictions_loaded", False):
            pytest.skip("ChicagoTaxi predictions not loaded")
    except requests.exceptions.RequestException:
        pytest.skip("ChicagoTaxi not reachable")

    response = requests.get(f"{url}/demand?area=8&hour=14&limit=5")
    assert response.status_code == 200, f"ChicagoTaxi failed: {response.text}"
    data = response.json()
    assert isinstance(data, list)

    # Test areas endpoint
    response = requests.get(f"{url}/areas")
    assert response.status_code == 200
    areas = response.json()
    assert isinstance(areas, list)
    if len(areas) > 0:
        assert "area_id" in areas[0]
        assert "avg_demand" in areas[0]
