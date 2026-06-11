---
description: Incident workflow for leaked secrets — halt pipeline, rotate, audit, post-mortem
---

# /secret-breach Workflow

Triggers the `secret-breach-response` skill when a credential leak is detected or
reported. This is a **STOP-class operation** — agents must halt any running pipeline
and wait for human confirmation before proceeding with rotation.

## When to invoke

- Agent-SecurityAuditor finds a secret pattern in the repo or logs
- A developer realizes they committed a credential
- Gitleaks or Trivy in CI flags a secret
- An external alert (GitHub Secret Scanning, AWS IAM notification) fires
- Manual: "I leaked an API key", "Rotate the GCP service account for fraud-detector"

## Workflow phases (enforced order)

### Phase 1 — Halt & Classify (AUTO)
Agent emits STOP signal and classifies the secret type per the skill's table.
Produces `incidents/secret-breach-<timestamp>.md`.

### Phase 2 — Revoke (STOP, requires human)
Agent proposes the exact revocation command. Human executes.

### Phase 3 — Audit (AUTO)
Agent runs CloudTrail / Cloud Audit Logs / GitHub audit log queries and produces
the access-audit artifact.

### Phase 4 — Rotate (STOP, requires human)
Agent proposes the rotation + rollout plan. Human executes.

### Phase 5 — Clean git history (STOP — destructive)
Only if secret was in git and history rewrite is authorized. Otherwise skip.

### Phase 6 — Notify (AUTO)
Agent drafts notifications per org policy. Human sends.

### Phase 7 — Post-mortem (AUTO, 48h SLA)
Agent drafts the post-mortem issue with timeline, root cause, and controls.

## Anti-patterns during incident response

- ❌ Silent rotation without notification — destroys audit trail
- ❌ Reusing any part of the old credential as the new one
- ❌ Force-pushing to clean history on a public repo (secret already scraped)
- ❌ Closing the incident before the post-mortem is drafted
- ❌ Skipping phase 3 (access audit) — even if the exposure window seems short

## Related

- Skill: `secret-breach-response`
- Skill: `security-audit` (prevention)
- Rule: `.windsurf/rules/12-security-secrets.md`
- ADR: `ADR-005` (agent behavior + security)
