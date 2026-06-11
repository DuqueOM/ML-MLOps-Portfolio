---
trigger: glob
globs: [".github/workflows/*.yml", ".github/workflows/*.yaml"]
description: GitHub Actions CI/CD patterns for ML services
---

# GitHub Actions Rules

## Workflow Organization

```
.github/workflows/
├── ci.yml                    # Lint, test, build — on push to main/develop
├── ci-infra.yml              # Terraform validate, tfsec, checkov — on infra/ changes
├── deploy-gcp.yml            # Deploy to GKE — on release tag or manual
├── deploy-aws.yml            # Deploy to EKS — on release tag or manual
├── drift-detection.yml       # PSI drift check — scheduled daily
└── retrain-{service}.yml     # Retrain triggered by drift — workflow_dispatch
```

## CI Workflow (`ci.yml`)

```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    steps:
      - flake8, black --check, isort --check
      - mypy (type checking)

  test:
    strategy:
      matrix:
        service: [ServiceA, ServiceB, ServiceC]
    steps:
      - pytest with coverage >= 90%
      - Upload coverage report

  build:
    needs: [lint, test]
    steps:
      - docker build --cache-from
      - trivy scan (image vulnerabilities)
      - docker push (only on main, not PRs)
```

## Infrastructure CI (`ci-infra.yml`)

Triggered on changes to `infra/` or `k8s/`:
```yaml
jobs:
  terraform-validate:
    strategy:
      matrix:
        cloud: [gcp, aws]
    steps:
      - terraform fmt -check
      - terraform validate
      - tfsec --format json
      - checkov -d infra/terraform/{cloud}
```

## Deploy Workflows

- Always use `kubectl apply -k k8s/overlays/{cloud}/`
- Always verify: `kubectl rollout status deployment/{service}`
- Always smoke test: `curl /health`
- Always use secrets from GitHub Secrets (never hardcoded)

## Drift Detection (`drift-detection.yml`)

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 02:00 UTC
  workflow_dispatch: {}

jobs:
  drift:
    strategy:
      matrix:
        service: [ServiceA, ServiceB, ServiceC]
    steps:
      - run: python src/{service}/monitoring/drift_detection.py
        continue-on-error: true
      - if: steps.drift.outcome == 'failure'
        uses: actions/github-script@v7
        # Creates GitHub Issue automatically
```

## Retraining Workflows

Triggered by `workflow_dispatch` (from drift detection or manual):
```yaml
on:
  workflow_dispatch:
    inputs:
      reason:
        description: 'Reason for retraining'
        required: true

jobs:
  retrain:
    steps:
      - Download fresh data
      - Execute Trainer.run() with Optuna
      - Evaluate quality gates
      - if ALL PASS: promote model + deploy
      - if ANY FAIL: open GitHub Issue
```

## Required Secrets — cloud-native delegation only (D-18)

**Never** put long-lived cloud credentials in GitHub Secrets. Use OIDC
federation: GitHub mints a short-lived token, the cloud provider
exchanges it for a scoped role/SA via Workload Identity Federation
(GCP) or IAM Identity Provider (AWS).

Document the OIDC binding in the workflow comments — not the keys:

```yaml
# Identity (OIDC, no static credentials):
# GCP   — Workload Identity Federation (provider + service account)
#         google-github-actions/auth@v2 with workload_identity_provider
# AWS   — IAM Identity Provider for token.actions.githubusercontent.com
#         aws-actions/configure-aws-credentials@v4 with role-to-assume
#
# Non-secret config (GitHub Variables, not Secrets):
# GCP_PROJECT_ID, GCP_REGION, AWS_REGION, AWS_ACCOUNT_ID
#
# Secrets (per Environment, never repo-wide):
# MLFLOW_TRACKING_URI    — MLflow server URL for the env
# STAGING_KUBECONFIG / PRODUCTION_KUBECONFIG — kubeconfig blobs
```

**STOP if you see** `GCP_SA_KEY`, `AWS_ACCESS_KEY_ID`, or any
`*_SECRET_ACCESS_KEY` in a workflow — that is a D-17/D-18 violation.
Replace with OIDC; document the migration in the same PR.

## Environment Promotion Gates (MANDATORY — D-26)

Deploys MUST chain through `dev → staging → prod` with human approval
at staging and prod via GitHub Environment Protection Rules:

```yaml
jobs:
  deploy-dev:
    uses: ./.github/workflows/deploy-common.yml
    with: { environment: dev, ... }    # no reviewers

  deploy-staging:
    needs: deploy-dev
    uses: ./.github/workflows/deploy-common.yml
    with: { environment: staging, ... }  # 1 reviewer via Env Protection

  deploy-prod:
    needs: deploy-staging
    if: startsWith(github.ref, 'refs/tags/v')
    uses: ./.github/workflows/deploy-common.yml
    with: { environment: production, ... }  # 2 reviewers + wait_timer
```

Environments to configure in `Settings → Environments`:

| Env name | Reviewers | Wait timer | Deployment branches |
|---|---|---|---|
| `{cloud}-dev` | 0 | 0 | all |
| `{cloud}-staging` | 1 | 0 | main + tags |
| `{cloud}-production` | 2 | 5 min | version tags only |

## Reusable Workflows (MANDATORY for multi-cloud deploys)

Deploy logic that is identical across clouds (build, push, smoke-test)
MUST be extracted into a `workflow_call` reusable workflow so a single
fix applies everywhere:

```yaml
# deploy-common.yml
on:
  workflow_call:
    inputs:
      cloud: { type: string, required: true }
      environment: { type: string, required: true }
      ...
```

See `docs/environment-promotion.md` for full setup.

## Rules

- NEVER store credentials in workflow files — use GitHub Secrets
- ALWAYS use **Environment secrets** (not repo-level) for
  cloud-credential scoping per dev/staging/prod (D-18 + D-26)
- ALWAYS pin action versions to a specific SHA (not `@main` or `@v3`)
- ALWAYS use `continue-on-error: true` for drift detection (drift does not block CI)
- ALWAYS run security scans (trivy for images, tfsec/checkov for Terraform)
- ALWAYS use matrix strategies for multi-service operations
- ALWAYS use `workflow_call` reusable workflows for shared deploy logic
- Production deploys MUST be gated on a version tag + 2 reviewers (D-26)
