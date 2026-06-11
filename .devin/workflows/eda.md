---
description: Run 6-phase exploratory data analysis on a new dataset — ingest, profile, leakage gate, feature proposals
---

# /eda Workflow

Triggers the `eda-analysis` skill on a new dataset. Invokes specialist agents across
6 phases and chains to `/new-service` if leakage gate passes, or `/incident` if it fails.

## When to run

- New raw dataset added to `data/raw/`
- Before training any new model variant
- After a major schema change in the source data
- When drift detection baseline needs to be refreshed (re-run EDA phase 2)

## Arguments

- `<dataset-path>`: Path to the dataset (CSV, Parquet). Example: `data/raw/transactions.csv`
- `<service-slug>`: (Optional) Service this EDA supports. Example: `fraud_detector`

## Steps

### 1. Setup
```bash
pip install -r templates/eda/requirements.txt
mkdir -p eda/reports eda/artifacts eda/notebooks
```

### 2. Invoke `eda-analysis` skill
The skill executes phases 0–6 (see `.windsurf/skills/eda-analysis/SKILL.md`).

### 3. Leakage gate check
After phase 4:
- **If `BLOCKED_FEATURES` is empty** → continue to step 4
- **If non-empty** → chain to `/incident` (severity P2: "EDA leakage gate failed for <dataset>"). Halt.

### 4. Review outputs
Engineer reviews:
- `eda/reports/eda_summary.md` — human summary
- `eda/artifacts/feature_catalog.yaml` — approve/reject each proposal
- `src/{service}/schema_proposal.py` — copy accepted parts to `schemas.py`

### 5. Close the drift loop
Update drift detection config to reference `eda/artifacts/baseline_distributions.parquet`.
Verify drift CronJob manifest:
```bash
grep -l "baseline_distributions" k8s/base/drift-cronjob.yaml
```

### 6. Commit via DVC
```bash
dvc add data/raw/<dataset>
dvc add eda/artifacts/baseline_distributions.parquet
git add eda/ .dvc/
git commit -m "feat(eda): complete EDA for <dataset>"
dvc push
```

### 7. Chain to next workflow
- **New service**: chain to `/new-service` with the scaffolded EDA outputs as inputs
- **Existing service**: proceed to training (no workflow, just `make train`)
- **Refresh only**: no chain — EDA artifacts replaced, drift detection picks up new baseline on next run

## Success criteria
- All 6 phases complete
- Leakage gate passed (empty `BLOCKED_FEATURES`)
- `baseline_distributions.parquet` DVC-tracked and wired to drift CronJob
- `feature_catalog.yaml` reviewed with engineer sign-off
- ADR entry drafted citing `eda_summary.md`

## Related
- Skill: `eda-analysis`
- Rule: `.windsurf/rules/11-data-eda.md`
- Anti-patterns: D-13 (sandbox), D-14 (schema ranges), D-15 (baseline), D-16 (rationale)
- Next workflow: `/new-service` (if new) or `/retrain` (if refresh)
