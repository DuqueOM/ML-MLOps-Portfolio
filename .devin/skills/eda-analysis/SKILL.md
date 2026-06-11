---
name: eda-analysis
description: Run 6-phase exploratory data analysis on a new dataset — ingest, profile, univariate, correlations, leakage gate, feature proposals
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash(python:*)
  - Bash(dvc:*)
  - Bash(jupyter:*)
when_to_use: >
  Use when given a new dataset (data/raw/*.csv|parquet) before any training happens.
  Examples: 'explore this customer churn dataset', 'do EDA on the fraud transactions data',
  'analyze the new loan applications CSV'.
argument-hint: "<dataset-path> [service-slug]"
arguments:
  - dataset-path
  - service-slug
authorization_mode:
  ingest_profile: AUTO           # read CSV/Parquet, compute stats, no side effects outside eda/
  univariate_correlations: AUTO  # local plots + summary tables
  leakage_gate: AUTO             # boolean check; result drives next mode
  propose_features: AUTO         # writes feature_catalog.yaml only
  propose_schema: AUTO           # writes schema_proposal.py only
  escalation_triggers:
    - leakage_detected: STOP            # ANY blocked feature → halt; ADR-014 / D-13
    - target_metric_over_99: STOP       # suspicious — investigate before training
    - missing_target_column: CONSULT    # human decides label strategy
    - data_outside_data_raw: STOP       # never read from arbitrary paths
---

# EDA Analysis Skill

Guides the agent through a **6-phase EDA pipeline** that produces artifacts consumed by
training (`features.py`), schema generation (`schemas.py`), and drift detection in production
(`baseline_distributions.parquet`).

## Inputs
- `$dataset-path`: Path to raw data (e.g., `data/raw/transactions.csv`)
- `$service-slug`: Optional — the snake_case service name the EDA belongs to

## Goal
Complete EDA with all 6 artifacts produced, leakage audit passing (or explicitly resolved),
and `feature_catalog.yaml` ready for `features.py` consumption.

## Pre-conditions
- `templates/eda/eda_pipeline.py` is available (copied by `new-service.sh`)
- Dataset is in `data/raw/` (NEVER read from production paths — invariant D-13)
- Required deps installed: `pip install -r eda/requirements.txt`

## Steps

### Phase 0 — Ingest & Normalization
**Trigger**: Agent-DataValidator. Raw file arrives in `data/raw/`.

1. Detect encoding with `chardet` (non-ASCII datasets are common)
2. Load with `pandas.read_csv` / `read_parquet`
3. Normalize columns: `df.columns = df.columns.str.lower().str.replace(r'\W+', '_', regex=True)`
4. Drop fully-null columns
5. `dvc add data/raw/<file>` if not already tracked

**Output**: `data/processed/dataset_clean.parquet`, `eda/reports/00_ingest_report.md`

**Success criteria**: File loads, all columns are `snake_case`, DVC hash recorded.

### Phase 1 — Structural Profile
**Trigger**: Agent-EDAProfiler. Clean dataset available.

1. Shape, dtypes, memory footprint
2. Null counts + percentages per column
3. Cardinality per column (distinguishes categorical from high-cardinality)
4. Exact duplicates + near-duplicates (MinHash for >100k rows)
5. Index integrity + temporal coverage (if datetime column detected)

**Output**: `eda/reports/01_profile.html` (ydata-profiling or lightweight), canonical `eda/artifacts/schema_ranges.json`

**Success criteria**: Profile report generated. `schema_ranges.json` enumerates every column with inferred dtype and observed range.

### Phase 2 — Univariate Distributions + Baseline
**Trigger**: Agent-EDAProfiler. **Critical phase — feeds drift detection.**

1. For numeric: mean/std/skew/kurtosis, IQR outliers, normality test
2. For categorical: frequency, dominance, rare labels (<1%)
3. Target distribution: class balance, imbalance ratio
4. **Quantile bin boundaries** per feature (stored for PSI computation)

**Output**: `eda/reports/02_univariate.html`, **`eda/artifacts/baseline_distributions.parquet`**

**Success criteria**: `baseline_distributions.parquet` exists with quantile bins for each feature. This file is the source of truth for drift detection in production. Missing = D-15 violation.

### Phase 3 — Multivariate Correlations + VIF
**Trigger**: Agent-EDAProfiler.

1. Pearson (numeric↔numeric), Spearman (ordinal), Cramér's V (categorical↔categorical)
2. VIF (Variance Inflation Factor) for multicollinearity — flag features with VIF > 10
3. Feature-to-target correlation ranking

**Output**: `eda/reports/03_correlations.html`, `eda/artifacts/03_feature_ranking_initial.csv`

**Success criteria**: Ranking CSV produced with top 20 features by target correlation. Multicollinearity groups identified.

### Phase 4 — Leakage Detection (HARD GATE)
**Trigger**: Agent-DataValidator. **This phase can BLOCK the pipeline.**

1. Correlation > 0.95 with target → suspicious
2. Features derived from target (check for variance identity)
3. Temporal leakage: future information in time-series features
4. Near-duplicate rows with near-identical targets
5. Mutual information with target > threshold

**Output**: canonical `eda/artifacts/leakage_report.json` plus human-readable `eda/reports/04_leakage_audit.md`

**Success criteria**:
- If `BLOCKED_FEATURES: []` → continue to phase 5
- If non-empty → **HALT**. Chain to `/incident` workflow with severity P2. Engineer must:
  - Investigate each flagged feature
  - Document resolution (exclude, transform, or justify with ADR)
  - Re-run phase 4 until empty before proceeding

### Phase 5 — Feature Proposals
**Trigger**: Agent-MLTrainer + Agent-EDAProfiler (collaborative).

Based on phases 2–3, propose transformations with documented rationale:
- Skewed numeric (|skew| > 1) → log or boxcox transform
- High cardinality categorical (> 50 unique) → target encoding or binning
- Interaction candidates (pairs with meaningful combined signal)
- Time-based features if datetime present (hour, day_of_week, is_weekend)

**Output**: `eda/artifacts/feature_catalog.yaml`

**Success criteria**: Every proposal has a `rationale` field citing specific EDA findings (e.g., "skew=2.3 → boxcox stabilizes variance"). Invariant D-16 enforced.

### Phase 6 — Consolidation + Schema Proposal
**Trigger**: Agent-DocumentationAI + Agent-DataValidator.

1. Generate `eda/reports/eda_summary.md` with key findings (for ADR)
2. Generate `src/{service}/schema_proposal.py` — Pandera `DataFrameModel` with observed ranges
   (Engineer REVIEWS and copies to `schemas.py`. Never auto-overwrite.)
3. Ensure `baseline_distributions.parquet` is DVC-tracked and referenced from drift CronJob config

**Output**: `eda/reports/eda_summary.md`, `src/{service}/schema_proposal.py`, ADR entry

**Success criteria**:
- `eda_summary.md` produced with measurable findings
- `schema_proposal.py` has ranges derived from observed data (D-14 enforced)
- Drift CronJob config updated to load `baseline_distributions.parquet` (closes the loop)

## Rules
- Never skip phase 4 (leakage gate) — proceeding past a non-empty `BLOCKED_FEATURES` is an automatic P2 incident
- Never auto-overwrite `schemas.py` — produce `schema_proposal.py` for human review
- Never read from production data paths — violation of D-13
- Always commit `baseline_distributions.parquet` via DVC before closing EDA phase
- Notebook outputs (cells with results) are allowed but `.html`/`.png` reports in `eda/reports/` stay out of git (see `.gitignore`)

## Acceptance Criteria

EDA is complete when ALL of these pass:
- [ ] All 6 phases produced their expected artifacts
- [ ] `leakage_report.json` shows `blocked_features: []`
- [ ] `baseline_distributions.parquet` is DVC-tracked
- [ ] `feature_catalog.yaml` has rationale on every entry
- [ ] `schema_proposal.py` exists with observed ranges
- [ ] `eda_summary.md` ready for ADR citation
- [ ] Drift detection CronJob config points to `baseline_distributions.parquet`
