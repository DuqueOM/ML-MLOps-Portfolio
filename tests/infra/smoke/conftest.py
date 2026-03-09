"""
Conftest for smoke tests — environment detection and reporting.

Prints a header showing which environment and URLs are being tested
so CI/CD logs and screenshots clearly identify the target environment.
"""

import os

import pytest


def _detect_environment() -> str:
    """Detect target environment from configured URLs."""
    bankchurn_url = os.getenv("BANKCHURN_URL", "http://localhost:8001")
    if "localhost" in bankchurn_url or "127.0.0.1" in bankchurn_url:
        return "local (port-forward)"
    if "staging" in bankchurn_url:
        return "staging"
    if "prod" in bankchurn_url:
        return "production"
    if bankchurn_url.startswith("https://"):
        return "production (TLS)"
    # Any non-localhost HTTP URL is assumed to be a real cluster (Ingress/LB)
    if bankchurn_url.startswith("http://") and "/bankchurn" in bankchurn_url:
        return "GKE Ingress (nginx)"
    return "custom"


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "smoke: mark test as a smoke test (requires running services)",
    )


def pytest_report_header(config):
    """Print environment info in pytest header — visible in CI logs and screenshots."""
    env = _detect_environment()
    bankchurn = os.getenv("BANKCHURN_URL", "http://localhost:8001")
    nlpinsight = os.getenv("NLPINSIGHT_URL", "http://localhost:8003")
    chicagotaxi = os.getenv("CHICAGOTAXI_URL", "http://localhost:8004")
    timeout = os.getenv("SMOKE_TIMEOUT", "10")
    return [
        "─" * 60,
        f"  Smoke Test Environment : {env}",
        f"  bankchurn  → {bankchurn}",
        f"  nlpinsight → {nlpinsight}",
        f"  chicagotaxi→ {chicagotaxi}",
        f"  timeout    : {timeout}s",
        "─" * 60,
    ]


@pytest.fixture(scope="session")
def smoke_env() -> dict:
    """Session-scoped fixture exposing environment metadata to tests."""
    return {
        "environment": _detect_environment(),
        "bankchurn_url": os.getenv("BANKCHURN_URL", "http://localhost:8001"),
        "nlpinsight_url": os.getenv("NLPINSIGHT_URL", "http://localhost:8003"),
        "chicagotaxi_url": os.getenv("CHICAGOTAXI_URL", "http://localhost:8004"),
    }
