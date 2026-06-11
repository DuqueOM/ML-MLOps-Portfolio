---
name: secret-breach-response
description: Incident playbook for leaked secrets — detect, revoke, rotate, audit access, notify, post-mortem
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(gitleaks:*)
  - Bash(git:*)
  - Bash(aws:*)
  - Bash(gcloud:*)
  - Bash(kubectl:*)
  - Bash(gh:*)
when_to_use: >
  Use IMMEDIATELY when a credential is found in the repo, logs, or an artifact.
  Triggered automatically by Agent-SecurityAuditor on any secret scan finding.
  Manual invocation: 'I leaked an API key', 'secret in git history', 'rotate credentials'.
argument-hint: "<secret-type> <exposure-scope>"
arguments:
  - secret-type
  - exposure-scope
authorization_mode:
  detect: AUTO          # read-only scan
  revoke_credential: STOP   # destructive — human must confirm rotation path
  clean_git_history: STOP   # history rewrite — human must approve
  rotate_secret: STOP   # secret rotation requires out-of-band verification
---

# Secret Breach Response

## 🚨 STOP EVERYTHING FIRST

If you are the agent:
1. **Halt any running pipeline step** (CI deploy, K8s apply, image push)
2. **Emit**:
   ```
   [AGENT MODE: STOP]
   Operation: Secret breach response
   Finding: <secret-type> exposed in <location>
   Waiting for: Human confirmation to proceed with rotation
   ```
3. **Do NOT attempt to rewrite git history or rotate credentials without explicit
   authorization.** Silent rotation destroys the audit trail.

## Phase 1 — Detect & Classify (AUTO)

Classify the exposed credential:

| Type | Example pattern | Rotation urgency |
|------|----------------|------------------|
| AWS access key | `AKIA[0-9A-Z]{16}` | **P1** — minutes |
| GCP service account JSON | `"private_key": "-----BEGIN PRIVATE KEY-----` | **P1** — minutes |
| GitHub PAT | `ghp_[A-Za-z0-9]{36}` | **P1** — minutes |
| Database password | (variable) | **P2** — 1h |
| Internal API key | (variable) | **P2** — 1h |
| Signing key | (variable) | **P1** — minutes |
| Slack/webhook URL | `hooks.slack.com/services/...` | **P3** — 24h |

Determine exposure scope:
- [ ] Where was the leak? (git log, CI logs, image layer, Slack message)
- [ ] How long has it been exposed? (git commit timestamp, log retention)
- [ ] Was it pushed to a public remote? (`git log origin/main`)
- [ ] Did any external CI/CD run with the credential? (check workflow history)

Output classification to `incidents/secret-breach-<YYYY-MM-DD-HHMM>.md`.

## Phase 2 — Revoke Credential (STOP before proceeding)

**This phase requires human confirmation.** Agent proposes, human executes.

### AWS
```bash
# Delete the access key at the root of the tree
aws iam delete-access-key --access-key-id <AKIA...> --user-name <username>
# OR disable it first if investigation needed:
aws iam update-access-key --access-key-id <AKIA...> --status Inactive --user-name <username>
```

### GCP
```bash
# Delete the service account key
gcloud iam service-accounts keys delete <KEY_ID> \
  --iam-account=<service-account-email>
```

### GitHub
1. https://github.com/settings/tokens → revoke the PAT
2. If it was a fine-grained PAT, check which repos had access

### Database/internal
- Rotate per the service's own runbook
- Never use the same password for the replacement — generate fresh

## Phase 3 — Audit Access Window (AUTO)

Determine what the leaked credential could have accessed during its exposure:

### AWS
```bash
# CloudTrail lookup for this access key
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=<AKIA...> \
  --start-time <exposure-start> --end-time <exposure-end>
```

### GCP
```bash
# Cloud Audit Logs
gcloud logging read 'protoPayload.authenticationInfo.serviceAccountKeyName="<key-id>"' \
  --freshness=<exposure-duration>
```

### GitHub
- Repository audit log: Settings → Audit log
- Filter by the PAT user

Save to `incidents/secret-breach-<timestamp>/access-audit.md`.

## Phase 4 — Rotate to New Secret (STOP before proceeding)

Generate replacement via the appropriate secret manager (D-18):

### AWS
```bash
# Update the secret in Secrets Manager (not create a new one — preserves ARN)
aws secretsmanager update-secret \
  --secret-id <service-namespace>/<key> \
  --secret-string <new-value>
```

### GCP
```bash
# Add a new version to the existing secret (old version disabled)
echo -n "<new-value>" | gcloud secrets versions add <secret-name> --data-file=-
gcloud secrets versions disable <old-version> --secret=<secret-name>
```

Restart services that consume the secret (they pick up new version on next pod start):
```bash
kubectl rollout restart deployment/<service> -n <namespace>
```

## Phase 5 — Clean Git History (STOP — destructive)

**If the secret was committed to git:**

```bash
# Option A: git filter-repo (preferred, requires install)
git filter-repo --invert-paths --path <file-with-secret>

# Option B: BFG (alternative)
bfg --delete-files <file-with-secret>
```

**Consequences**: rewrites history. All collaborators must re-clone. All
open PRs must be rebased. Get team approval first.

**Do NOT proceed if the secret was ever in a public repo** — assume it was
scraped by bots within seconds. Rotation (phase 4) is the only mitigation.

## Phase 6 — Notify (AUTO within org policy)

- [ ] Security team (Slack #security or similar)
- [ ] Platform team (Slack #platform)
- [ ] If customer data accessed: legal / DPO
- [ ] Update `incidents/secret-breach-<timestamp>.md` with notification log

## Phase 7 — Post-Mortem (AUTO, async)

Within 48h, open a post-mortem issue with:
- **Timeline**: detection, revocation, rotation, notification
- **Root cause**: why did the secret reach the code / log / artifact?
- **Controls that failed**: why didn't gitleaks / pre-commit / CI catch it?
- **Controls to add**: what prevents recurrence?
- **Action items** with owners and deadlines

Link the post-mortem to any new ADRs and to `SECURITY.md` updates.

## Checklist before closing

- [ ] Credential revoked (verified via API call returning "access denied")
- [ ] New secret deployed and services healthy
- [ ] Access audit completed and no suspicious activity found (or escalated)
- [ ] Git history cleaned or rotation is the final control
- [ ] Stakeholders notified per policy
- [ ] Post-mortem drafted within 48h
- [ ] At least one control added to prevent recurrence

## Related

- Rule: `.windsurf/rules/12-security-secrets.md` (D-17, D-18, D-19)
- Skill: `security-audit` (detection)
- Workflow: `/secret-breach` (entry point)
- ADR: `ADR-005` (agent behavior + security)
