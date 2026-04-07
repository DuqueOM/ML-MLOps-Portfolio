---
trigger: glob
globs: ".github/workflows/*.yml,.github/workflows/*.yaml"
---

# GitHub Actions Conventions

## Workflow Structure
- ci-mlops.yml: Lint + test + build for all 3 ML services (matrix strategy)
- ci-infra.yml: Terraform validate + plan on infra/ changes
- deploy-gcp.yml / deploy-aws.yml: Tag-triggered deployments
- drift-detection.yml: Daily cron for PSI-based drift check
- retrain-bankchurn.yml: Triggered by drift alert

## Standards
- Use matrix strategy for multi-service testing
- Pin action versions with full SHA, not just major tags
- Secrets via GitHub repository secrets — never hardcode
- Cache pip dependencies for faster CI runs
- Fail fast on lint errors before running expensive tests

## Testing in CI
- Generate lightweight test models — never use production models
- Run pytest with --cov and enforce minimum coverage (80%)
- Include both unit and integration tests
- Security scanning: gitleaks for secrets, safety/pip-audit for dependencies

## Docker in CI
- Multi-stage builds to minimize image size
- Tag images with git SHA + semver
- Push to Artifact Registry (GCP) or ECR (AWS)
- Scan images with Trivy before push

## Deployment
- Deploy only from tagged releases (vX.Y.Z)
- GKE: use Workload Identity for authentication
- EKS: use IRSA for authentication
- Run smoke tests after deploy before marking as successful
