---
name: debug-ml-inference
description: Diagnoses ML inference issues including slow predictions, wrong outputs, SHAP errors, model loading failures, and HPA scaling problems in Kubernetes. Cross-references project ADRs for root cause analysis.
---

## Diagnostic Flowchart

### Step 1: Identify Symptom Category

| Symptom | Likely Root Cause | First Check |
|---------|------------------|-------------|
| Slow predictions (>500ms p95) | ThreadPoolExecutor saturation, CPU limits | `kubectl top pods`, check workers config |
| Wrong prediction values | Model version mismatch, numpy incompatibility | Check model version, numpy pinning |
| SHAP returns all zeros | Missing shap dep, wrong explainer type | Check requirements.txt, KernelExplainer |
| Pod CrashLoopBackOff | Model file missing, OOM, import error | `kubectl logs`, `kubectl describe pod` |
| HPA stuck at max replicas | Memory-based HPA (fixed footprint) | `kubectl describe hpa`, check metrics |
| HPA never scales down | Memory metric in HPA spec | Verify CPU-only HPA (ADR-001) |
| 81%+ error rate under load | Multi-worker uvicorn thrashing | Check --workers flag (must be 1, ADR-014) |

### Step 2: Collect Evidence

```bash
# Pod status and logs
kubectl get pods -l app=<service> -o wide
kubectl logs -l app=<service> --tail=200
kubectl describe pod <pod-name>

# Resource usage
kubectl top pods -l app=<service>
kubectl top nodes

# HPA status
kubectl describe hpa <service>-hpa
kubectl get hpa -w  # watch mode

# Service endpoints
kubectl get svc <service>
curl -s http://<service-ip>:<port>/health | jq .
```

### Step 3: Cross-Reference ADRs

See `adr-quick-reference.md` in this skill directory for the full reference.

### Step 4: Resolution Pattern

1. **Document** the root cause clearly
2. **Implement** the minimal fix (prefer upstream fix over downstream workaround)
3. **Add regression test** to prevent recurrence
4. **Update ADR** if the fix changes an architectural decision
5. **Verify** fix under load with `scripts/load_test_services.py`
