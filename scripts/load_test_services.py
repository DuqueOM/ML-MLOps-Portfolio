#!/usr/bin/env python3
"""
Production Load Testing & Smoke Testing for ML-MLOps Portfolio.

Professional testing methodology for ML services deployed on Kubernetes:

  Phase 1 — Smoke Tests:  Health + single prediction per service (fast fail)
  Phase 2 — Load Tests:   Sustained traffic with varied payloads (metrics gen)
  Phase 3 — Report:       Latency percentiles, error rates, throughput

Usage:
    # Prerequisite: port-forward all services
    kubectl port-forward svc/bankchurn-service 8000:80 -n ml-portfolio &
    kubectl port-forward svc/carvision-service 8001:80 -n ml-portfolio &
    kubectl port-forward svc/nlpinsight-service   8002:80 -n ml-portfolio &

    # Run all phases
    python scripts/load_test_services.py

    # Smoke test only (quick validation)
    python scripts/load_test_services.py --smoke-only

    # Custom load parameters
    python scripts/load_test_services.py --requests 200 --concurrency 5 --ramp-up 10

    # Single service
    python scripts/load_test_services.py --service bankchurn
"""

import argparse
import json
import random
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# ---------------------------------------------------------------------------
# Service definitions & payload generators
# ---------------------------------------------------------------------------

SERVICES = {
    "bankchurn": {
        "name": "BankChurn-Predictor",
        "base_url": "http://localhost:8000",
        "predict_endpoint": "/predict",
        "health_endpoint": "/health",
        "metrics_endpoint": "/metrics",
    },
    "carvision": {
        "name": "CarVision-Market-Intelligence",
        "base_url": "http://localhost:8001",
        "predict_endpoint": "/predict",
        "health_endpoint": "/health",
        "metrics_endpoint": "/metrics",
    },
    "nlpinsight": {
        "name": "NLPInsight-Analyzer",
        "base_url": "http://localhost:8002",
        "predict_endpoint": "/predict",
        "health_endpoint": "/health",
        "metrics_endpoint": "/metrics",
    },
}


def generate_bankchurn_payload() -> Dict[str, Any]:
    """Generate a realistic, randomized BankChurn customer payload."""
    return {
        "CreditScore": random.randint(350, 850),
        "Geography": random.choice(["France", "Spain", "Germany"]),
        "Gender": random.choice(["Male", "Female"]),
        "Age": random.randint(18, 92),
        "Tenure": random.randint(0, 10),
        "Balance": round(random.uniform(0, 250000), 2),
        "NumOfProducts": random.randint(1, 4),
        "HasCrCard": random.randint(0, 1),
        "IsActiveMember": random.randint(0, 1),
        "EstimatedSalary": round(random.uniform(10000, 200000), 2),
    }


def generate_carvision_payload() -> Dict[str, Any]:
    """Generate a realistic, randomized CarVision vehicle payload."""
    return {
        "model_year": random.randint(2000, 2024),
        "model": random.choice(
            [
                "civic",
                "camry",
                "corolla",
                "f-150",
                "silverado",
                "accord",
                "altima",
                "mustang",
                "wrangler",
                "rav4",
            ]
        ),
        "condition": random.choice(["new", "like new", "excellent", "good", "fair"]),
        "cylinders": random.choice([4, 6, 8]),
        "fuel": random.choice(["gas", "diesel", "electric", "hybrid"]),
        "odometer": random.randint(0, 300000),
        "transmission": random.choice(["automatic", "manual"]),
        "drive": random.choice(["fwd", "rwd", "4wd"]),
        "type": random.choice(["sedan", "SUV", "truck", "coupe", "hatchback"]),
        "paint_color": random.choice(["white", "black", "silver", "red", "blue", "grey"]),
    }


def generate_nlpinsight_payload() -> Dict[str, Any]:
    """Generate a realistic, randomized NLPInsight sentiment analysis payload."""
    texts = [
        "Revenue growth exceeded expectations this quarter",
        "The company reported significant losses due to market downturn",
        "Shares remained stable with no major changes in outlook",
        "Strong earnings drove stock prices to new highs",
        "The acquisition is expected to boost market share significantly",
        "Declining sales led to workforce reduction announcements",
        "The board approved a new dividend payout for shareholders",
        "Market uncertainty continues to weigh on investor confidence",
        "Operating margins improved thanks to cost reduction initiatives",
        "The company faces regulatory challenges in key markets",
    ]
    return {
        "text": random.choice(texts),
    }


