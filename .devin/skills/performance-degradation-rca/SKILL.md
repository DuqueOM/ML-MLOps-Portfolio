---
name: performance-degradation-rca
description: End-to-end RCA for a performance-degradation incident — correlates sliced metrics, drift, deploy history, upstream data changes, and prediction logs into one evidence-backed root cause.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(python:*)
  - Bash(kubectl:*)
  - Bash(gh:*)
  - Bash(mlflow:*)
  - Bash(curl:*)
when_to_use: >
  Use AFTER an SLO-level regression has been confirmed (e.g. AUC dropped
  global > 5 pp, or multiple slices are firing, or the on-call escalated
  from a fast-alert to an RCA). This skill BUILDS ON concept-drift-analysis
  (which handles one-slice analysis) by correlating multiple evidence
  streams and producing a blameless RCA document ready for review.
argument-hint: "<service-name> <incident-id> [--window-days N]"
arguments:
  - service-name
  - incident-id
authorization_mode:
  analyze: AUTO
  trigger_retrain: CONSULT
  promote_fix: STOP
---

# Performance Degradation RCA — Multi-stream root cause

This skill is the post-incident counterpart to `/rollback`. Rollback
restores service; this skill explains WHY degradation happened and what
long-term fix is needed to prevent recurrence.

## When NOT to use this skill

- **Single-slice performance alert** — use `concept-drift-analysis`
  first; it's narrower and faster.
- **Active incident with user impact** — run `/rollback` first, this
  skill after the dust settles.
- **Drift-only without performance impact** — use `drift-detection`;
  degradation RCA assumes ground truth has already revealed regression.

## Evidence streams

The skill correlates FIVE independent streams, then synthesizes:

1. **Sliced performance metrics** (from `performance_monitor` Prometheus
   push) — which slices degraded, by how much, when
2. **PSI drift history** (`ops/drift_reports/*.json`) — was the
   distribution shift gradual or sudden?
3. **Deploy + release history** (MLflow Registry, `kubectl rollout
   history`, GitHub Releases) — did a deploy precede the regression?
4. **Upstream data** (feature store / ETL provenance) — did an upstream
   schema or semantic change leak through?
5. **Prediction log statistics** — score distribution shift, error rate
   per version, logger error rate (if this spiked, our verdict is
   uncertain — flag it)

## Execution flow

### Step 1 — Incident intake (AUTO, 2 min)

```bash
# Confirm the incident is declared
gh issue view {incident-id} --json labels,body,createdAt

# Pull the current Prometheus alert state
curl -s "http://prometheus.monitoring:9090/api/v1/query?query=ALERTS{service='{service}'}" | jq '.'

# What alert(s) kicked this off? Record them as the starting hypothesis.
```

Output: a single-paragraph framing — "At {ts}, {alertname} fired for
{service} claiming {metric}={value}. Impact window: {start}→{end}."

### Step 2 — Sliced regression scan (AUTO, 3 min)

```bash
# What slices are below baseline? Which are ABOVE?
curl -s 'http://prometheus.monitoring:9090/api/v1/query_range?query=\
{service}_performance_metric{metric="auc"}&start=...&end=...&step=1h' | \
  jq '.data.result' > ops/incidents/{incident}/sliced_auc.json

# Rank slices by magnitude of regression (current - baseline)
python scripts/rank_regressions.py ops/incidents/{incident}/sliced_auc.json
```

Produce a table:

| slice | baseline | current | delta |
|-------|----------|---------|-------|
| by_country=MX | 0.87 | 0.71 | -0.16 |
| by_channel=web | 0.84 | 0.79 | -0.05 |
| _global | 0.86 | 0.80 | -0.06 |

If ONE slice dominates → likely segmented regression (data-quality or
population shift). If ALL slices drop together → likely model
regression (deploy, concept drift, upstream semantic change).

### Step 3 — Deploy correlation (AUTO, 2 min)

```bash
# When did the regression start?
REGRESSION_TS=$(python scripts/first_regression.py ...)

# Was there a deploy within ±6h?
kubectl argo rollouts history {service}-predictor -n {ns} \
  --no-headers | awk '{print $1, $2}'
# → map revisions to timestamps; cross-check with REGRESSION_TS
```

If yes → deploy-correlated. Pull the diff:
```bash
gh pr list --search "merged:<={REGRESSION_TS} state:merged" \
  -L 5 --json number,title,mergedAt
```

If no → data-correlated (proceed to Step 4).

### Step 4 — Drift correlation (AUTO, 3 min)

