---
description: Run Locust load tests against ML services to validate SLAs
---

# /load-test Workflow

## 1. Select Target

Determine which service and environment to test:
- Service: ${SERVICE}
- Cloud: GCP / AWS / both
- Users: start with 10, ramp to 100

## 2. Configure Locust

Verify `scripts/load_test_services.py` has the correct endpoints and payloads for the target service.

Before starting load, verify the FastAPI contract with the same auth
posture production clients use:

```bash
curl -f http://${ENDPOINT}/health
curl -f http://${ENDPOINT}/ready
curl -X POST http://${ENDPOINT}/predict \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "load-smoke-001",
    "slice_values": {"smoke": "load"},
    "feature_a": 42.0,
    "feature_b": 50000.0,
    "feature_c": "category_A"
  }'
curl -s http://${ENDPOINT}/metrics | grep "_requests_total"
```

If the service has customized `app/schemas.py`, replace the smoke
payload with a schema-valid example from the service README before
running Locust. Do not load-test a payload that returns 422.

## 3. Run Load Test (GCP)

```bash
locust -f scripts/load_test_services.py \
  --host http://${GCP_ENDPOINT} \
  --users 100 \
  --spawn-rate 10 \
  --run-time 2m \
  --headless \
  --csv results/locust_gcp_${SERVICE}
```

## 4. Run Load Test (AWS)

```bash
locust -f scripts/load_test_services.py \
  --host http://${AWS_ENDPOINT} \
  --users 100 \
  --spawn-rate 10 \
  --run-time 2m \
  --headless \
  --csv results/locust_aws_${SERVICE}
```

## 5. Analyze Results

Check SLA compliance:
```
- Error rate: must be < 1% under 100 concurrent users
- P50 latency: must be < ${P50_SLA}ms
- P95 latency: must be < ${P95_SLA}ms
- P99 latency: document (informational)
```

## 6. Compare Clouds

| Metric | GCP | AWS | SLA |
|--------|-----|-----|-----|
| P50 (idle) | ___ms | ___ms | <${P50_SLA}ms |
| P95 (idle) | ___ms | ___ms | <${P95_SLA}ms |
| P50 (100u) | ___ms | ___ms | <${P50_LOAD_SLA}ms |
| Error rate | ___% | ___% | <1% |

## 7. Document Results

Update service README and relevant ADR with measured values, including:
- Date of measurement
- Instance types used
- Number of replicas during test
- HPA behavior observed

## 8. Action Items

If SLA violated:
- Check HPA scaling behavior
- Review ThreadPoolExecutor worker count
- Consider resource limit adjustments
- Document in ADR with cost analysis
