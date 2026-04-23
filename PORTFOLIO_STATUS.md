# Portfolio Status

> **Mode:** `Reference / Showcase` — infrastructure is **not currently running**.
> **Last active deployment:** v3.6.0 (March 2026).
> **Reactivation cost estimate:** ~1–2 hours + cloud budget (see §5).

This document explains the operational state of the ML-MLOps Portfolio so that
visitors (recruiters, reviewers, contributors) can quickly understand what is
runnable vs. what is documentation of a prior active state.

---

## 1. What this project is

A reference implementation of production-grade MLOps patterns — 3 ML microservices,
multi-cloud Kubernetes (GKE + EKS), Terraform IaC, CI/CD, observability, drift
detection, and 18 ADRs capturing the design decisions.

**The code, manifests, Terraform, and CI/CD pipelines are real and were deployed
to live clusters during development.** Screenshots, GIFs, measured latencies, and
incident reports in the docs are from those real deployments.

## 2. What is currently active

| Surface | Status | Notes |
|--------|--------|-------|
| Source code (all services) | ✅ Active | Tested on every push (395+ tests, 90–96% coverage) |
| Unit / integration CI | ✅ Active | `ci-mlops.yml` runs on push and PR |
| Terraform validation | ✅ Active | `ci-infra.yml` runs on infra/ changes |
| Docs (MkDocs) | ✅ Active | Deployed to GitHub Pages |
| Docker images (GHCR) | ✅ Active | Built on every push, used as CI test artifacts |
| **GKE cluster** | ⏸️ **Inactive** | Torn down after development |
| **EKS cluster** | ⏸️ **Inactive** | Torn down after development |
| **Artifact Registry / ECR images** | ⏸️ **Inactive** | Promotion workflow disabled |
| **MLflow, Prometheus, Grafana** | ⏸️ **Inactive** | Deployed on the clusters; gone with them |
| **Daily drift detection** | ⏸️ **Paused** | `schedule:` trigger commented out — `workflow_dispatch` only |
| **Daily retrain checks** | ⏸️ **Paused** | Same as above |

## 3. Why infrastructure is off

Running GKE + EKS + managed Postgres + Artifact Registry continuously costs
~$180–$220/month combined. This is sustainable during active development and
load-testing but not as a permanent showcase. The technical material that
demonstrates the deployments (manifests, runbooks, ADRs, screenshots, load-test
results, incident post-mortems) is preserved.

See [ADR-018: Portfolio Maintenance Mode](decisions/018-portfolio-maintenance-mode.md)
for the full decision record.

## 4. How noise from inactive infrastructure is handled

With real CI/CD pipelines but no live clusters, three sources of auto-generated
noise appear on any GitHub repository:

| Noise source | Handling |
|-------------|----------|
| **Daily drift-detection workflow** | Converted to `workflow_dispatch`-only. The previous `if: steps.drift.outcome == 'failure'` condition is a known anti-pattern: it misinterprets *script errors* (data missing, network issue) as *drift events*. Fixed to `steps.drift.outcome == 'success' && drift_detected == 'true'`. |
| **Trivy base-image CVE alerts** | `ignore-unfixed: true` added to the scanner. Only CVEs with an upstream fix are surfaced. Previously-open base-image CVEs dismissed with reason `won't fix` (see GitHub Security tab). |
| **Dependabot PRs for GitHub Actions** | Weekly cadence, capped at 3 open PRs. CI-only action bumps are merged promptly; Docker image bumps evaluated at next active development sprint. |

## 5. How to reactivate for live demo

If a recruiter or reviewer wants to see the system running end-to-end, full
reactivation takes ~1–2 hours plus cloud spend. Steps (documented in
`docs/PRODUCTION_DEPLOYMENT.md`):

1. **Provision infrastructure** (~30 min)
   ```bash
   cd infra/terraform/gcp && terraform apply -var-file=terraform.tfvars
   cd ../aws && terraform apply -var-file=terraform.tfvars
   ```
2. **Push images to cloud registries** (~15 min)
   ```bash
   gh workflow run promote-images.yml
   ```
3. **Deploy to clusters** (~20 min)
   ```bash
   gh workflow run deploy-gcp.yml --ref v3.6.0
   gh workflow run deploy-aws.yml --ref v3.6.0
   ```
4. **Re-enable scheduled drift detection** — uncomment the `schedule:` block in
   `.github/workflows/drift-detection.yml`.
5. **Run smoke tests** — `./scripts/smoke_test.sh`.
6. **Teardown when done** — `terraform destroy` in both `infra/terraform/gcp`
   and `infra/terraform/aws`.

## 6. What changed in this maintenance pass

- Closed **168 stale drift-alert issues** with explanation linking to this file.
- Merged **3 Dependabot PRs** (GitHub Actions version bumps).
- **Fixed the drift workflow bug**: `if: outcome == 'failure'` → `outcome == 'success' && drift_detected == 'true'`.
- **Disabled the daily schedule** on `drift-detection.yml` (kept `workflow_dispatch`).
- **Hardened Trivy**: `ignore-unfixed: true` to prevent re-accumulation of unfixable base-image CVEs.
- **Dismissed ~210 legacy Trivy alerts** with documented `won't fix` reason.
- Added this file and [ADR-018](decisions/018-portfolio-maintenance-mode.md).

## 7. Questions frequently asked by reviewers

**Q: Can you actually redeploy this, or are the clusters gone and it's all just docs?**
A: Yes — the Terraform is current and validated on every `infra/` push. Deploy
   is ~1 hour from `terraform apply` to green smoke tests.

**Q: How did you verify the latencies in the README (200ms BankChurn, etc.)?**
A: With Locust load tests against the live clusters at v3.6.0 — raw results in
   `docs/load-test-results.md`, session screenshots in `docs/media/`.

**Q: Why not keep it running with lower resources?**
A: Considered — see ADR-018 alternatives. The cost floor is GKE control plane
   ($72/mo) + EKS control plane ($72/mo), which exists even at 0 workload. Not
   economical for a permanent showcase.

**Q: How would you avoid this noise problem in a real production setup?**
A: The bug (`if: outcome == 'failure'`) was a real anti-pattern and is now
   fixed in the workflow. In production with live data, the drift job would
   succeed every run, and issues would only be created on actual PSI violations
   above 0.25 (see ADR-006, `drift-detection` skill).
