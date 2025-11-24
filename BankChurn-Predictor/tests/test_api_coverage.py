from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.fastapi_app import app

client = TestClient(app)


@pytest.fixture
def mock_predictor():
    with patch("app.fastapi_app.predictor") as mock:
        yield mock


@pytest.fixture
def mock_load_logic():
    with patch("app.fastapi_app.load_model_logic") as mock:
        yield mock


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "BankChurn Predictor API" in response.json()["message"]


def test_health_healthy(mock_predictor):
    # Mock predictor as not None
    mock_predictor.return_value = MagicMock()
    # We need to ensure the global variable in app.fastapi_app is set
    # Since we are patching, the fixture handles the mock object replacing the variable

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_degraded():
    # Force predictor to None
    with patch("app.fastapi_app.predictor", None):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "degraded"


def test_predict_endpoint(mock_predictor):
    # Setup mock
    mock_df = pd.DataFrame({"prediction": [1], "probability": [0.8], "risk_level": ["HIGH"]})
    mock_predictor.predict.return_value = mock_df

    payload = {
        "CreditScore": 600,
        "Geography": "France",
        "Gender": "Male",
        "Age": 40,
        "Tenure": 3,
        "Balance": 60000.0,
        "NumOfProducts": 2,
        "HasCrCard": 1,
        "IsActiveMember": 1,
        "EstimatedSalary": 50000.0,
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["churn_prediction"] == 1
    assert data["churn_probability"] == 0.8
    assert data["risk_level"] == "HIGH"


def test_predict_batch_endpoint(mock_predictor):
    # Setup mock
    mock_df = pd.DataFrame({"prediction": [0, 1], "probability": [0.1, 0.9], "risk_level": ["LOW", "HIGH"]})
    mock_predictor.predict.return_value = mock_df

    customer = {
        "CreditScore": 600,
        "Geography": "Spain",
        "Gender": "Female",
        "Age": 30,
        "Tenure": 2,
        "Balance": 0.0,
        "NumOfProducts": 1,
        "HasCrCard": 1,
        "IsActiveMember": 0,
        "EstimatedSalary": 30000.0,
    }

    payload = {"customers": [customer, customer]}

    response = client.post("/predict_batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["predictions"]) == 2
    assert data["total_customers"] == 2


def test_predict_model_not_loaded():
    with patch("app.fastapi_app.predictor", None):
        customer = {
            "CreditScore": 600,
            "Geography": "France",
            "Gender": "Male",
            "Age": 40,
            "Tenure": 3,
            "Balance": 60000.0,
            "NumOfProducts": 2,
            "HasCrCard": 1,
            "IsActiveMember": 1,
            "EstimatedSalary": 50000.0,
        }
        response = client.post("/predict", json=customer)
        assert response.status_code == 503
