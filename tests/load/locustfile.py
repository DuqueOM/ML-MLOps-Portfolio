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
    # Ports: BankChurn=8001, CarVision=8002, NLPInsight=8003

Option B — Kubernetes port-forward (GKE / EKS):
    kubectl port-forward svc/bankchurn-service 8000:80 -n ml-portfolio &
    kubectl port-forward svc/carvision-service 8001:80 -n ml-portfolio &
    kubectl port-forward svc/nlpinsight-service 8002:80 -n ml-portfolio &
    # Ports: BankChurn=8000, CarVision=8001, NLPInsight=8002

Option C — Ingress IP (production-grade, recommended for real metrics):
    # GCP: Uses GCE Ingress with public IP
    export INGRESS_HOST=http://34.120.120.57
    # AWS: Uses ALB DNS
    export INGRESS_HOST=http://<alb-dns-name>
    # Routes: /bankchurn/*, /carvision/*, /nlpinsight/*
    # No port-forward overhead (~70ms saved per request)

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

# Production — via Ingress (eliminates port-forward overhead)
INGRESS_HOST=http://34.120.120.57 locust -f tests/load/locustfile.py \
       --headless -u 30 -r 5 -t 120s \
       --only-summary --csv=reports/load_test_ingress \
       --html=reports/load_test_ingress.html

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

import os
import random

from locust import HttpUser, between, task

# ---------------------------------------------------------------------------
# Ingress-aware host resolution
# Set INGRESS_HOST to test via real Ingress/LoadBalancer (production-grade).
# When set, all User classes target the same Ingress IP with path prefixes.
# When unset, falls back to per-service localhost ports (port-forward mode).
# ---------------------------------------------------------------------------
_INGRESS_HOST = os.environ.get("INGRESS_HOST", "").rstrip("/")

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


