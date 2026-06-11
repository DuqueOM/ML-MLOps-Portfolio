---
name: rule-audit
description: Automated scan of a service/repo for compliance with AGENTS.md invariants D-01 through D-27 — produces a PASS/FAIL report with file:line evidence
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(grep:*)
  - Bash(rg:*)
  - Bash(python3:*)
  - Bash(conftest:*)
  - Bash(yq:*)
when_to_use: >
  Invoke before a major release, after merging a large PR, during incident
  post-mortems to check whether a missing invariant contributed, or on a
  schedule (e.g. monthly) to catch drift from the template. Also useful
  when onboarding a new service created outside the scaffolder.
argument-hint: "[service-path] [--subset probes|pdb|security|closed-loop|all]"
authorization_mode:
  scan: AUTO
  fix_findings: CONSULT
  patch_scaffolder: STOP
---

# Rule Audit — Compliance scan against AGENTS.md invariants

This skill is READ-ONLY. It does not modify code. When findings are
identified, the agent produces a remediation plan and waits for human
approval (CONSULT) before any fix. Template-scaffolder patches require
STOP because they affect all future services.

## When NOT to use this skill

- **Before running tests** — broken tests are a faster signal than
  structural audits.
- **During active incidents** — use `/incident` or `/rollback` first.
  Come back to audit in the post-mortem.
- **On third-party code** — this skill is scoped to the template's own
  conventions.

## Invariant catalogue (D-01 → D-27)

The checks below map one-to-one onto the AGENTS.md anti-pattern table.
The agent runs the matching query for each ID and records PASS/FAIL +
evidence (file:line or metric) per service.

### Serving (D-01 → D-05)

| ID | Check | Command |
|----|-------|---------|
| D-01 | `uvicorn --workers N` where N > 1 | `rg -n "uvicorn.*--workers\s+[2-9]" --glob "**/Dockerfile*" --glob "**/*.sh"` |
| D-02 | HPA uses memory metric | `yq '.spec.metrics[] \| select(.resource.name == "memory")' k8s/**/hpa.yaml` |
| D-03 | `model.predict(` inside an `async def` without `run_in_executor` | `rg -n "async def.*:" -A 30 app/ \| rg "model\.(predict\|predict_proba)\("` |
| D-04 | `shap.TreeExplainer` used with stacking/ensemble wrapper | `rg -n "TreeExplainer" app/` |
| D-05 | `==` in requirements.txt for ML packages | `rg -n "^(numpy\|scipy\|scikit-learn\|pandas\|xgboost\|lightgbm)==" requirements*.txt` |

### Infrastructure + Quality (D-06 → D-12)

| ID | Check |
|----|-------|
| D-06 | Any metric in `artifacts/metrics.json` ≥ 0.99 — requires ADR |
| D-07 | Fairness DIR < 0.80 or missing |
| D-08 | PSI CronJob reports but no alert routes configured |
| D-09 | Drift CronJob last_run > 48h → heartbeat missing |
| D-10 | `terraform.tfstate*` tracked in git |
| D-11 | Model artifact present in Dockerfile (`COPY *.joblib` / `*.pkl`) |
| D-12 | Promotion pipeline missing a quality-gate script |

### Data + EDA (D-13 → D-16)

| ID | Check |
|----|-------|
| D-13 | EDA notebooks writing under `data/raw/` or `data/processed/` |
| D-14 | Pandera schemas missing `Check.in_range` derived from EDA |
| D-15 | canonical `baseline_distributions.parquet` missing or never regenerated |
| D-16 | canonical `feature_catalog.yaml` without `rationale:` on every transform |

### Security (D-17 → D-19)

| ID | Check |
|----|-------|
| D-17 | `os.environ[.*API_KEY|SECRET|TOKEN|PASSWORD]` outside tests |
| D-18 | `AWS_ACCESS_KEY_ID` or raw JSON GCP SA key in committed files |
| D-19 | Deploy workflow missing `cosign sign` + `syft` step |

### Closed-loop (D-20 → D-22)

| ID | Check |
|----|-------|
| D-20 | `PredictionEvent(` without `entity_id=` or `prediction_id=` |
| D-21 | `log_prediction(` called synchronously in `async def` endpoint |
| D-22 | Missing `except Exception` + `prediction_log_errors_total` metric |

### Lifecycle + Operations (D-23 → D-27 — v1.7.1)

