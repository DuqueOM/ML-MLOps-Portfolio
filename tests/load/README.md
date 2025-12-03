# Load Testing Suite

Performance and load testing for the ML-MLOps Portfolio APIs using [Locust](https://locust.io/).

## Quick Start

```bash
# 1. Install locust
pip install locust

# 2. Start the demo services
docker-compose -f docker-compose.demo.yml up -d

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

| Service | Port | Endpoint | Expected Latency |
|---------|------|----------|------------------|
| BankChurn | 8001 | POST /predict | < 50ms p95 |
| CarVision | 8002 | POST /predict | < 100ms p95 |
| TelecomAI | 8003 | POST /predict | < 50ms p95 |

## Performance Targets

| Metric | Target | Critical |
|--------|--------|----------|
| p95 Latency | < 100ms | < 500ms |
| p99 Latency | < 200ms | < 1000ms |
| Error Rate | < 0.1% | < 1% |
| RPS (per instance) | > 100 | > 50 |

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
