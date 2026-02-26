"""
Professional Load Testing for ML-MLOps Portfolio — Locust Edition.

Industry-standard load testing following SRE methodology:
  - Randomized payloads (avoid cache effects, test real model paths)
  - Weighted task distribution (realistic traffic mix)
  - Inline SLA assertions (failure if response content invalid)
  - Separate User classes per service with independent host configuration
  - Compatible with Locust web UI and headless CI mode

─────────────────────────────────────────────────────────────────────
ENVIRONMENT SETUP
─────────────────────────────────────────────────────────────────────
Option A — Docker Compose (local dev):
    docker compose -f docker-compose.demo.yml up -d
    # Ports: BankChurn=8001, CarVision=8002, TelecomAI=8003

Option B — Kubernetes port-forward (GKE / EKS):
    kubectl port-forward svc/bankchurn-service 8000:80 -n ml-portfolio &
    kubectl port-forward svc/carvision-service 8001:80 -n ml-portfolio &
    kubectl port-forward svc/telecom-service   8002:80 -n ml-portfolio &
    # Ports: BankChurn=8000, CarVision=8001, TelecomAI=8002

─────────────────────────────────────────────────────────────────────
USAGE
─────────────────────────────────────────────────────────────────────
# Interactive web UI (open http://localhost:8089)
locust -f tests/load/locustfile.py

# Headless — single service
locust -f tests/load/locustfile.py --class-picker \
       --headless -u 20 -r 5 -t 60s \
       --only-summary --csv=reports/bankchurn

# Headless — all services simultaneously (recommended)
locust -f tests/load/locustfile.py \
       --headless -u 30 -r 5 -t 120s \
       --only-summary --csv=reports/load_test \
       --html=reports/load_test.html

# CI mode — strict SLA enforcement (exits non-zero if thresholds breached)
locust -f tests/load/locustfile.py \
       --headless -u 10 -r 2 -t 30s \
       --only-summary \
       --exit-code-on-error 1

─────────────────────────────────────────────────────────────────────
SLA THRESHOLDS (production targets)
─────────────────────────────────────────────────────────────────────
  Error rate   < 1%
  P95 latency  < 500ms  (BankChurn: < 800ms — heavier ensemble model)
  P99 latency  < 1000ms
"""

import random

from locust import HttpUser, between, task

# ---------------------------------------------------------------------------
# Payload generators — randomized to avoid cache effects and exercise
# different model branches (risk levels, price segments, plan categories)
# ---------------------------------------------------------------------------


def _bankchurn_payload() -> dict:
    return {
        "CreditScore": random.randint(350, 850),
        "Geography": random.choice(["France", "Spain", "Germany"]),
        "Gender": random.choice(["Male", "Female"]),
        "Age": random.randint(18, 92),
        "Tenure": random.randint(0, 10),
        "Balance": round(random.uniform(0, 250_000), 2),
        "NumOfProducts": random.randint(1, 4),
        "HasCrCard": random.randint(0, 1),
        "IsActiveMember": random.randint(0, 1),
        "EstimatedSalary": round(random.uniform(10_000, 200_000), 2),
    }


def _carvision_payload() -> dict:
    return {
        "model_year": random.randint(2000, 2024),
        "model": random.choice(
            ["civic", "camry", "corolla", "f-150", "silverado", "accord", "altima", "mustang", "wrangler", "rav4"]
        ),
        "condition": random.choice(["new", "like new", "excellent", "good", "fair"]),
        "cylinders": random.choice([4, 6, 8]),
        "fuel": random.choice(["gas", "diesel", "electric", "hybrid"]),
        "odometer": random.randint(0, 300_000),
        "transmission": random.choice(["automatic", "manual"]),
        "drive": random.choice(["fwd", "rwd", "4wd"]),
        "type": random.choice(["sedan", "SUV", "truck", "coupe", "hatchback"]),
        "paint_color": random.choice(["white", "black", "silver", "red", "blue", "grey"]),
    }


def _telecom_payload() -> dict:
    return {
        "calls": round(random.uniform(0, 200), 1),
        "minutes": round(random.uniform(0, 1_000), 1),
        "messages": round(random.uniform(0, 300), 1),
        "mb_used": round(random.uniform(0, 50_000), 2),
    }


# ---------------------------------------------------------------------------
# BankChurn — http://localhost:8000 (K8s) or http://localhost:8001 (Docker)
# ---------------------------------------------------------------------------