| ID | Check | Automated? |
|----|-------|-----------|
| D-23 | Liveness and readiness probes share `httpGet.path` | yes (Rego) |
| D-24 | `KernelExplainer(...)` constructed per request (not cached at startup) | `rg -n "KernelExplainer\(" app/` |
| D-25 | `terminationGracePeriodSeconds` missing OR <= uvicorn `--timeout-graceful-shutdown` | yes (Rego) |
| D-26 | `deploy-*.yml` missing the 3-env chain (dev/staging/prod environments) | grep |
| D-27 | Deployment without matching `PodDisruptionBudget` | yes (Rego) |

## Execution flow

### Step 1 — Scope (AUTO, 30 s)

Agent identifies services to audit:

```bash
find . -maxdepth 3 -type d -name "k8s" -prune | xargs dirname
# → list of service roots
```

If the user specifies `[service-path]`, restrict to that directory.

### Step 2 — Static invariants (AUTO, 2 min)

For each invariant in the catalogue, run the command, capture hits, and
write one row to `ops/rule_audit.jsonl`:

```json
{"service":"fraud_detector","invariant":"D-03","status":"FAIL","evidence":"app/main.py:142: async def predict(...): prediction = model.predict(X)","timestamp":"..."}
```

### Step 3 — Structural invariants via conftest (AUTO, 1 min)

The Rego policies in `tests/infra/policies/` cover D-23/D-25/D-27 and
several D-02 / D-11 checks. Run:

```bash
conftest test --policy tests/infra/policies/ k8s/base/ k8s/overlays/<env>/ 2>&1
```

Record FAIL/WARN as additional rows.

### Step 4 — Produce summary (AUTO, 30 s)

The agent emits:

```
# Rule Audit — {service-name} — {date}

Summary: 23 PASS / 2 FAIL / 1 WARN / 1 SKIPPED

## Failures (require CONSULT)
- D-04 app/explain.py:18 — uses shap.TreeExplainer with a StackingClassifier
  Fix: swap to KernelExplainer via predict_proba_wrapper (rule 04a).
- D-26 .github/workflows/deploy-gcp.yml — single 'production-gcp' environment
  Fix: adopt dev→staging→prod chain (docs/environment-promotion.md).

## Warnings
- D-25 k8s/base/deployment.yaml:45 — terminationGracePeriodSeconds (30)
  equals uvicorn --timeout-graceful-shutdown (30). Best practice: strictly
  greater (termGrace > uvicorn timeout).

## Skipped
- D-06 — no metrics.json available in this service.
```

### Step 5 — Remediation plan (CONSULT)

For each FAIL the agent proposes the MINIMAL patch and waits for
operator approval. No code is written until the operator confirms.

### Step 6 — Audit trail (AUTO)

Every run appends an `AuditEntry` tagged `operation: rule_audit` to
`ops/audit.jsonl` via `common_utils.agent_context.AuditLog`, carrying
the summary counts. A run with FAILs sets `result: halted` to flag the
issue in the ops log.

## Subset flag

For large repos the agent can restrict scope:

- `--subset probes` → D-23, D-25 only
- `--subset pdb` → D-27 only
- `--subset security` → D-17, D-18, D-19
- `--subset closed-loop` → D-20, D-21, D-22, D-24
- `--subset all` (default) → every invariant

## What this skill is NOT

- NOT a replacement for unit tests or integration tests (different signal)
- NOT a code formatter (black/isort handle that)
- NOT a security scanner (trivy/gitleaks handle that — this skill CHECKS
  that they are wired, not the findings themselves)
- NOT a migration tool — it identifies gaps but proposes patches as
  CONSULT, letting the human decide whether each fix is worth it

## Invariants

- Audit is READ-ONLY by default. The agent MUST NOT write fixes in AUTO.
- Every FAIL is evidence-backed (`file:line` or metric name) — never
  "might be missing".
- Subset flag is idempotent: running `--subset probes` and then `--subset
  all` produces a superset of the first run.
- The audit log entry is ALWAYS created, even when every check passes
  (historical record).

## Related

- AGENTS.md anti-pattern table (D-01..D-27)
- `.windsurf/skills/security-audit/SKILL.md` — deeper security scan
- `.windsurf/skills/debug-ml-inference/SKILL.md` — uses D-01..D-27 as
  diagnostic checklist
- `common_utils/agent_context.py::AuditLog` — audit trail integration
