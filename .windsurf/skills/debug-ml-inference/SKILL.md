---
name: debug-ml-inference
description: Debug ML inference issues — latency spikes, wrong predictions, event loop blocking
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(kubectl:*)
  - Bash(grep:*)
  - Bash(curl:*)
when_to_use: >
  Use when an ML service has inference errors, high latency, or incorrect predictions.
  Examples: 'inference is slow', 'predictions are wrong', '5xx from predict endpoint',
  'latency spike in Grafana', 'SHAP errors'
argument-hint: "<service-name> [symptom description]"
arguments:
  - service-name
authorization_mode:
  collect_traces: AUTO           # logs, metrics, kubectl describe
  diagnose: AUTO                 # apply heuristics from D-01..D-32 table
  propose_fix: AUTO              # produce a diff or runbook step in chat
  apply_fix_dev: AUTO            # reversible — dev cluster only
  apply_fix_staging: CONSULT     # staging change requires reviewer
  apply_fix_prod: STOP           # production patch is rollback-class
  escalation_triggers:
    - p1_alert_active: STOP             # drop tools, read rollback skill first
    - error_budget_exhausted: CONSULT   # do not change behavior without approval
    - root_cause_unclear: CONSULT       # avoid "fix-and-pray" in prod
---

# Debug ML Inference

Systematically diagnose and fix ML inference issues in production FastAPI services.

## Inputs
- `$service-name`: Name of the ML service to debug (e.g., `bankchurn`)

## Goal
Identify the root cause of the inference issue and either fix it or provide a specific
remediation plan with commands. Every check must produce evidence (command + output).

## Steps

### 1. Anti-Pattern Checklist (DO THIS FIRST)

Run this diagnostic before deep debugging — most inference issues match one of these patterns:

| # | Check | Command | Pass If |
|---|-------|---------|---------|
| D-01 | Multiple workers | `grep -rn "workers" $service-name/Dockerfile $service-name/k8s/` | `--workers` absent or exactly `1` |
| D-02 | Memory HPA | `grep -n "memory" $service-name/k8s/base/*hpa*` | Empty output |
| D-03 | Sync predict | `grep -rn "\.predict\|predict_proba" $service-name/app/` | Direct model calls only inside sync helpers delegated by `run_in_executor` |
| D-04 | TreeExplainer | `grep -rn "TreeExplainer" $service-name/` | None, or only in try/fallback |
| D-05 | `==` pinning | `grep "==" $service-name/requirements.txt` | No ML packages with `==` |
| D-06 | Suspiciously high metric | Check MLflow: primary > 0.99? | Below 0.99 |
| D-07 | SHAP background | Check background has both classes | Both high/low probs |
| D-08 | Uniform PSI bins | `grep -n "np.linspace\|uniform" $service-name/src/*/monitoring/` | Uses `np.percentile` |
| D-09 | Missing heartbeat | `grep -n "heartbeat" $service-name/k8s/ monitoring/` | Alert rule exists |
| D-10 | tfstate in git | `git ls-files \| grep tfstate` | Empty output |
| D-11 | Model in Docker | `grep -n "COPY.*model\|ADD.*model" $service-name/Dockerfile` | No matches |
| D-12 | No quality gates | `grep -rn "quality_gate\|should_promote" $service-name/src/` | Gate logic exists |
| D-21/D-22 | Blocking prediction logs | `grep -rn "log_prediction" $service-name/app/` | Logging is fire-and-forget and errors are swallowed |
| D-23 | Probe split | `grep -rn '"/health"\|"/ready"' $service-name/app/ $service-name/k8s/` | `/health` is liveness, `/ready` gates on model + warm-up |
| D-24 | SHAP rebuild per request | `grep -rn "KernelExplainer" $service-name/app/` | Built once during artifact load/warm-up, not inside endpoint |

**Success criteria**: All serving checks run, plus any D-13..D-32 checks
that match the symptom. Any violation is fixed or documented before
proceeding to deep debugging.

### 1b. FastAPI template contract

Before treating the symptom as service-specific, verify the scaffolded
contract still holds:

```bash
pytest tests/test_fastapi_template_contract.py -v
curl -f http://${ENDPOINT}/health
curl -f http://${ENDPOINT}/ready
curl -s http://${ENDPOINT}/metrics | head
```

If auth is enabled, include the same `X-API-Key` or Bearer token used by
clients when testing `/predict` and `/model/info`. A failure here means
the service has drifted from the template contract; fix that first.