PAYLOAD_GENERATORS = {
    "bankchurn": generate_bankchurn_payload,
    "carvision": generate_carvision_payload,
    "nlpinsight": generate_nlpinsight_payload,
}

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def http_get(url: str, timeout: float = 10.0) -> Dict[str, Any]:
    """GET request returning parsed JSON."""
    req = Request(url, method="GET")
    req.add_header("Accept", "application/json")
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def http_post(url: str, payload: Dict[str, Any], timeout: float = 15.0) -> Dict[str, Any]:
    """POST request returning parsed JSON."""
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


# ---------------------------------------------------------------------------
# Result tracking
# ---------------------------------------------------------------------------


@dataclass
class RequestResult:
    service: str
    status: int
    latency_ms: float
    success: bool
    error: Optional[str] = None


@dataclass
class ServiceReport:
    service: str
    total_requests: int = 0
    successes: int = 0
    failures: int = 0
    latencies_ms: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def error_rate(self) -> float:
        return (self.failures / self.total_requests * 100) if self.total_requests else 0

    @property
    def p50(self) -> float:
        return self._percentile(50)

    @property
    def p95(self) -> float:
        return self._percentile(95)

    @property
    def p99(self) -> float:
        return self._percentile(99)

    @property
    def avg(self) -> float:
        return statistics.mean(self.latencies_ms) if self.latencies_ms else 0

    @property
    def throughput(self) -> float:
        total_sec = sum(self.latencies_ms) / 1000
        return self.total_requests / total_sec if total_sec > 0 else 0

    def _percentile(self, pct: int) -> float:
        if not self.latencies_ms:
            return 0
        sorted_lat = sorted(self.latencies_ms)
        idx = int(len(sorted_lat) * pct / 100)
        idx = min(idx, len(sorted_lat) - 1)
        return sorted_lat[idx]


# ---------------------------------------------------------------------------
# Phase 1: Smoke Tests
# ---------------------------------------------------------------------------


def run_smoke_tests(services: Dict[str, dict]) -> bool:
    """Quick validation: health check + single prediction per service."""
    print("\n" + "=" * 70)
    print("  PHASE 1 — SMOKE TESTS  (health + single prediction)")
    print("=" * 70)

    all_ok = True
    for key, svc in services.items():
        name = svc["name"]
        base = svc["base_url"]

        # Health check
        print(f"\n  [{name}]")
        try:
            resp = http_get(f"{base}{svc['health_endpoint']}")
            model_loaded = resp.get("model_loaded", False)
            status = resp.get("status", "unknown")
            icon = "✅" if model_loaded else "⚠️"
            print(f"    Health:     {icon}  status={status}, model_loaded={model_loaded}")
            if not model_loaded:
                print("    ⚠️  Model not loaded — predictions will fail")
                all_ok = False
                continue
        except Exception as e:
            print(f"    Health:     ❌  UNREACHABLE — {e}")
            all_ok = False
            continue

        # Single prediction
        try:
            payload = PAYLOAD_GENERATORS[key]()
            t0 = time.perf_counter()
            resp = http_post(f"{base}{svc['predict_endpoint']}", payload)
            latency = (time.perf_counter() - t0) * 1000
            print(f"    Predict:    ✅  {latency:.0f}ms — response keys: {list(resp.keys())}")
        except HTTPError as e:
            body = e.read().decode() if hasattr(e, "read") else str(e)
            print(f"    Predict:    ❌  HTTP {e.code} — {body[:200]}")
            all_ok = False
        except Exception as e:
            print(f"    Predict:    ❌  {e}")
            all_ok = False

        # Metrics endpoint
        try:
            req = Request(f"{base}{svc['metrics_endpoint']}", method="GET")
            with urlopen(req, timeout=5) as resp:
                content = resp.read().decode()
            has_prom = "# HELP" in content or "# TYPE" in content
            print(f"    Metrics:    {'✅' if has_prom else '⚠️'}  Prometheus format={has_prom}")
        except Exception as e:
            print(f"    Metrics:    ⚠️  {e}")

    print()
    if all_ok:
        print("  ✅ All smoke tests PASSED")
    else:
        print("  ⚠️  Some smoke tests had issues (see above)")
    return all_ok


# ---------------------------------------------------------------------------
# Phase 2: Load Tests
# ---------------------------------------------------------------------------


