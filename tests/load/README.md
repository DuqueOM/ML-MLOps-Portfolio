# Load Testing Suite

Performance and load testing for the ML-MLOps Portfolio APIs using [Locust](https://locust.io/).

## Quick Start

```bash
# 1. Install locust
pip install locust

# 2. Start the demo services
docker compose -f docker-compose.demo.yml up -d

# 3. Run load test with web UI
locust -f tests/load/locustfile.py

# 4. Open http://localhost:8089 and configure:
#    - Number of users: 50
#    - Spawn rate: 10
#    - Host: http://localhost:8001 (BankChurn)
```

## Headless Mode (CI/CD)

```bash
# Run 50 users for 60 seconds, output CSV reports
locust -f tests/load/locustfile.py \
    --host http://localhost:8001 \
    --headless \
    -u 50 \
    -r 10 \
    -t 60s \
    --csv=reports/load_test
```

## Test Scenarios

| Service | Port | Endpoint | In-Pod Latency (GKE) | Via-Ingress Latency |
|---------|------|----------|---------------------|--------------------|
| BankChurn | 8001 | POST /predict | 103ms p50 / 111ms p95 | 770ms p50 / 1700ms p95 |
| NLPInsight | 8003 | POST /predict | 5ms p50 / 15ms p95 | 80ms p50 / 160ms p95 |
| ChicagoTaxi | 8004 | GET /demand | 75ms p50 / 460ms p95 | 90ms p50 / 170ms p95 |

## Production Baseline (2026-03-11)

Run: `INGRESS_HOST=http://136.111.152.72 locust -f tests/load/locustfile.py --headless -u 30 -r 5 -t 120s`

| Metric | Value |
|--------|-------|
| Total requests | 2,673 |
| Concurrent users | 30 |
| Ramp rate | 5/s |
| Duration | 120s |
| Aggregate throughput | 22.35 req/s |
| Error rate | **0.07%** (2 transient 502s on BankChurn) |
| BankChurn predict P50/P95/P99 | 770ms / 1700ms / 2100ms |
| NLPInsight predict P50/P95/P99 | 80ms / 160ms / 240ms |
| NLPInsight predict_batch P50/P95 | 84ms / 150ms |
| ChicagoTaxi demand P50/P95/P99 | 90ms / 170ms / 230ms |
| ChicagoTaxi areas P50/P95 | 110ms / 230ms |

## Performance Targets

| Metric | Target | Critical | Observed (prod) |
|--------|--------|----------|-----------------|
| p95 Latency | < 500ms | < 2000ms | NLP 160ms ✅ / Taxi 170ms ✅ / BankChurn 1700ms ⚠️ |
| p99 Latency | < 1000ms | < 3000ms | NLP 240ms ✅ / Taxi 230ms ✅ / BankChurn 2100ms ✅ |
| Error Rate | < 0.1% | < 1% | **0.07%** ✅ |
| Aggregate RPS | > 10 | > 5 | **22.35 req/s** ✅ |

> BankChurn ingress P95=1700ms includes NGINX routing overhead + StackingClassifier inference. In-pod is 111ms P95.

## Reports

After running tests, CSV reports are saved to `reports/`:
- `load_test_stats.csv` - Aggregate statistics
- `load_test_stats_history.csv` - Time series data
- `load_test_failures.csv` - Failure details

## Integration with CI

The load tests can be integrated into CI/CD as a quality gate:

```yaml
# In .github/workflows/ci-mlops.yml
- name: Run Load Tests
  run: |
    pip install locust
    locust -f tests/load/locustfile.py \
        --host http://localhost:8001 \
        --headless -u 20 -r 5 -t 30s \
        --csv=reports/load_test \
        --exit-code-on-error 1
```

## Scaling Recommendations

Based on load test results:

| RPS Observed | Recommended Replicas | Notes |
|--------------|---------------------|-------|
| < 100 | 1 | Development |
| 100-500 | 2-3 | Staging |
| 500-1000 | 3-5 | Production |
| > 1000 | 5+ with HPA | Auto-scaling |
