---
name: security-audit
description: Pre-build and pre-deploy security audit — secret scans, IAM least-privilege, IRSA/WI verification, image signing, SBOM
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(gitleaks:*)
  - Bash(trivy:*)
  - Bash(cosign:*)
  - Bash(syft:*)
  - Bash(kubectl:*)
  - Bash(aws:*)
  - Bash(gcloud:*)
when_to_use: >
  Use BEFORE every build or deploy. Triggered automatically by Agent-DockerBuilder
  (pre-build) and Agent-K8sBuilder (pre-deploy). Also on demand: 'audit security
  of fraud-detector', 'check for secrets', 'verify image signatures'.
argument-hint: "<service-path> [environment]"
arguments:
  - service-path
  - environment
authorization_mode:
  scan: AUTO       # read-only, no side effects
  block_build: AUTO  # blocking the pipeline is always authorized when findings are critical
  rotate_secret: STOP  # never auto-rotate; chain to /secret-breach
---

# Security Audit Skill

Agent-SecurityAuditor runs this skill **before every build and deploy**. Blocks the
pipeline if any critical finding is detected.

## What this skill checks

### 1. Secret scanning (blocker)
- `gitleaks detect --no-git --source=<service-path> --redact --config=.gitleaks.toml`
- Scan last 50 commits: `gitleaks detect --source=<repo> --log-opts="-50"`
- Scan env files: `.env`, `.env.local`, `.envrc` — must not be committed
- Scan Terraform state: `terraform.tfstate` must NOT exist in repo (D-10)

**Block pipeline if any finding.** Chain to `/secret-breach` for rotation.

### 2. Dependency vulnerabilities (blocker for HIGH/CRITICAL)
- `trivy fs --severity HIGH,CRITICAL <service-path>`
- Check `requirements.txt` for known CVEs
- Fail on any CVE with fix available (patch is mandatory)

### 3. Container image scanning (blocker for CRITICAL)
- `trivy image --severity HIGH,CRITICAL <image-tag>`
- Verify base image has security updates
- Check Dockerfile for anti-patterns (running as root, curl|bash, etc.)

### 4. IAM least-privilege (blocker)
- Verify service uses IRSA (AWS) or Workload Identity (GCP) — not static credentials
- `grep -rE "AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY" --include="*.py" --include="*.yaml" <service-path>`
  must return zero hardcoded values
- K8s ServiceAccount must have `annotations.iam.gke.io/gcp-service-account` (GCP) or
  `annotations.eks.amazonaws.com/role-arn` (AWS)
- IAM policy must have `Resource` specified (not `"*"`) and `Condition` where applicable

### 5. Image signing (required for prod) — keyless OIDC (D-19)
- The template uses **keyless Cosign** (no static public key). Verify via:
  ```bash
  cosign verify <image-ref> \
    --certificate-identity-regexp 'https://github.com/ORG/REPO/.github/workflows/ci.yml@.*' \
    --certificate-oidc-issuer https://token.actions.githubusercontent.com
  ```
- Unsigned images are blocked by Kyverno admission controller in prod namespace
  (see `templates/k8s/policies/kyverno-image-verification.yaml`).
- Missing signature → block deploy, chain to CI `sign_image` step.
- Do NOT use `cosign verify --key <pub-key>` — that pattern requires
  long-lived key material (D-17/D-18 violation) and is not what the
  Kyverno ClusterPolicy in this template expects.

### 6. SBOM generation (required for prod)
- `syft <image-tag> -o cyclonedx-json > sbom.json`
- SBOM attached as image attestation: `cosign attest --predicate sbom.json --type cyclonedx <image-tag>`
- Required for SLSA Level 2+ compliance (see ADR-005)

### 7. Network policies (warning)
- K8s NetworkPolicy must exist for each service namespace
- Default-deny posture preferred
- Missing → warn, require engineer to explain in PR

### 8. Debug/logging hygiene
- `grep -rE "print\(.*(password|token|secret|key)" <service-path>` must return zero
- `/predict` endpoint must NOT log request bodies in production
- Stack traces with sensitive data must be filtered (use `logger.exception` with care)

## When to invoke

| Caller | When | Mode |
|--------|------|------|
| Agent-DockerBuilder | Pre-build (before `docker build`) | AUTO — block if findings |
| Agent-K8sBuilder | Pre-deploy (before `kubectl apply`) | AUTO — block if findings |
| Agent-CICDBuilder | On every PR via CI workflow | AUTO — comment on PR |
| CI scheduled (weekly) | Full audit across all services | AUTO — open issue if new findings |
| Human-triggered | `audit security of <service>` | AUTO — report to console |

## Outputs

Every run produces:
- `eda/artifacts/security_audit_<timestamp>.json` — structured findings
- GitHub Action job summary (when in CI)
- Exit code: `0` = clean, `1` = findings, `2` = tool error

## Failure handling

If findings are detected:

1. **Output the AGENT MODE signal** (per AGENTS.md):
   ```
   [AGENT MODE: STOP — BLOCKED BY SECURITY AUDIT]
   Operation: {build|deploy} of {service}
   Findings: <count> critical, <count> high
   Details: <path to audit report>
   Waiting for: Engineer resolution
   ```

2. **Do NOT propose a workaround.** Skipping security findings requires:
   - An ADR documenting the decision
   - Explicit override via `--skip-security-audit=<finding-id>` (engineer must review)
   - Mitigation plan tracked as an issue

3. **Chain to `/secret-breach`** if findings include any secret leak.

## Related

- Rule: `.windsurf/rules/12-security-secrets.md` (always_on)
- Skill: `secret-breach-response` (activated on secret findings)
- Workflow: `/secret-breach`
- ADR: `ADR-005` (agent behavior & security)
- Anti-patterns: D-10 (Terraform state), D-17 (secrets in code), D-18 (static AWS keys), D-19 (unsigned images in prod)