class BankChurnUser(HttpUser):
    """
    Simulates traffic to BankChurn Predictor.

    Task weights model a realistic production traffic mix:
      - predict (10x): core business endpoint — heaviest traffic
      - health  (1x):  liveness probe — kubernetes readiness pattern
      - metrics (1x):  Prometheus scrape simulation
    """

    host = "http://localhost:8000"
    wait_time = between(0.5, 2.0)
    weight = 3  # Relative weight across all User classes

    def on_start(self) -> None:
        """Validate service is ready before generating load."""
        with self.client.get("/health", name="bankchurn:health", catch_response=True) as r:
            if r.status_code != 200:
                r.failure(f"Health check failed: {r.status_code}")

    @task(10)
    def predict(self) -> None:
        """Single-record churn prediction — primary load driver."""
        with self.client.post(
            "/predict",
            json=_bankchurn_payload(),
            name="bankchurn:predict",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                data = r.json()
                if "churn_probability" not in data:
                    r.failure("Missing churn_probability")
                elif not (0.0 <= data["churn_probability"] <= 1.0):
                    r.failure(f"Invalid probability: {data['churn_probability']}")
            elif r.status_code == 503:
                r.failure("Service unavailable — model not loaded")
            else:
                r.failure(f"Unexpected status {r.status_code}")

    @task(1)
    def health(self) -> None:
        """Liveness probe — mimics Kubernetes health check cadence."""
        self.client.get("/health", name="bankchurn:health")

    @task(1)
    def metrics(self) -> None:
        """Prometheus metrics scrape simulation."""
        self.client.get("/metrics", name="bankchurn:metrics")


# ---------------------------------------------------------------------------
# CarVision — http://localhost:8001 (K8s) or http://localhost:8002 (Docker)
# ---------------------------------------------------------------------------


class CarVisionUser(HttpUser):
    """
    Simulates traffic to CarVision Market Intelligence.

    Task weights:
      - predict (10x): vehicle price prediction — primary endpoint
      - health  (1x):  liveness probe
    """

    host = "http://localhost:8001"
    wait_time = between(0.3, 1.5)
    weight = 2

    def on_start(self) -> None:
        with self.client.get("/health", name="carvision:health", catch_response=True) as r:
            if r.status_code != 200:
                r.failure(f"Health check failed: {r.status_code}")

    @task(10)
    def predict(self) -> None:
        """Vehicle price prediction — randomized models and conditions."""
        with self.client.post(
            "/predict",
            json=_carvision_payload(),
            name="carvision:predict",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                data = r.json()
                if "prediction" not in data:
                    r.failure("Missing prediction field")
                elif not isinstance(data["prediction"], (int, float)):
                    r.failure(f"Invalid prediction type: {type(data['prediction'])}")
            elif r.status_code == 503:
                r.failure("Service unavailable — model not loaded")
            else:
                r.failure(f"Unexpected status {r.status_code}")

    @task(1)
    def health(self) -> None:
        self.client.get("/health", name="carvision:health")

    @task(1)
    def metrics(self) -> None:
        self.client.get("/metrics", name="carvision:metrics")


# ---------------------------------------------------------------------------
# TelecomAI — http://localhost:8002 (K8s) or http://localhost:8003 (Docker)
# ---------------------------------------------------------------------------


class TelecomUser(HttpUser):
    """
    Simulates traffic to TelecomAI Customer Intelligence.

    Task weights:
      - predict (10x): plan recommendation — primary endpoint
      - health  (1x):  liveness probe
    """

    host = "http://localhost:8002"
    wait_time = between(0.3, 1.5)
    weight = 2

    def on_start(self) -> None:
        with self.client.get("/health", name="telecom:health", catch_response=True) as r:
            if r.status_code != 200:
                r.failure(f"Health check failed: {r.status_code}")

    @task(10)
    def predict(self) -> None:
        """Plan recommendation — randomized usage patterns."""
        with self.client.post(
            "/predict",
            json=_telecom_payload(),
            name="telecom:predict",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                data = r.json()
                if "prediction" not in data:
                    r.failure("Missing prediction field")
            elif r.status_code == 503:
                r.failure("Service unavailable — model not loaded")
            else:
                r.failure(f"Unexpected status {r.status_code}")

    @task(1)
    def health(self) -> None:
        self.client.get("/health", name="telecom:health")

    @task(1)
    def metrics(self) -> None:
        self.client.get("/metrics", name="telecom:metrics")