```bash
# Load the most recent PSI drift report
cat ops/drift_reports/$(ls ops/drift_reports/ | tail -1)

# Which features have PSI > alert threshold at REGRESSION_TS?
python scripts/correlate_drift.py --since "{REGRESSION_TS - 7d}"
```

Produce:

| feature | psi_at_regression | alert_threshold | 2x_threshold |
|---------|-------------------|-----------------|--------------|
| amount | 0.42 | 0.25 | 0.50 |
| country_mix | 0.12 | 0.20 | 0.40 |

If drift is SEVERE (> 2× threshold) AND one-slice-dominant →
data-quality incident (upstream change, ingestion bug).

### Step 5 — Prediction-log sanity (AUTO, 1 min)

```bash
# Was the logger healthy during the regression window?
curl -s 'http://prometheus.monitoring:9090/api/v1/query?query=\
rate(prediction_log_errors_total[24h])' | jq '.data.result'
```

If logger error rate > 5% during the window, our sliced metrics might
be biased by missing labels. FLAG THIS PROMINENTLY in the RCA.

### Step 6 — Synthesis (AUTO, 5 min)

The agent combines the four streams into ONE of the following root-cause
categories (select exactly one; confidence-scored):

- **R1 — Model regression** — deploy correlated; all slices drop; model
  version changed around REGRESSION_TS. Fix: revert or retrain the
  previous champion.
- **R2 — Concept drift** — no deploy; PSI within bounds; specific slices
  degraded over weeks. Fix: retrain with recent data.
- **R3 — Data-quality / semantic shift** — PSI > 2× threshold on feature
  {X}, one-slice-dominant. Fix: ingestion/ETL correction + retrain.
- **R4 — Monitoring failure** — logger error rate > 5%, inconclusive
  verdict. Fix: repair logger, re-run RCA.
- **R5 — Compound** — multiple signals; escalate to architecture review.

Each RCA MUST cite file paths, timestamps, PR numbers, and metric
values. No "probably" or "likely" without evidence.

### Step 7 — RCA document (CONSULT, 10 min)

Produce `docs/incidents/{date}-{service}.md` based on the template
below. Ping the on-call owner for review before committing.

```markdown
# RCA: {service} {incident-id}

## Timeline (UTC)
- {ts} — {alertname} fires
- {ts+5m} — on-call paged; confirms user impact
- {ts+15m} — rollback executed (rollout rev {N-1})
- {ts+2h} — performance stabilizes

## Root cause
{R1 | R2 | R3 | R4 | R5} — {one-sentence summary}

## Evidence
- Sliced AUC drop: {tabla}
- Drift report at REGRESSION_TS: {path}
- Deploy correlated: {PR # / none}
- Logger health: {%}

## Contributing factors
- ...

## Corrective actions (5 business days)
- [ ] {short-term fix, e.g. revert feature X}
- [ ] {medium-term, e.g. retrain with recent 30d}
- [ ] {long-term, e.g. add Pandera check for semantic range on feature X}

## Lessons
- {What would have caught this earlier?}
- {What should the skill / runbook / rule add?}
```

### Step 8 — Trigger retrain if recommended (CONSULT)

If the root-cause category is R2 or R3:

```bash
# Propose to operator:
gh workflow run retrain-{service}.yml \
  -f reason="RCA {incident-id}: {root cause}" \
  -f window="30d"
```

Agent emits `[AGENT MODE: CONSULT]` and waits for operator to confirm
the retrain trigger.

### Step 9 — Audit trail (AUTO)

Append `AuditEntry` tagged `operation: performance_rca,
incident: {incident-id}` to `ops/audit.jsonl`, carrying the root-cause
category and the list of evidence paths.

## Invariants

- RCA must select EXACTLY one primary root cause (no "both A and B"
  without explicit R5)
- Every claim carries evidence (`file:line`, metric value, PR URL)
- RCA doc lives under `docs/incidents/{date}-{service}.md`
- Corrective actions have owners and due dates (5 business days max)
- Blameless — names people who would benefit from a specific follow-up,
  never "who caused this"

## Related

- `.windsurf/skills/concept-drift-analysis/SKILL.md` — narrower, single-slice
- `.windsurf/skills/drift-detection/SKILL.md` — PSI-only, pre-RCA
- `.windsurf/skills/rollback/SKILL.md` — stabilizes BEFORE RCA
- `.windsurf/workflows/incident.md` — orchestrates this skill during
  active incidents
- `AGENTS.md §Audit Trail Protocol` — `AuditEntry` contract