### 2. Identify the Symptom

Classify the issue into one of:
- **High latency**: P95 above SLA → likely event loop blocking or resource contention
- **Wrong predictions**: Output doesn't match expectations → model or data issue
- **5xx errors**: Service crashes or timeouts → code or infrastructure issue
- **Score distribution shift**: Model output pattern changed → input drift or model staleness

**Success criteria**: Symptom classified with supporting evidence (logs, metrics, or user report).

### 3. Check Event Loop Blocking

The #1 cause of ML inference latency in FastAPI is blocking the event loop.

```bash
grep -r "run_in_executor" $service-name/app/
grep -r "sync_predict\|_sync_predict" $service-name/app/
```

If `model.predict()` is called directly in an `async def` endpoint → wrap it:
```python
loop = asyncio.get_running_loop()
return await loop.run_in_executor(_inference_executor, partial(_sync_predict, data))
```

**Success criteria**: Confirmed predict calls are wrapped in `run_in_executor`, or fix applied.

### 4. Check Worker Count

```bash
grep -r "workers" $service-name/Dockerfile k8s/base/$service-name-deployment.yaml
```

If `--workers N` where N > 1 under K8s → change to 1 worker. HPA handles scaling.

**Success criteria**: Confirmed single worker (or fix applied).

### 5. Check Model Loading

```bash
grep -r "joblib.load\|pickle.load\|load_model" $service-name/app/
```

Model should be loaded ONCE at startup (lifespan handler or module level), not per-request.

**Success criteria**: Model load is confirmed at startup, not inside endpoint functions.

### 6. Check SHAP Performance

If `/predict?explain=true` is slow:
- Verify background data is ≤ 50 samples
- Verify `nsamples` parameter in KernelExplainer (default 2*K+2048 can be excessive)
- SHAP is expected to be slower (seconds) — verify it's opt-in only

**Success criteria**: SHAP configuration verified or issue identified with fix.

### 7. Check Resource Limits

```bash
kubectl top pod -l app=$service-name -n ml-services
kubectl describe pod -l app=$service-name -n ml-services | grep -A5 "Limits\|Requests"
```

If CPU is at limit → HPA should scale. If not scaling → check HPA target.

**Success criteria**: Resource usage confirmed within limits or bottleneck identified.

### 8. Check Data Validation

```bash
kubectl logs -l app=$service-name -n ml-services --tail=100 | grep -i "SchemaError\|validation"
```

SchemaError means input data violates the Pandera schema → upstream data change.

**Success criteria**: No validation errors in logs, or schema mismatch identified.

## Rules
- Always check event loop blocking first — it's the most common cause
- Never recommend `--workers N` as a fix; always use ThreadPoolExecutor + HPA
- Use KernelExplainer, never TreeExplainer for ensemble/pipeline models
- Document findings in an incident report if the issue is production-impacting

## Quick Reference: Anti-Pattern → Fix

| Issue | Anti-Pattern | Fix | ADR |
|-------|-------------|-----|-----|
| CPU thrashing | `uvicorn --workers N` | Single worker + HPA | D-01 |
| HPA stuck | Memory-based metric | CPU-only HPA | D-02 |
| Event loop block | `model.predict()` in async | `run_in_executor` | D-03 |
| SHAP errors | TreeExplainer on ensemble | KernelExplainer | D-04 |

## Success criteria

The skill is complete when ALL of the following hold:

- [ ] Root cause identified — every claim has command + output as evidence
- [ ] If an anti-pattern (D-01..D-32) was violated, the specific ID is cited
- [ ] Either:
  * (dev) the fix has been applied AND the symptom no longer reproduces, OR
  * (staging/prod) a remediation plan with concrete commands is written
    and the operator has been handed off (CONSULT/STOP path)
- [ ] If production-impacting, a regression test is added in
      `tests/regression/` to prevent recurrence
- [ ] Audit entry written to `ops/audit.jsonl` with the timeline
      (symptom → diagnosis → fix or plan)
- [ ] If escalation_triggers fired (P1 active, error budget exhausted),
      the chain to `/rollback` or `/incident` was made explicit

A "fix" without evidence is a guess. The skill blocks until evidence
is collected.

## Related

- Workflow: `.windsurf/workflows/incident.md`
- Skill: `rollback` (if a deploy is the cause)
- Skill: `performance-degradation-rca` (if metric regression precedes)
