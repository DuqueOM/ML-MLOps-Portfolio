---
name: release-checklist
description: Full release checklist for multi-cloud deployment (GCP + AWS)
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(git:*)
  - Bash(docker:*)
  - Bash(kubectl:*)
  - Bash(gh:*)
  - Bash(curl:*)
when_to_use: >
  Use when preparing a version release to production across GCP and AWS.
  Examples: 'release v1.2.0', 'prepare production release', 'deploy new version',
  'multi-cloud release'
argument-hint: "<version-tag> [service-name]"
arguments:
  - version-tag
authorization_mode:
  pre_flight_checks: AUTO        # all checks read-only
  build_images: AUTO             # CI-driven; reversible via tag deletion
  deploy_dev: AUTO               # GitHub Environment dev has no Protection Rules
  deploy_staging: CONSULT        # 1 reviewer per ADR-011
  deploy_production: STOP        # 2 reviewers + wait_timer + protected_tags
  rollback_invocation: STOP      # chains to rollback skill (also STOP)
  escalation_triggers:
    - quality_gate_fail: STOP          # any failing gate halts the chain
    - sbom_missing: STOP               # D-30 — no unsigned/un-attested image
    - kyverno_policy_fail: STOP        # admission-time failure
    - disagreement_in_metrics: CONSULT # primary up, secondary down → human reads
---

# Release Checklist

## Pre-Release Verification

### Code Quality
- [ ] All CI checks passing (lint, test, build)
- [ ] Coverage >= 90% lines, >= 80% branches
- [ ] No TODO/FIXME items in critical paths
- [ ] Type hints on all public functions

### Model Quality
- [ ] Quality gates passing for all services
- [ ] Fairness checks passed (DIR >= 0.80)
- [ ] SHAP consistency verified
- [ ] No data leakage detected

### Infrastructure
- [ ] Terraform plan shows no unexpected changes
- [ ] tfsec/checkov clean (no HIGH/CRITICAL findings)
- [ ] Secrets rotated if approaching expiry

### Documentation
- [ ] ADRs up to date for any new decisions
- [ ] Service READMEs updated with new metrics
- [ ] AGENTS.md updated if new invariants
- [ ] CHANGELOG.md updated

## Version Tagging

```bash
# Update version
export VERSION=v{MAJOR}.{MINOR}.{PATCH}

# Tag and push
git tag -a ${VERSION} -m "Release ${VERSION}: {summary}"
git push origin ${VERSION}
```

## Build and Push Images

```bash
# For each service
for SERVICE in service-a service-b service-c; do
  # GCP Artifact Registry
  docker build -t ${GCP_REGISTRY}/${SERVICE}:${VERSION} ${SERVICE}/
  docker push ${GCP_REGISTRY}/${SERVICE}:${VERSION}

  # AWS ECR
  docker build -t ${AWS_REGISTRY}/${SERVICE}:${VERSION} ${SERVICE}/
  docker push ${AWS_REGISTRY}/${SERVICE}:${VERSION}
done
```

## Deploy to GCP

```bash
# Update overlays (production environment for release)
# k8s/overlays/gcp-prod/kustomization.yaml → newTag: ${VERSION} (CI replaces with @sha256 digest)
kubectl apply -k k8s/overlays/gcp-prod/
kubectl rollout status deployment --all -n {namespace} --timeout=300s
```

## Deploy to AWS

```bash
# Update overlays (production environment for release)
# k8s/overlays/aws-prod/kustomization.yaml → newTag: ${VERSION} (CI replaces with @sha256 digest)
kubectl apply -k k8s/overlays/aws-prod/
kubectl rollout status deployment --all -n {namespace} --timeout=300s
```

## Post-Deploy Verification

### Both Clouds
- [ ] `/health` returning 200 on all services
- [ ] `/predict` returning valid predictions
- [ ] `/metrics` being scraped by Prometheus
- [ ] Grafana dashboards showing new version
- [ ] No P1/P2 alerts in AlertManager
- [ ] HPA functioning (correct replica counts)

### Smoke Tests

Smoke tests run **inside** the deploy chain via `deploy-common.yml`
(canonical SSOT). Each environment job invokes the smoke test step
against the freshly-deployed pods; failure halts the chain.

```bash
# Manual invocation (one service, one cloud) for debugging:
kubectl --context=$CLUSTER -n $NAMESPACE port-forward svc/$SERVICE 8000:8000 &
curl -fsS http://localhost:8000/health    # liveness
curl -fsS http://localhost:8000/ready     # readiness (gates traffic)
curl -fsS -X POST http://localhost:8000/predict \
     -H 'content-type: application/json' \
     -d "$(cat tests/fixtures/smoke_payload.json)"
kill %1
```

For a multi-service / multi-cloud sweep, drive the loop from a
runbook page or a CI workflow-dispatch — the template does not ship
a `scripts/smoke_test.py` script (would compete with `deploy-common.yml`
as SSOT).

## Rollback Plan

If any issue detected within 30 minutes:
```bash
# Rollback all services
kubectl rollout undo deployment --all -n {namespace}
kubectl rollout status deployment --all -n {namespace}
```

## Post-Release

- [ ] Update CHANGELOG.md with release notes
- [ ] Close related GitHub Issues
- [ ] Update cost projections if resource changes
- [ ] Schedule next drift detection run

## Success criteria

The release is complete when ALL of the following hold across BOTH clouds:

- [ ] All quality gates green (CI test+lint+type, security audit, contract
      snapshot, fairness DIR >= 0.80)
- [ ] Image signed with Cosign keyless and SBOM attached as attestation
      (D-19, D-30) — verified by Kyverno admission policy at deploy time
- [ ] Six environment deploys succeeded in order:
      gcp-dev → gcp-staging → gcp-prod ; aws-dev → aws-staging → aws-prod
- [ ] Smoke tests pass on all 6 (`/health` 200, `/ready` 200, `/predict`
      returns valid response, `/metrics` scraped by Prometheus)
- [ ] Production environment Protection Rules honored:
      2 reviewers + wait_timer: 5 + protected_tags only (ADR-011)
- [ ] CHANGELOG.md updated and `releases/v<version>.md` published
- [ ] Per-environment audit entry in `ops/audit.jsonl` with operation
      = `release_deploy`, result = `success` for each cloud × env pair

## Failure modes — must STOP before completion

If any of these signals appears, the release is NOT complete and must
be either rolled back via `/rollback` (STOP) or paused for human review:

- Quality gate fail at any stage
- Cosign verification fail at admission (Kyverno blocks the pod)
- SBOM attestation older than 90 days (rule 14 §retention)
- Smoke test 5xx rate > 0.5% in any environment for > 60s
- Slice metric regression > 5pp on any monitored slice (ADR-007)

## Related

- Workflow: `.windsurf/workflows/release.md`
- Skill: `rollback` (consequence path on any failure mode)
- Skill: `security-audit` (gate before build)
- ADR-011 — Environment promotion gates