def send_single_request(service_key: str, svc: dict) -> RequestResult:
    """Send one prediction request and return the result."""
    payload = PAYLOAD_GENERATORS[service_key]()
    url = f"{svc['base_url']}{svc['predict_endpoint']}"
    t0 = time.perf_counter()
    try:
        http_post(url, payload)
        latency = (time.perf_counter() - t0) * 1000
        return RequestResult(service=service_key, status=200, latency_ms=latency, success=True)
    except HTTPError as e:
        latency = (time.perf_counter() - t0) * 1000
        return RequestResult(
            service=service_key,
            status=e.code,
            latency_ms=latency,
            success=False,
            error=f"HTTP {e.code}",
        )
    except Exception as e:
        latency = (time.perf_counter() - t0) * 1000
        return RequestResult(
            service=service_key,
            status=0,
            latency_ms=latency,
            success=False,
            error=str(e)[:100],
        )


def run_load_tests(
    services: Dict[str, dict],
    total_requests: int = 100,
    concurrency: int = 3,
    ramp_up_seconds: float = 5.0,
) -> Dict[str, ServiceReport]:
    """Sustained load test with concurrent requests across all services."""
    print("\n" + "=" * 70)
    print(f"  PHASE 2 — LOAD TESTS  ({total_requests} req × {len(services)} services, " f"concurrency={concurrency})")
    print("=" * 70)

    reports: Dict[str, ServiceReport] = {key: ServiceReport(service=svc["name"]) for key, svc in services.items()}

    # Build work items: distribute requests evenly across services
    work: List[tuple] = []
    for key, svc in services.items():
        for _ in range(total_requests):
            work.append((key, svc))
    random.shuffle(work)

    total_work = len(work)
    completed = 0
    start_all = time.perf_counter()

    # Ramp-up: gradually increase request rate
    delay_per_req = ramp_up_seconds / min(total_work, 20)  # ramp over first 20 reqs

    print(f"\n  Sending {total_work} total requests (ramp-up: {ramp_up_seconds:.0f}s)...\n")

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {}
        for i, (key, svc) in enumerate(work):
            f = pool.submit(send_single_request, key, svc)
            futures[f] = key
            # Ramp-up delay for first N requests
            if i < 20:
                time.sleep(delay_per_req)

        for future in as_completed(futures):
            result = future.result()
            report = reports[result.service]
            report.total_requests += 1
            if result.success:
                report.successes += 1
            else:
                report.failures += 1
                if result.error:
                    report.errors.append(result.error)
            report.latencies_ms.append(result.latency_ms)

            completed += 1
            if completed % 25 == 0 or completed == total_work:
                elapsed = time.perf_counter() - start_all
                rps = completed / elapsed if elapsed > 0 else 0
                print(f"    Progress: {completed}/{total_work} " f"({completed/total_work*100:.0f}%) — {rps:.1f} req/s")

    elapsed_total = time.perf_counter() - start_all
    print(f"\n  Completed in {elapsed_total:.1f}s " f"({total_work/elapsed_total:.1f} req/s overall)")

    return reports


# ---------------------------------------------------------------------------
# Phase 3: Report
# ---------------------------------------------------------------------------


def print_report(reports: Dict[str, ServiceReport]) -> None:
    """Print a professional summary with latency percentiles and error rates."""
    print("\n" + "=" * 70)
    print("  PHASE 3 — RESULTS REPORT")
    print("=" * 70)

    header = f"  {'Service':<32} {'Reqs':>5} {'OK':>5} {'Err%':>6} " f"{'Avg':>7} {'P50':>7} {'P95':>7} {'P99':>7}"
    print(f"\n{header}")
    print("  " + "-" * 86)

    for key, r in reports.items():
        err_pct = f"{r.error_rate:.1f}%"
        avg = f"{r.avg:.0f}ms"
        p50 = f"{r.p50:.0f}ms"
        p95 = f"{r.p95:.0f}ms"
        p99 = f"{r.p99:.0f}ms"
        print(
            f"  {r.service:<32} {r.total_requests:>5} {r.successes:>5} "
            f"{err_pct:>6} {avg:>7} {p50:>7} {p95:>7} {p99:>7}"
        )

    print()

    # SLA check (professional standards)
    print("  SLA Compliance:")
    for key, r in reports.items():
        issues = []
        if r.error_rate > 1.0:
            issues.append(f"error rate {r.error_rate:.1f}% > 1%")
        if r.p95 > 500:
            issues.append(f"P95 latency {r.p95:.0f}ms > 500ms")
        if r.p99 > 1000:
            issues.append(f"P99 latency {r.p99:.0f}ms > 1000ms")

        if issues:
            print(f"    ⚠️  {r.service}: {', '.join(issues)}")
        else:
            print(f"    ✅  {r.service}: All SLAs met (err<1%, P95<500ms, P99<1s)")

    # Unique errors
    all_errors = []
    for r in reports.values():
        all_errors.extend(r.errors)
    if all_errors:
        unique = set(all_errors)
        print(f"\n  Unique errors ({len(unique)}):")
        for err in list(unique)[:10]:
            print(f"    - {err}")

    print()


