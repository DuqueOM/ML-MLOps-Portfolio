---
name: concept-drift-analysis
description: Root-cause a performance alert using sliced metrics + ground-truth
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(python:*)
  - Bash(kubectl:*)
  - Bash(gh:*)
when_to_use: >
  Use when a performance-level alert fires (AUC/F1 dropped), when you need to
  discriminate concept drift from data drift, or when a slicing alert asks
  'why is country=ES AUC low?'. Pairs naturally with drift-detection (PSI)
  but focuses on GROUND-TRUTH-BACKED metrics, not feature distributions.
  Examples: 'AUC dropped for country=ES', 'concept drift analysis', 'why is
  F1 low', 'interpret performance report'
argument-hint: "<service-name> [--slice <slice=value>]"
arguments:
  - service-name
authorization_mode:
  analyze: AUTO          # reading reports, cross-referencing metrics
  update_baseline: CONSULT
  trigger_retrain: CONSULT
---

# Concept Drift Analysis

This skill is the RCA counterpart to `drift-detection`. Where PSI detects
*feature-distribution change*, this skill detects and diagnoses
*performance degradation* using delayed ground-truth labels.

## Inputs you need

- `reports/performance.json` from the most recent CronJob run (or manual run)
- Baseline metrics from training: `models/baseline_metrics.json`
- (Optional) `drift_report.json` to cross-reference with PSI

## Decision tree

```
                    Performance alert fired
                             │
               ┌─────────────┴─────────────┐
         Global AUC low?             Only sliced AUC low?
               │                             │
       ┌───────┴───────┐           ┌─────────┴─────────┐
   Data drift         No drift   Drift in same slice?   No drift?
       │                │               │                 │
  Retrain on       Label noise     Targeted retrain   Label quality
  fresh data       or real         or feature fix     in that segment
                   concept drift
```

## Step 1: Read the report

```bash
jq '.status, .global, .alerts' reports/performance.json
jq '.slices' reports/performance.json   # per-slice breakdown
```

Identify which slices fired alerts. Each entry has:
```json
{ "slice_name": "by_country", "slice": "country=ES", "metric": "auc",
  "value": 0.58, "threshold": 0.65 }
```

## Step 2: Distinguish global vs sliced

```bash
# Global AUC
jq '.global.auc' reports/performance.json
# All slice AUCs, sorted ascending
jq -r '.slices | to_entries[] | .value | to_entries[] | [.key, .value.auc] | @tsv' \
  reports/performance.json | sort -k2 -n
```

- **Global degradation** (many slices low)       → population-wide concept drift
- **Single-slice degradation** (others healthy)  → subpopulation issue
- **Healthy global, healthy slices**             → false alarm from window size

## Step 3: Cross-reference with data drift

Correlate slice degradation with feature PSI in the SAME window:

```bash
jq '.features | to_entries[] | select(.value.psi > 0.15)' drift_report.json
```

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| High PSI + sliced AUC drop in same slice | Upstream data pipeline for that segment | Fix ETL, no retrain yet |
| High PSI everywhere + global AUC drop | New data regime | Full retrain |
| No PSI + AUC drop in one slice | Label noise or concept shift | Inspect labels_log for that slice |
| No PSI + global AUC drop | Ground-truth pipeline degraded | Verify ingester heartbeat |

## Step 4: Sample size sanity

```bash
jq '.slices.by_country | to_entries[] | {slice: .key, n: .value.sample_size, status: .value.status}' \
  reports/performance.json
```

If `status == "insufficient_data"` for the flagged slice, you are looking at
noise. Raise `min_samples_per_slice` in `configs/slices.yaml` or wait for
more data. DO NOT retrain on noise.

## Step 5: Label causality check

Before blaming the model, rule out ground-truth quality:

```bash
# Check ingester heartbeat
kubectl get cronjob {service}-ground-truth-ingester -n {namespace}
kubectl logs job/{service}-ground-truth-ingester-<timestamp>

# Verify labels have non-trivial class balance
python -c "
import pandas as pd, glob
files = sorted(glob.glob('data/labels_log/year=*/month=*/day=*/*.parquet'))[-7:]
df = pd.concat(pd.read_parquet(f) for f in files)
print(df['true_value'].value_counts())
"
```

A sudden swing in class balance often explains AUC/F1 drops without any
model change.

## Step 6: Decide next action

| Diagnosis | Action | Mode |
|-----------|--------|------|
| Noise (small n)                               | Wait, widen window | AUTO |
| Subpopulation data pipeline issue             | Fix ETL; no retrain | CONSULT |
| Real sliced concept drift                     | Retrain (possibly with reweighted sampling) | CONSULT |
| Population-wide concept drift                 | Trigger `/retrain` | CONSULT |
| Ground-truth pipeline broken                  | Fix ingester; mute alert for now | STOP-for-retrain |
| Label noise                                   | Escalate to data team | STOP-for-retrain |

Trigger retraining only after confirming real concept drift:

```bash
gh workflow run retrain-{service}.yml \
  -f reason="Concept drift confirmed: global AUC ${auc} vs baseline ${baseline}; slices: ${slices}"
```

The retrain workflow will execute C/C (ADR-008) — do not assume promotion.

## Step 7: Post-RCA artifact

Always append a short entry to `docs/concept_drift_log.md`:

```markdown
## 2026-04-23 — {service} concept-drift incident

- **Triggered by**: SlicedAUCBelowAlert country=ES (AUC=0.58)
- **Global AUC**: 0.84 (healthy)
- **Slice AUC**: 0.58 (ES), 0.87 (US), 0.85 (MX)
- **Data drift in ES**: PSI(feature_X) = 0.24
- **Root cause**: ES-specific data pipeline joined stale partner feed
- **Action taken**: Fixed ETL partition filter; no retrain
- **Confirmed resolved**: 2026-04-24 report shows ES AUC = 0.86
```

This log is cheap insurance against repeated debugging of the same issue.

## What this skill is NOT

- It is NOT for real-time debugging of inference (that is `debug-ml-inference`).
- It is NOT for data drift as an early signal (that is `drift-detection`).
- It does NOT promote or demote models (that is `model-retrain` + ADR-008).
