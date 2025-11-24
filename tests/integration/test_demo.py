import time

import pytest
import requests

# Configuration
BASE_URLS = {
    "bankchurn": "http://localhost:8001",
    "carvision": "http://localhost:8002",
    "telecom": "http://localhost:8003",
    "mlflow": "http://localhost:5000",
}


def wait_for_service(url: str, timeout: int = 30):
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
        assert data.get("status") in ["ok", "healthy"]


def test_bankchurn_prediction():
    url = f"{BASE_URLS['bankchurn']}/predict"
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
    response = requests.post(url, json=payload)
    assert response.status_code == 200, f"BankChurn failed: {response.text}"
    data = response.json()
    assert "churn_prediction" in data
    assert "churn_probability" in data


def test_carvision_prediction():
    url = f"{BASE_URLS['carvision']}/predict"
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
    response = requests.post(url, json=payload)
    assert response.status_code == 200, f"CarVision failed: {response.text}"
    data = response.json()
    assert "prediction" in data
    assert isinstance(data["prediction"], (int, float))


def test_telecom_prediction():
    url = f"{BASE_URLS['telecom']}/predict"
    # Payload matched to TelecomAI's TelecomFeatures
    payload = {"calls": 10.0, "minutes": 300.0, "messages": 5.0, "mb_used": 1500.0}
    response = requests.post(url, json=payload)
    assert response.status_code == 200, f"TelecomAI failed: {response.text}"
    data = response.json()
    assert "prediction" in data
