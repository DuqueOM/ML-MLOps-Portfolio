---
name: batch-inference
description: Scaffold and run batch scoring jobs (CronJob + Parquet output) that reuse the service's model + feature-engineering code without opening the live API
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash(kubectl:*)
  - Bash(python:*)
  - Bash(gcloud:*)
  - Bash(aws:*)
when_to_use: >
  Use when the business needs SCHEDULED scoring over a large dataset
  (nightly customer scoring, monthly eligibility ranking, weekly risk
  review) and the per-row latency of the real-time API would exceed
  the job budget. Also use for backfill when a new model needs scores
  for historical entities.
argument-hint: "<service-name> [--schedule '0 2 * * *'] [--output gs://bucket/path/]"
authorization_mode:
  scaffold: AUTO
  deploy_cronjob: CONSULT
  enable_in_prod: STOP
---

# Batch Inference — scheduled scoring jobs

Real-time /predict serves one request at a time. Batch scoring reuses
the SAME feature engineering + model artifact but runs over millions
of rows in one process. Sharing the code path prevents training/serving
skew AND training/batch skew — the classic silent-ML-failure mode.

## When NOT to use this skill

- **Intermittent one-offs** — script + argparse inside the service repo
  suffices; no need for a K8s CronJob.
- **Scoring must happen inline** (form submission, checkout flow) —
  that is real-time; use /predict.
- **Training-adjacent batch** (e.g., feature backfill for re-training)
  — that belongs in the training pipeline, not a batch scoring job.

## Architecture

```
templates/service/
├── app/                 # real-time API (unchanged)
├── src/{service}/
│   ├── predictor.py     # EXISTING: shared predict() — used by both paths
│   └── batch.py         # NEW: batch runner — main() entry
└── k8s/base/
    └── cronjob-batch.yaml   # NEW: scheduled execution
```

Key principle: **both paths import `predictor.predict()`**. Never
duplicate feature engineering. Any change to prediction logic auto-
propagates to both.

## Execution flow

### Step 1 — Confirm intent (AUTO, 30s)

Agent confirms:
- service name + code path exists
- business cadence (hourly / daily / weekly / monthly)
- input source (BigQuery table, S3 parquet, GCS folder)
- output sink (parquet partitioned by date, BigQuery table, RDS)
- expected row count per run (sizes the K8s resources)

### Step 2 — Scaffold `src/{service}/batch.py` (AUTO)

The scaffolded module MUST:

1. Read input via a PANDAS/Polars DataFrame
2. Validate via the SAME Pandera schema used in training (rule 08)
3. Call `predictor.predict_batch(df)` — same code as `/predict`
4. Emit predictions as partitioned parquet with `prediction_id`,
   `entity_id`, `model_version`, `prediction_score`, `timestamp`
5. **Also** call `log_prediction()` for each row — the closed-loop
   flywheel works for batch too (ADR-006, D-20/D-22)
6. Emit metrics:
   * `{service}_batch_rows_processed_total`
   * `{service}_batch_duration_seconds`
   * `{service}_batch_errors_total`

```python
# src/{service}/batch.py (excerpt)
from common_utils.prediction_logger import get_logger
from common_utils.input_quality import build_from_env
from .predictor import predict_batch
from .schema import InputSchema

def main(input_uri: str, output_uri: str) -> int:
    df = read_input(input_uri)
    InputSchema.validate(df)                    # Pandera — same as training
    quality = build_from_env().check_batch(df)  # optional edge check (C4)
    scores = predict_batch(df)                   # shared predict() — single source

    logger = get_logger()
    for row, score in zip(df.itertuples(), scores):
        logger.log_prediction(entity_id=row.entity_id, score=score, model_version=...)
    logger.flush()

    write_output(df.assign(score=scores), output_uri)
    return 0
```

### Step 3 — Scaffold `k8s/base/cronjob-batch.yaml` (AUTO)

Template:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: "{service}-batch"
spec:
  schedule: "0 2 * * *"              # 02:00 UTC nightly
  concurrencyPolicy: Forbid          # no overlapping runs
  startingDeadlineSeconds: 600
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 5
  jobTemplate:
    spec:
      backoffLimit: 1
      activeDeadlineSeconds: 3600    # 1h hard cap
      template:
        spec:
          serviceAccountName: "{service}-sa"
          restartPolicy: Never
          containers:
            - name: batch
              image: "{service}-predictor:{version}"
              command: ["python", "-m", "{service}.batch"]
              env:
                - { name: INPUT_URI, value: "gs://..." }
                - { name: OUTPUT_URI, value: "gs://..." }
              resources:
                requests: { cpu: "2", memory: "4Gi" }
                limits:   { cpu: "4", memory: "8Gi" }
              # PSS restricted (v1.8.1)
              securityContext:
                runAsNonRoot: true
                allowPrivilegeEscalation: false
                capabilities: { drop: [ALL] }
```

### Step 4 — Wire into kustomization (AUTO)

Add `cronjob-batch.yaml` to `k8s/base/kustomization.yaml::resources`.

### Step 5 — Quality gate — dry run (CONSULT)

Before enabling the schedule, run once on a bounded input:

```bash
kubectl create job --from=cronjob/{service}-batch {service}-batch-dryrun-$(date +%s)
kubectl logs job/{service}-batch-dryrun-... --follow
```

Verify:
- Row count matches expected
- Schema validation passed
- Scores distribution matches a reference sample
- Output file written with correct partitioning

### Step 6 — Enable schedule (STOP for prod)

Enabling the CronJob in production is a STOP operation:

```
[AGENT MODE: STOP]
Operation: Enable {service}-batch schedule in prod
Rationale: Will start scoring {N} entities nightly at 02:00 UTC. Output
will append to gs://{bucket}/{path}/ using prediction_id uniqueness.
Waiting for: Approval from {data-owner}
```

## Invariants

- **Shared predict code**: batch MUST call the exact same function as
  /predict. A re-implementation would cause training/batch skew.
- **Pandera validation**: same schema as training; drift goes through
  the same alert.
- **Prediction logger**: batch rows go into predictions_log just like
  live ones (closed-loop unaffected).
- **concurrencyPolicy: Forbid**: two overlapping runs would double-
  write and corrupt partitions.
- **Hard deadline**: `activeDeadlineSeconds` prevents a hung job from
  blocking tomorrow's cron.
- **PSS restricted**: the batch container is subject to the same
  securityContext as /predict (D-29).

## Related

- `.windsurf/rules/02-kubernetes.md` §CronJob patterns
- `.windsurf/rules/13-closed-loop-monitoring.md` — batch MUST log predictions
- `common_utils/input_quality.py` — optional edge check works for batch too
- ADR-006 — prediction logger contract (batch is just another caller)
- AGENTS.md §Engineering Calibration — CronJob, not Airflow, for 1-3 jobs