def print_prometheus_check(services: Dict[str, dict]) -> None:
    """Show Prometheus metrics to verify they were populated."""
    print("=" * 70)
    print("  PROMETHEUS METRICS CHECK")
    print("=" * 70)

    for key, svc in services.items():
        print(f"\n  [{svc['name']}]")
        try:
            req = Request(f"{svc['base_url']}{svc['metrics_endpoint']}", method="GET")
            with urlopen(req, timeout=5) as resp:
                content = resp.read().decode()

            # Extract key counter/histogram values
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("#"):
                    continue
                # Show relevant metrics (total counters, not individual buckets)
                if (
                    any(
                        kw in line
                        for kw in [
                            "_total",
                            "_count",
                            "_sum",
                        ]
                    )
                    and "bucket" not in line
                    and line
                ):
                    print(f"    {line}")
        except Exception as e:
            print(f"    ⚠️  Could not fetch metrics: {e}")

    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Professional load testing for ML-MLOps Portfolio services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/load_test_services.py                          # Full run (100 req/service)
  python scripts/load_test_services.py --smoke-only             # Quick validation
  python scripts/load_test_services.py --requests 500 -c 10     # Heavy load test
  python scripts/load_test_services.py --service bankchurn      # Single service
  python scripts/load_test_services.py --requests 50 --ramp-up 3  # Quick metrics gen
        """,
    )
    parser.add_argument("--smoke-only", action="store_true", help="Run only smoke tests (health + single prediction)")
    parser.add_argument("--requests", "-n", type=int, default=100, help="Number of requests PER SERVICE (default: 100)")
    parser.add_argument("--concurrency", "-c", type=int, default=3, help="Max concurrent requests (default: 3)")
    parser.add_argument("--ramp-up", type=float, default=5.0, help="Ramp-up period in seconds (default: 5)")
    parser.add_argument("--service", "-s", choices=list(SERVICES.keys()), help="Test only a specific service")
    parser.add_argument("--bankchurn-port", type=int, default=8000)
    parser.add_argument("--carvision-port", type=int, default=8001)
    parser.add_argument("--nlpinsight-port", type=int, default=8002)

    args = parser.parse_args()

    # Apply port overrides
    SERVICES["bankchurn"]["base_url"] = f"http://localhost:{args.bankchurn_port}"
    SERVICES["carvision"]["base_url"] = f"http://localhost:{args.carvision_port}"
    SERVICES["nlpinsight"]["base_url"] = f"http://localhost:{args.nlpinsight_port}"

    # Filter services if single service mode
    services = SERVICES
    if args.service:
        services = {args.service: SERVICES[args.service]}

    print("\n" + "=" * 70)
    print("  ML-MLOps Portfolio — Production Service Testing")
    print(f"  {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("=" * 70)
    print(f"  Services:    {', '.join(s['name'] for s in services.values())}")
    if not args.smoke_only:
        print(f"  Requests:    {args.requests} per service ({args.requests * len(services)} total)")
        print(f"  Concurrency: {args.concurrency}")
        print(f"  Ramp-up:     {args.ramp_up}s")

    # Phase 1
    smoke_ok = run_smoke_tests(services)

    if args.smoke_only:
        print("\n  (--smoke-only mode, skipping load tests)")
        return 0 if smoke_ok else 1

    if not smoke_ok:
        print("\n  ⚠️  Smoke tests had issues. Proceeding with load tests anyway...")

    # Phase 2
    reports = run_load_tests(
        services,
        total_requests=args.requests,
        concurrency=args.concurrency,
        ramp_up_seconds=args.ramp_up,
    )

    # Phase 3
    print_report(reports)
    print_prometheus_check(services)

    # Final verdict
    total_err = sum(r.error_rate for r in reports.values())
    if total_err == 0:
        print("  🎉 All services healthy — Grafana should now show metrics!")
        print("  📸 Open http://localhost:3000 → 'ML Portfolio Metrics' dashboard")
        return 0
    elif total_err < 5:
        print("  ⚠️  Minor issues detected. Grafana metrics should still populate.")
        return 0
    else:
        print("  ❌ Significant errors detected. Check service logs.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
