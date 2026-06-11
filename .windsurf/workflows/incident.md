---
description: ML service incident response — diagnose, mitigate, resolve, document
---

# /incident Workflow

## 0. Classify Severity (DO THIS FIRST — 30 seconds)

Answer these questions to determine severity:

```
Error rate > 5% in last 5 min?
  YES → P1 → Go to Step 1 (rollback NOW, investigate later)

AUC < 0.75 in recently labeled data?
  YES → P2 → Go to Step 2 (model degraded, 4h to fix)

PSI > 0.20 on any critical feature?
  YES → P3 → Go to Step 3 (drift confirmed, 24h)

PSI 0.10–0.20 or minor anomaly?
  YES → P4 → Go to Step 4 (monitor, 1 week)
```

| Severity | Symptoms | SLA | First Action |
|----------|----------|-----|-------------|
| **P1** | >5% error rate, service down | 15 min | Rollback immediately |
| **P2** | AUC < 0.75, metric degradation | 4 hours | Investigate + retrain |
| **P3** | PSI > 0.20 on critical feature | 24 hours | Analyze drift + plan retrain |
| **P4** | PSI 0.10-0.20, minor anomaly | 1 week | Monitor, increase frequency |

## 1. P1 — Immediate Rollback (SLA: 15 min)

```bash
# Step 1: Rollback deployment
kubectl rollout undo deployment/${SERVICE}-predictor -n ${NAMESPACE}
kubectl rollout status deployment/${SERVICE}-predictor -n ${NAMESPACE}

# Step 2: Verify recovery
curl -f http://${ENDPOINT}/health
curl -f http://${ENDPOINT}/ready
```

## 3. Diagnose Root Cause

### Check Logs
```bash
kubectl logs -l app=${SERVICE} -n ${NAMESPACE} --since=1h | grep -i "error\|exception\|traceback"
```

### Check Metrics
```bash
# Error rate
curl 'http://prometheus:9090/api/v1/query?query=rate(${SERVICE}_requests_total{status=~"5.."}[5m])'

# Latency
curl 'http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95, sum(rate(${SERVICE}_request_duration_seconds_bucket[5m])) by (le))'

# Drift
curl 'http://prometheus:9090/api/v1/query?query=${SERVICE}_psi_score'
```

### Check Infrastructure
```bash
kubectl top pod -l app=${SERVICE} -n ${NAMESPACE}
kubectl describe pod -l app=${SERVICE} -n ${NAMESPACE} | grep -A5 "Events\|Conditions"
```

## 4. Common Root Causes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| 5xx errors, high latency | Event loop blocking | Wrap in `run_in_executor` |
| OOM kills | Model too large for limits | Increase memory limit |
| Pods not starting | Init container failing | Check model download path |
| Wrong predictions | Stale model, data drift | Retrain or rollback |
| Schema errors (422) | Upstream data change | Update Pandera schema |

## 5. Mitigate

Based on root cause, apply the appropriate fix:
- **Code fix**: PR → CI → deploy
- **Model fix**: Trigger `/retrain` workflow
- **Infra fix**: Terraform apply → deploy
- **Data fix**: Coordinate with upstream team

## 6. Verify Resolution

- [ ] Error rate back to normal
- [ ] Latency within SLA
- [ ] No new alerts
- [ ] Health checks passing
- [ ] Predictions validated

## 7. Document Incident

Create incident report:
```markdown
## Incident: ${TITLE}
**Date**: YYYY-MM-DD HH:MM UTC
**Severity**: P{N}
**Duration**: {minutes}
**Impact**: {description}

### Timeline
- HH:MM — Alert fired
- HH:MM — Investigation started
- HH:MM — Root cause identified
- HH:MM — Fix deployed
- HH:MM — Resolution confirmed

### Root Cause
{description with measured evidence}

### Action Items
- [ ] {preventive action 1}
- [ ] {preventive action 2}
```

## 8. Follow-Up

- Create ADR if the incident reveals a new architectural decision
- Update runbook with new diagnostic steps
- Update alerts if thresholds need adjustment
- Schedule post-mortem if P1/P2
