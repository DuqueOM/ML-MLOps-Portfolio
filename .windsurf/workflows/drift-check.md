---
description: Run PSI-based drift detection on ML models, analyze results, and trigger retraining if needed
---

## Drift Check Workflow

1. Ask the user which service to check (or all 3)

// turbo
2. Verify drift detection infrastructure is running:
   ```bash
   kubectl get cronjob drift-detection
   kubectl get jobs -l app=drift-detection --sort-by=.metadata.creationTimestamp | tail -5
   ```

3. Trigger a manual drift check if needed:
// turbo
   ```bash
   kubectl create job drift-check-manual --from=cronjob/drift-detection
   ```

4. Wait for completion and collect results:
   ```bash
   kubectl wait --for=condition=complete job/drift-check-manual --timeout=300s
   kubectl logs job/drift-check-manual
   ```

5. Analyze PSI values per feature (invoke `drift-detection` skill for thresholds):
   - PSI < 0.1 → **STABLE** — no action
   - 0.1 ≤ PSI < 0.25 → **WATCH** — monitor next 7 days
   - PSI ≥ 0.25 → **RETRAIN** — trigger retraining

6. If drift detected, investigate root cause:
   - Seasonal change? → Adjust thresholds
   - Data pipeline bug? → Fix upstream
   - Population shift? → Retrain with new data

7. If retraining needed, use `/retrain` workflow

8. Query Prometheus for drift metrics history:
   ```bash
   curl -s "http://localhost:9090/api/v1/query_range?query=bankchurn_drift_psi&start=$(date -d '7 days ago' +%s)&end=$(date +%s)&step=86400"
   ```

9. Generate drift report summary with findings and recommended actions

10. If no drift detected, log the clean check result for audit trail
