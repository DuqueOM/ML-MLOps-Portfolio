---
description: Run Locust load tests against ML services and analyze latency, throughput, and error rates
---

## Load Test Workflow

1. Ask the user which service(s) to test (or all 3)

// turbo
2. Verify the target service is running and healthy:
   ```bash
   curl -s http://localhost:8000/health | jq .
   ```

3. Run Locust load test:
   ```bash
   python scripts/load_test_services.py \
     --service <service-name> \
     --users 10 \
     --spawn-rate 2 \
     --duration 60
   ```

4. Collect and analyze results:
   - **Throughput**: requests per second (target: >5 RPS per pod)
   - **Latency**: p50, p95, p99 (target: p95 <500ms)
   - **Error rate**: percentage of failed requests (target: 0%)
   - **CPU usage**: `kubectl top pods -l app=<service>`

5. Compare against baseline performance:
   | Service | Baseline avg | Baseline p95 | Baseline RPS |
   |---------|-------------|-------------|-------------|
   | BankChurn | 130ms | 240ms | 6.58 |
   | NLPInsight | 87ms | 220ms | 7.32 |
   | ChicagoTaxi | 103ms | 150ms | 7.05 |

6. If performance regressed >20%, investigate:
   - Check model size changes
   - Check ThreadPoolExecutor config (should be 4 workers)
   - Check CPU limits in K8s deployment
   - Check if uvicorn workers >1 (must be 1, ADR-014)

7. Generate summary report with findings and recommendations

// turbo
8. If testing in K8s, verify HPA behavior during load:
   ```bash
   kubectl get hpa -w
   ```
