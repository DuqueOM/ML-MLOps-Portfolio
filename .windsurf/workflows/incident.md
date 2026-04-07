---
description: Guided incident response for ML service outages, performance degradation, or unexpected behavior
---

## Incident Response Workflow

1. **Identify the affected service(s)** — ask user or check alerts:
   ```bash
   kubectl get pods --all-namespaces | grep -v Running
   kubectl get events --sort-by='.lastTimestamp' | tail -20
   ```

2. **Classify severity**:
   - **P1 (Critical)**: Service completely down, 0 successful predictions
   - **P2 (Major)**: Error rate >10% or p95 latency >2s
   - **P3 (Minor)**: Degraded performance, p95 >500ms but functional
   - **P4 (Low)**: Cosmetic issues, non-blocking warnings

// turbo
3. **Gather diagnostic data**:
   ```bash
   kubectl logs -l app=<service> --tail=200 --since=30m
   kubectl describe pod -l app=<service>
   kubectl top pods -l app=<service>
   kubectl describe hpa <service>-hpa
   ```

4. **Check common root causes** (invoke `debug-ml-inference` skill for details):
   - Pod CrashLoopBackOff → model file missing, OOM, import error
   - High error rate → multi-worker uvicorn (ADR-014), numpy incompatibility (ADR-005)
   - HPA stuck → memory metric in HPA spec (ADR-001)
   - Slow predictions → CPU limits too low, ThreadPoolExecutor misconfigured (ADR-015)
   - SHAP errors → TreeExplainer with StackingClassifier (ADR-010)

5. **Implement fix**:
   - Prefer minimal upstream fix over downstream workaround
   - For P1/P2: apply hotfix, then proper fix in follow-up PR
   - For P3/P4: fix in normal development cycle

// turbo
6. **Verify fix**:
   ```bash
   kubectl rollout status deployment/<service>
   ./scripts/smoke_test.sh
   ```

7. **Post-incident**:
   - Document root cause, timeline, and resolution
   - Create ADR if architectural decision changed (use `/new-adr` workflow)
   - Add regression test to prevent recurrence
   - Update monitoring/alerts if gap detected

8. **Communicate**: Summarize incident, impact, and preventive measures
