---
name: rollback
description: Emergency rollback procedure for production ML service — Argo Rollouts abort + kubectl undo + MLflow revert + alert silencing
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(kubectl:*)
  - Bash(kubectl-argo-rollouts:*)
  - Bash(mlflow:*)
  - Bash(amtool:*)
  - Bash(curl:*)
  - Bash(gh:*)
when_to_use: >
  Use during an active production incident: metric regression confirmed,
  canary failure escalated to users, bad release of model or image, or
  drift/performance alert that the team decides must be reverted NOW
  rather than waiting for the next retrain cycle.
  Examples: 'rollback bankchurn to previous version', 'revert the
  deploy from last hour', 'emergency undo', 'something went wrong post-deploy'.
argument-hint: "<service-name> [target-revision]"
arguments:
  - service-name
authorization_mode:
  analyze: AUTO
  execute_rollback: STOP     # always — even in dev, human must approve
  silence_alerts: CONSULT
  close_incident: CONSULT
---

# Rollback — Emergency Procedure

This is the MOST CRITICAL skill in on-call. It must be predictable,
idempotent, and auditable. Execution is STOP-class: the agent produces
the plan; a human approves each destructive command.

## When NOT to use this skill

- **Flaky alert without user impact** → investigate with
  `concept-drift-analysis` first. Rollback has its own blast radius.
- **Degraded single slice, global healthy** → targeted retrain, not rollback.
- **Canary already auto-aborted by Argo Rollouts** → no action needed;
  verify and document.
- **Pre-canary issues (CI failures)** → use the deploy skill's abort path,
  not this one.

## Prerequisites

Before running the plan, verify:
- `kubectl config current-context` points at the affected cluster
- `kubectl argo rollouts version` is available OR kubectl with the
  `rollout` subcommand for plain Deployments
- GitHub token has `repo` + `actions` scopes for issue creation
- MLflow Tracking URI is reachable (check via `mlflow experiments list`)

## Decision tree

```
              Incident declared
                      │
         ┌────────────┴────────────┐
     Argo Rollouts?          Plain Deployment?
         │                         │
  kubectl argo rollouts        kubectl rollout undo
  abort + undo                 deployment/{service}
         │                         │
         └────────────┬────────────┘
                      │
          Wait for Ready (kubectl rollout status)
                      │
         ┌────────────┴────────────┐
     Model changed?            Image-only change?
     (MLflow revert)           (done)
         │
  MLflow transition_model_version_stage
  Previous → Production
         │
  POST /model/reload to each pod (or restart)
         │
  Silence incident-related alerts
         │
  Open audit issue (labels: rollback, incident)
```

## Step 1 — Confirm the incident (AUTO, 1 min)

```bash
# Who is firing?
kubectl get prometheusrules -n monitoring -o json | \
  jq '.items[].spec.groups[].rules[] | select(.alert != null) | .alert'

# Current rollout state
kubectl argo rollouts get rollout {service}-predictor -n {namespace}

# Recent deploys
kubectl rollout history deployment/{service}-predictor -n {namespace}
kubectl argo rollouts history {service}-predictor -n {namespace}
```

Agent outputs a short evidence pack: alert names, revisions, timestamps.

## Step 2 — Identify the target revision (AUTO, 1 min)

Pick the revision to revert to. The agent proposes the IMMEDIATELY
PREVIOUS healthy revision unless the operator specifies otherwise.

```bash
# For Argo Rollouts (default in this template)
kubectl argo rollouts get rollout {service}-predictor -n {namespace} \
  -o json | jq '.status.history[] | {revision, status, images: [.template.spec.containers[].image]}'

# For plain Deployment
kubectl rollout history deployment/{service}-predictor -n {namespace} --revision=<N-1>
```

Agent emits `[AGENT MODE: STOP]` with the proposed target.

## Step 3 — Execute rollback (STOP, 2 min)

Once the operator confirms the target revision:

### Case A — Argo Rollouts (default)

```bash
# Immediately stop any in-progress canary
kubectl argo rollouts abort {service}-predictor -n {namespace}

# Roll back to the last stable revision (K-1 in the history)
kubectl argo rollouts undo {service}-predictor -n {namespace} \
  --to-revision={target-revision}

# Wait until the new stable is fully rolled out
kubectl argo rollouts status {service}-predictor -n {namespace} \
  --watch --timeout 10m
```

