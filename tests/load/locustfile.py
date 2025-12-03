"""
Load Testing for ML-MLOps Portfolio APIs

Usage:
    # Start demo services first
    docker-compose -f docker-compose.demo.yml up -d

    # Run load test (web UI)
    locust -f tests/load/locustfile.py --host http://localhost

    # Run headless (CI mode)
    locust -f tests/load/locustfile.py --host http://localhost \
           --headless -u 50 -r 10 -t 60s --csv=reports/load_test

Metrics collected:
    - Response time (min, max, median, p95, p99)
    - Requests per second (RPS)
    - Failure rate
    - Response size
"""

from locust import HttpUser, between, task


class BankChurnUser(HttpUser):
    """Load test user for BankChurn API (port 8001)."""

    wait_time = between(0.5, 2)
    weight = 3  # Higher weight = more frequent

    def on_start(self):
        """Verify service is healthy before starting."""
        self.client.get("/health", name="bankchurn:health")

    @task(5)
    def predict_single(self):
        """Test single prediction endpoint."""
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
        with self.client.post(
            "/predict",
            json=payload,
            name="bankchurn:predict",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "churn_probability" not in data:
                    response.failure("Missing churn_probability in response")
            elif response.status_code == 503:
                response.failure("Model not loaded")

    @task(1)
    def health_check(self):
        """Periodic health checks."""
        self.client.get("/health", name="bankchurn:health")

    @task(1)
    def metrics(self):
        """Check Prometheus metrics endpoint."""
        self.client.get("/metrics", name="bankchurn:metrics")


class CarVisionUser(HttpUser):
    """Load test user for CarVision API (port 8002)."""

    wait_time = between(0.5, 2)
    weight = 2

    def on_start(self):
        self.client.get("/health", name="carvision:health")

    @task(5)
    def predict_price(self):
        """Test vehicle price prediction."""
        payload = {
            "model_year": 2018,
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
        with self.client.post(
            "/predict",
            json=payload,
            name="carvision:predict",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "prediction" not in data:
                    response.failure("Missing prediction in response")
            elif response.status_code == 503:
                response.failure("Model not loaded")

    @task(1)
    def health_check(self):
        self.client.get("/health", name="carvision:health")


class TelecomUser(HttpUser):
    """Load test user for TelecomAI API (port 8003)."""

    wait_time = between(0.5, 2)
    weight = 2

    def on_start(self):
        self.client.get("/health", name="telecom:health")

    @task(5)
    def predict_plan(self):
        """Test plan recommendation prediction."""
        payload = {
            "calls": 40.0,
            "minutes": 311.9,
            "messages": 83.0,
            "mb_used": 19915.42,
        }
        with self.client.post(
            "/predict",
            json=payload,
            name="telecom:predict",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "prediction" not in data:
                    response.failure("Missing prediction in response")
            elif response.status_code == 503:
                response.failure("Model not loaded")

    @task(1)
    def health_check(self):
        self.client.get("/health", name="telecom:health")


# Multi-service configuration
class BankChurnLoadUser(BankChurnUser):
    """BankChurn user configured for port 8001."""

    host = "http://localhost:8001"


class CarVisionLoadUser(CarVisionUser):
    """CarVision user configured for port 8002."""

    host = "http://localhost:8002"


class TelecomLoadUser(TelecomUser):
    """TelecomAI user configured for port 8003."""

    host = "http://localhost:8003"
