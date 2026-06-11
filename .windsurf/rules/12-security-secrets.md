---
trigger: always_on
description: Security invariants — secret management, credential hygiene, least-privilege
---

# Security & Secrets Rules (always_on)

Applies to **every file edit and every command**. These invariants supersede any
convenience shortcut.

## Non-negotiable invariants

### D-17 — No hardcoded credentials
- **Never** write literal credentials, tokens, API keys, or passwords in any file
- **Never** use `os.environ["API_KEY"]` in production code paths — always go through
  the `common_utils/secrets.py` loader which resolves per environment
- **Never** commit `.env`, `.env.local`, `terraform.tfstate`, or any file matching
  `.gitleaks.toml` patterns

### D-18 — Cloud-native credential delegation only
- **AWS**: IRSA (IAM Roles for Service Accounts) — no `AWS_ACCESS_KEY_ID` in code or env
- **GCP**: Workload Identity — no `GOOGLE_APPLICATION_CREDENTIALS` JSON keys
- Static credentials are acceptable ONLY in local development via `.env.local` (never committed)
- Any `AWS_SECRET_ACCESS_KEY` or GCP service account JSON in committed files → STOP

### D-19 — Image verification before deploy
- Production deploys MUST verify image signatures via Cosign
- Unsigned images MUST be rejected by Kyverno admission controller in prod namespace
- Missing SBOM for prod image → block deploy

## Agent Behavior on Secrets

### Before any commit (AUTO)
Run in sequence:
1. `gitleaks detect --no-git --source=. --redact`
2. `grep -rEI "AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|ghp_[A-Za-z0-9]{36}"` over changed files
3. `grep -E "os\.environ\[.(API_KEY|SECRET|TOKEN|PASSWORD)" --include="*.py"` must be empty
   (use `from common_utils.secrets import get_secret` instead)

If any step finds a hit → **STOP**. Chain to `/secret-breach`.

### When editing Python modules
- Prefer `from common_utils.secrets import get_secret` over direct env reads
- Never `print()` or `logger.info()` a value that might be a secret
- Use `logger.debug(..., extra={"redact": ["api_key", "token"]})` if structured
- Exception traces on production paths must filter PII via log middleware

### When editing K8s manifests
- Secrets MUST be mounted via `envFrom.secretRef` or `volumeMounts`, never literals
- ServiceAccount must have IRSA annotation (AWS) or WI annotation (GCP)
- `image:` references without a digest (`@sha256:...`) are allowed in dev only
- In staging/prod overlays, all image references MUST pin to digests after signing

### When editing Terraform
- No `default = "sk_live_..."` or similar literal values in `variables.tf`
- Use `data "aws_secretsmanager_secret_version"` or `data "google_secret_manager_secret_version"`
- Remote state backend must use encryption-at-rest
- `*.tfvars` files with secrets must never be committed (`.gitignore` enforced)

## Secret Rotation

- Rotation is a **STOP** operation — requires human authorization
- Procedure codified in `.windsurf/skills/secret-breach-response/SKILL.md`
- Workflow: `/secret-breach`
- Never attempt silent rotation, even if obvious. Audit trail is mandatory.

## Environment Separation

| Environment | Secret store | Delivery mechanism |
|-------------|--------------|--------------------|
| Local dev | `.env.local` (gitignored) | dotenv loader |
| CI | GitHub Secrets | workflow env |
| Staging | AWS Secrets Manager / GCP Secret Manager | IRSA/WI + CSI driver or env via operator |
| Production | AWS Secrets Manager / GCP Secret Manager | IRSA/WI + CSI driver (required for immutability) |

Agents must never propose "copy this secret from staging to prod" — each environment
has its own secret. Rotation cadence is per environment.

## What this rule does NOT cover

- **HashiCorp Vault**: deferred by ADR-001 (revisit trigger: IRSA/WI insufficient)
- **SLSA Level 3+**: requires hermetic builds — out of scope for template
- **Compliance programs (SOC2/HIPAA)**: organizational, not template (ADR-001)

This rule covers the 90% case: cloud-native credential delegation with defense-in-depth.