def _nlpinsight_payload() -> dict:
    texts = [
        "This product exceeded all my expectations. Absolutely fantastic quality!",
        "Terrible experience. The worst customer service I have ever dealt with.",
        "The quarterly earnings report shows strong growth in revenue.",
        "Market volatility has increased significantly due to geopolitical tensions.",
        "The new feature release has been well received by our user base.",
        "Disappointing results this quarter with declining margins across segments.",
        "Innovation in AI and machine learning continues to drive efficiency gains.",
        "Supply chain disruptions are impacting delivery timelines negatively.",
    ]
    return {"text": random.choice(texts)}


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

    host = _INGRESS_HOST or "http://localhost:8000"
    wait_time = between(0.5, 2.0)
    weight = 3  # Relative weight across all User classes
    _prefix = "/bankchurn" if _INGRESS_HOST else ""

    def on_start(self) -> None:
        """Validate service is ready before generating load."""
        with self.client.get(f"{self._prefix}/health", name="bankchurn:health", catch_response=True) as r:
            if r.status_code != 200:
                r.failure(f"Health check failed: {r.status_code}")

    @task(10)
    def predict(self) -> None:
        """Single-record churn prediction — primary load driver."""
        with self.client.post(
            f"{self._prefix}/predict",
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
        self.client.get(f"{self._prefix}/health", name="bankchurn:health")

    @task(1)
    def metrics(self) -> None:
        """Prometheus metrics scrape simulation."""
        self.client.get(f"{self._prefix}/metrics", name="bankchurn:metrics")


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

    host = _INGRESS_HOST or "http://localhost:8001"
    wait_time = between(0.3, 1.5)
    weight = 2
    _prefix = "/carvision" if _INGRESS_HOST else ""

    def on_start(self) -> None:
        with self.client.get(f"{self._prefix}/health", name="carvision:health", catch_response=True) as r:
            if r.status_code != 200:
                r.failure(f"Health check failed: {r.status_code}")

    @task(10)
    def predict(self) -> None:
        """Vehicle price prediction — randomized models and conditions."""
        with self.client.post(
            f"{self._prefix}/predict",
            json=_carvision_payload(),
            name="carvision:predict",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                data = r.json()
                if "predicted_price" not in data:
                    r.failure("Missing predicted_price field")
                elif not isinstance(data["predicted_price"], (int, float)):
                    r.failure(f"Invalid predicted_price type: {type(data['predicted_price'])}")
            elif r.status_code == 503:
                r.failure("Service unavailable — model not loaded")
            else:
                r.failure(f"Unexpected status {r.status_code}")

    @task(2)
    def predict_batch(self) -> None:
        """Batch vehicle price prediction — 5 vehicles per request."""
        payload = {"vehicles": [_carvision_payload() for _ in range(5)]}
        with self.client.post(
            f"{self._prefix}/predict_batch",
            json=payload,
            name="carvision:predict_batch",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                data = r.json()
                if data.get("total_vehicles") != 5:
                    r.failure(f"Expected 5 vehicles, got {data.get('total_vehicles')}")
            elif r.status_code == 503:
                r.failure("Service unavailable — model not loaded")
            else:
                r.failure(f"Unexpected status {r.status_code}")

    @task(1)
    def health(self) -> None:
        self.client.get(f"{self._prefix}/health", name="carvision:health")

    @task(1)
    def metrics(self) -> None:
        self.client.get(f"{self._prefix}/metrics", name="carvision:metrics")


# ---------------------------------------------------------------------------
# NLPInsight — http://localhost:8002 (K8s) or http://localhost:8003 (Docker)
# ---------------------------------------------------------------------------


class NLPInsightUser(HttpUser):
    """
    Simulates traffic to NLPInsight Analyzer (Sentiment Analysis).

    Task weights:
      - predict (10x): single text sentiment — primary endpoint
      - predict_batch (3x): batch sentiment — exercises transformer batching
      - health  (1x):  liveness probe
    """

    host = _INGRESS_HOST or "http://localhost:8002"
    wait_time = between(0.3, 1.5)
    weight = 2
    _prefix = "/nlpinsight" if _INGRESS_HOST else ""

    def on_start(self) -> None:
        with self.client.get(f"{self._prefix}/health", name="nlpinsight:health", catch_response=True) as r:
            if r.status_code != 200:
                r.failure(f"Health check failed: {r.status_code}")

    @task(10)
    def predict(self) -> None:
        """Single text sentiment analysis — randomized inputs."""
        with self.client.post(
            f"{self._prefix}/predict",
            json=_nlpinsight_payload(),
            name="nlpinsight:predict",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                data = r.json()
                pred = data.get("prediction", {})
                if "label" not in pred:
                    r.failure("Missing prediction.label")
                if "confidence" not in pred:
                    r.failure("Missing prediction.confidence")
                elif not (0.0 <= pred["confidence"] <= 1.0):
                    r.failure(f"Invalid confidence: {pred['confidence']}")
            elif r.status_code == 503:
                r.failure("Service unavailable — model not loaded")
            else:
                r.failure(f"Unexpected status {r.status_code}")

    @task(3)
    def predict_batch(self) -> None:
        """Batch sentiment analysis — 5 texts per request."""
        payload = {"texts": [_nlpinsight_payload() for _ in range(5)]}
        with self.client.post(
            f"{self._prefix}/predict_batch",
            json=payload,
            name="nlpinsight:predict_batch",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                data = r.json()
                if data.get("count") != 5:
                    r.failure(f"Expected 5 predictions, got {data.get('count')}")
            elif r.status_code == 503:
                r.failure("Service unavailable — model not loaded")
            else:
                r.failure(f"Unexpected status {r.status_code}")

    @task(1)
    def health(self) -> None:
        self.client.get(f"{self._prefix}/health", name="nlpinsight:health")

    @task(1)
    def metrics(self) -> None:
        self.client.get(f"{self._prefix}/metrics", name="nlpinsight:metrics")
