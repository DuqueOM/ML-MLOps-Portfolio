---
trigger: glob
globs:
  - "**/prediction_logger.py"
  - "**/ground_truth.py"
  - "**/performance_monitor.py"
  - "**/champion_challenger.py"
  - "**/monitoring/**/*.py"
  - "**/app/fastapi_app.py"
  - "**/app/main.py"
  - "**/app/schemas.py"
  - "**/configs/slices.yaml"
  - "**/configs/ground_truth_source.yaml"
  - "**/configs/champion_challenger.yaml"
  - "**/k8s/base/cronjob-performance.yaml"
  - "**/k8s/base/performance-prometheusrule.yaml"
description: Closed-loop monitoring invariants — prediction logging, ground truth, sliced performance, champion/challenger
---

# Closed-Loop Monitoring Rules (ADR-006 / ADR-007 / ADR-008)

Applies to every file that touches prediction logging, ground-truth
ingestion, sliced performance monitoring, or champion/challenger comparison.
These invariants exist because concept drift is silent without them.

## Non-negotiable invariants

### D-20 — Identity + lineage on every logged prediction
- Every prediction MUST carry a unique `prediction_id` (UUID hex) and a stable
  business `entity_id`. The `entity_id` is the JOIN key with delayed labels.
- `model_version` MUST be present on every logged event. Without it, drift
  analysis cannot attribute performance to a specific deploy.
- The `PredictionRequest` schema MUST expose `entity_id` as a required field.
- The response MUST include the `prediction_id` so clients can reference it
  later (customer support, audit, label matching).
- Never generate `entity_id` server-side from features — it must be a stable
  business key (customer_id, transaction_id, session_id).

### D-21 — Prediction logging is fire-and-forget
- `log_prediction()` MUST return immediately after enqueueing. It MUST NOT
  perform synchronous I/O on the hot path.
- The handler MUST NOT `await` a network call to the log backend directly;
  instead the logger buffers in memory and flushes in a background task.
- Backends are sync; they execute via `run_in_executor(None, ...)` so the
  event loop stays responsive (same principle as D-03 for inference).
- The buffer MUST drain on `FastAPI.lifespan` shutdown (`await close()`).

### D-22 — Observability failures never break serving
- `log_prediction()` MUST swallow exceptions. Enqueue errors increment the
  Prometheus counter `prediction_log_errors_total` but MUST NOT propagate.
- Flush errors are logged at WARNING and counted — the handler NEVER sees
  them. The client ALWAYS gets its response.
- Health of closed-loop monitoring is observed through the counter, not
  through HTTP 5xx. An alert on `rate(prediction_log_errors_total[15m]) /
  rate(prediction_log_total[15m]) > 0.05` surfaces degraded observability
  without impacting SLO.

## Slicing contract (ADR-007)

- The `slice_values` field in `PredictionRequest` accepts a dict of
  `{slice_name: slice_value}` pairs referenced in `configs/slices.yaml`.
- Cardinality MUST be bounded. Unknown slice names are silently ignored by
  the monitor. Unbounded slices (free-text fields) are FORBIDDEN — they
  explode Prometheus label cardinality.
- Slice values MUST be low-cardinality categoricals (country, channel,
  segment) or numeric features bucketed via `bins:` in `slices.yaml`.
- Per-slice metrics are only computed when `sample_size >= min_samples_per_slice`
  (default 50). Below that the slice is reported as `insufficient_data`.

## Ground-truth contract (ADR-006)

- The function `fetch_labels_from_source()` is a USER-REPLACED stub. The CSV
  implementation is ONLY for local development and tests.
- Return rows MUST have non-null `entity_id` and `true_value`, and a
  `label_ts` that is the moment the ground truth became KNOWN (not the
  moment the event happened).
- Labels are joined with predictions where `label_ts >= prediction_ts`
  (causality). Reverse-order matches are dropped.
- Ingester writes are idempotent via daily partition overwrites; never
  mutate an existing partition's rows in place.

## Champion/Challenger contract (ADR-008)

- C/C is a STOP-class operation. The CI workflow MUST be the only automated
  path to promotion, and its result MUST be posted to the Actions step
  summary for audit.
- The statistical test set is McNemar (exact binomial) AND bootstrap ΔAUC
  95% CI. Single-test decisions are FORBIDDEN — both must align.
- The decision is tri-state (promote/keep/block). A challenger that is not
  significantly better is kept, NOT promoted. A challenger that is worse
  than the non-inferiority margin is blocked and an issue is opened.
- The configured margins (`non_inferiority_margin`, `superiority_margin`)
  are domain-dependent. Changing them requires an ADR explaining the
  business rationale.

## Agent behavior on closed-loop files

### Before editing fastapi_app.py or main.py (AUTO)
- Verify D-21/D-22 are preserved: no `await` on backend I/O, no exceptions
  leak from the log path.

### Before editing prediction_logger.py (CONSULT)
- Changes to buffering or backend semantics affect every service that
  adopts the template. Propose a diff with reasoning before applying.

### Before editing champion_challenger.py or its config (STOP)
- Margins and alpha are governance parameters. An ADR addendum MUST
  accompany any change, even for dev environments (drift between envs
  makes the gate meaningless).

### When adding a new backend (CONSULT)
- New backends MUST implement `write_batch()` and `health_check()`.
- Add a unit test exercising `write_batch` on a real (or mocked) store.
- Document the env vars in `.env.example` under the same section.

## What this rule does NOT cover

- **Streaming ingestion** (Kafka/Bytewax): deferred by ADR-006 (revisit
  trigger: >100M predictions/day or sub-minute label latency requirements).
- **Full feature store** (Feast): out of scope per ADR-003.
- **Shadow mode with Istio traffic mirroring**: noted in ADR-008 as future
  work behind an ADR trigger ("multi-tenant high-stakes deploys").

These are legitimate patterns but outside the template's calibrated scope
(1–5 classical ML models, single team).