### Case B — Plain Deployment (legacy services without Argo)

```bash
kubectl rollout undo deployment/{service}-predictor -n {namespace} \
  --to-revision={target-revision}
kubectl rollout status deployment/{service}-predictor -n {namespace} \
  --timeout 10m
```

## Step 4 — Revert the model artifact if needed (STOP, 2 min)

An image-only rollback (code fix, dependency fix) does not require this
step. But if the bad release included a new model artifact promoted in
MLflow Registry, the artifact ALSO must move back:

```bash
python - <<PY
import mlflow
c = mlflow.tracking.MlflowClient()
# Previous production version → Production
# Current production version → Archived
c.transition_model_version_stage('{service}Model', version={previous}, stage='Production')
c.transition_model_version_stage('{service}Model', version={current}, stage='Archived')
print('MLflow registry reverted')
PY

# Trigger pods to pick up the old model (init container re-downloads)
kubectl rollout restart deployment/{service}-predictor -n {namespace}
# OR hot-reload without restart:
for pod in $(kubectl get pods -l app={service} -n {namespace} -o name); do
  kubectl exec -n {namespace} $pod -- curl -s -X POST http://localhost:8000/model/reload
done
```

## Step 5 — Silence alerts related to the incident (CONSULT, 1 min)

Alerts that were caused BY the incident will self-resolve as the rollback
propagates. But alerts already queued MUST be silenced to prevent
downstream paging. Proposed silence duration: 2h. Always extend rather
than let alerts fire again before the postmortem.

```bash
# Alertmanager silence (requires amtool or /api/v2/silences)
amtool silence add \
  alertname=~"({AlertA}|{AlertB})" \
  service={service} \
  --duration=2h \
  --comment="Rollback in progress — ref: incident {incident-id}" \
  --author="rollback-skill"
```

## Step 6 — Verify (AUTO, 2 min)

```bash
# Pods Ready?
kubectl get pods -l app={service} -n {namespace}

# Readiness probe returns 200?
kubectl exec -n {namespace} <pod> -- curl -s http://localhost:8000/ready

# Error rate back down?
curl -s 'http://prometheus.monitoring:9090/api/v1/query?query=sum(rate({service}_requests_total{status=~"5.."}[2m]))/sum(rate({service}_requests_total[2m]))'

# Score distribution returned to stable-version profile?
curl -s 'http://prometheus.monitoring:9090/api/v1/query?query=histogram_quantile(0.5,sum(rate({service}_prediction_score_bucket[5m]))by(le))'
```

All four signals must return to pre-incident baselines before the rollback
is declared complete.

## Step 7 — Document (CONSULT, 5 min)

Create an incident issue with all the evidence gathered above:

```bash
gh issue create \
  --title "Rollback: {service} {incident-id}" \
  --body "$(cat <<EOF
## Incident summary
- Start: {start-ts}
- End: {rollback-complete-ts}
- Duration: {duration}
- User impact: {brief}

## Rollback evidence
- Rolled back: rev {current} → rev {previous}
- MLflow model: v{N} → v{N-1}
- Alerts silenced: {list}

## Metrics
- Error rate pre/post: {before}% → {after}%
- p95 latency pre/post: {before}ms → {after}ms

## Next steps
- [ ] Postmortem scheduled for {date}
- [ ] Regression test added to tests/regression/
- [ ] Blameless RCA doc in docs/incidents/{date}-{service}.md
EOF
)" \
  --label "rollback,incident,postmortem-needed"
```

## After the incident

Within 5 business days, the on-call owner MUST:
1. File a blameless RCA in `docs/incidents/{YYYY-MM-DD}-{service}.md`
2. Add a regression test for the failure mode (NOT a pytest of the
   symptom — a test for the ROOT cause)
3. Update the relevant runbook if the incident exposed a gap in this
   skill

## Invariants

- Rollback NEVER runs without human approval (STOP mode), even in dev
- Every executed rollback produces an audit issue (visible, searchable)
- Alerts are SILENCED, not deleted — silence expires and forces review
- Postmortem is not optional; the skill explicitly depends on it to
  avoid repeat incidents
