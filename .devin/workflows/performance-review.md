---
description: Monthly sliced-performance review using ground-truth metrics — detect silent concept drift, document findings
---

# Performance Review Workflow

Cadence: monthly (first Monday). Also on-demand when a stakeholder asks
"how is the model doing vs last month?".

This is the CONCEPT DRIFT counterpart of `/cost-review`. Where cost-review
looks at \$/1000 predictions, this looks at how the model's REAL performance
has evolved once ground truth has caught up.

## Prerequisites

- At least 30 days of data in `data/predictions_log/` and `data/labels_log/`
- `models/baseline_metrics.json` present (produced at training time)
- `configs/slices.yaml` reflects current business dimensions

## 1. Collect window metrics

Run the performance monitor over progressively wider windows:

```bash
for window in 24h 7d 30d; do
  python -m src.{service}.monitoring.performance_monitor \
    --predictions data/predictions_log \
    --labels      data/labels_log \
    --slices      configs/slices.yaml \
    --window      ${window} \
    --baseline    models/baseline_metrics.json \
    --output      reports/perf_${window}.json
done
```

## 2. Build the review dashboard

```bash
# Global trend
jq -r '[.window.since, .global.auc, .global.f1] | @tsv' \
  reports/perf_*.json | sort

# Per-slice breakdown (30d)
jq '.slices' reports/perf_30d.json > reports/slices_30d.json
```

## 3. Identify degrading slices

Slice is "degrading" if its 30d AUC is lower than baseline by more than
`auc_drop_warning` (see `slices.yaml`), and its 7d AUC is lower than its
30d AUC (i.e., trending the wrong way).

```bash
python - <<'PY'
import json
r30 = json.load(open("reports/perf_30d.json"))
r7  = json.load(open("reports/perf_7d.json"))
baseline = json.load(open("models/baseline_metrics.json"))
for slice_name, groups in r30["slices"].items():
    for v, m in groups.items():
        if not isinstance(m, dict) or m.get("status") == "insufficient_data":
            continue
        auc_30 = m["auc"]
        auc_7  = r7["slices"].get(slice_name, {}).get(v, {}).get("auc", auc_30)
        drop = baseline["auc"] - auc_30
        if drop > 0.05 and auc_7 < auc_30:
            print(f"DEGRADING  {slice_name}={v}: 30d={auc_30:.3f} 7d={auc_7:.3f} drop={drop:.3f}")
PY
```

## 4. Root-cause (use concept-drift-analysis skill)

For each degrading slice, invoke the `concept-drift-analysis` skill's
decision tree. Do not retrain reactively — confirm the root cause first.

## 5. Document

Append to `docs/performance_review_log.md`:

```markdown
## YYYY-MM-DD — {service} monthly review

### Global metrics (30d vs training baseline)
- AUC: 0.XX (vs baseline 0.YY, Δ=-0.ZZ)
- F1:  0.XX
- Brier: 0.XX

### Slices flagged
- by_country=ES: AUC=0.58 — investigating (see concept_drift_log.md)
- by_channel=api: healthy

### Decisions
- No retraining this cycle
- Raised min_samples_per_slice to 100 for by_score_bucket (noisy)

### Next checkpoint
- Re-run on YYYY-MM-DD
```

## 6. (If needed) Propose retraining

If a real concept drift is confirmed:

```bash
gh workflow run retrain-{service}.yml \
  -f reason="Monthly review: AUC baseline→30d drop = X.XX"
```

The retrain workflow will run Champion/Challenger (ADR-008) — retraining
does NOT automatically replace the current model.

## What this workflow is NOT

- It is NOT an incident response (`/incident`).
- It does NOT alter thresholds without ADR approval.
- It is NOT a substitute for real-time alerts — those fire via
  PrometheusRule when the performance drop is acute. This workflow
  catches slow, silent drifts that never cross the hard alert threshold.
