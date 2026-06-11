---
description: Emergency rollback of a production ML service — pairs with the rollback skill (STOP-class operation)
---

# /rollback

Invoke when an incident is active and the decision has been made to
revert the previous deploy. For "is this even a real problem?" questions,
start with `/incident` instead — it triages before it acts.

Authorization: **STOP** for every executed step, even in dev. The agent
proposes; the human approves each destructive command.

## 1. Triage (15 min budget)

Before rollback, the agent MUST confirm:
- Is the alert a real user impact or a dashboard blip?
- Has Argo Rollouts already aborted the canary automatically?
- Is a targeted retrain (`/retrain`) a better fix?

If any answer changes the plan, abandon rollback and escalate to
`/incident` for the correct path.

## 2. Invoke skill

Load `.windsurf/skills/rollback/SKILL.md` and follow its 7 steps:

1. Confirm incident (evidence pack)
2. Identify target revision
3. Execute rollback — Argo Rollouts `abort` + `undo`
4. Revert MLflow model if artifact changed
5. Silence related alerts
6. Verify (error rate, latency, score distribution, readiness)
7. Open audit issue tagged `rollback,incident`

Each step emits a structured `[AGENT MODE: STOP]` signal with the exact
command and waits for the operator's confirmation.

## 3. Followups (5 business days)

- [ ] Blameless RCA in `docs/incidents/{date}-{service}.md`
- [ ] Regression test for the ROOT cause (not the symptom)
- [ ] Rollback skill update if this incident exposed a gap

## What this workflow is NOT

- It is NOT a "just undo whatever happened" button. It requires triage.
- It does NOT replace the postmortem — it triggers it.
- It does NOT handle data corruption (that is a different runbook:
  restore from backup + replay with idempotent ingesters).

## Related

- Skill: `rollback/SKILL.md`
- Workflow: `/incident` (triage before rollback)
- Workflow: `/retrain` (alternative to rollback if drift is the cause)
- ADR-008 (Champion/Challenger) — post-deploy rollback is governed, not automatic
