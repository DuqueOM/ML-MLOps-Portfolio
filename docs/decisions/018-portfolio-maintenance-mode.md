<div class="portfolio-page" markdown="1">

# ADR-018: Portfolio Maintenance Mode

## Status

**Accepted** — April 2026

## Context

After reaching v3.6.0 (full multi-cloud deployment verified, managed ML
platforms added, load-tested on both clouds), the portfolio entered a phase
where keeping the infrastructure running continuously was economically
unjustified:

- **GKE control plane**: ~$72/month (even at 0 workload)
- **EKS control plane**: ~$72/month (even at 0 workload)
- **Managed Postgres (RDS + Cloud SQL)**: ~$30–50/month combined
- **Artifact Registry / ECR storage**: minor but non-zero
- **NAT gateways, load balancers, disks**: ~$40/month combined
- **Total idle cost**: ~$180–220/month for a portfolio nobody is actively using

At the same time, three symptoms appeared on the public repository:

1. **168 stale "drift-alert" issues** auto-created by the daily drift-detection
   workflow. The workflow ran on schedule against stale data, failed for
   unrelated reasons (missing data path, hash-pinned requirements conflict), and
   the condition `if: steps.drift.outcome == 'failure'` misinterpreted those
   script errors as drift events — creating empty-body issues every day.
2. **~210 Trivy code-scanning alerts** for base-image (Debian/Python) CVEs,
   most of them `severity=note` and most without an upstream fix available.
3. **Multiple unmerged Dependabot PRs** for GitHub Actions version bumps.

A visitor (recruiter, reviewer) arriving at the repo would see these as signals
of an abandoned project, which contradicts the actual state (technically sound
code, 395+ tests passing, fully documented).

## Decision

**Transition the portfolio to a formal "Reference / Showcase" mode** and encode
this state in visible artifacts:

1. **Declare the mode publicly** — add a status badge and banner to README.md
   linking to `PORTFOLIO_STATUS.md` which explains what is live, what is paused,
   and how to reactivate.
2. **Convert scheduled workflows to manual-only** — drop `schedule:` triggers on
   `drift-detection.yml` and related workflows while infrastructure is offline;
   keep `workflow_dispatch` so everything can still be demonstrated on demand.
3. **Fix the drift-alert bug** — change the issue-creation condition from
   `steps.drift.outcome == 'failure'` to
   `steps.drift.outcome == 'success' && steps.metrics.outputs.drift_detected == 'true'`.
   This is a correctness fix that would apply even in active mode: *script
   failure* and *drift event* are distinct things and must not be conflated.
4. **Harden Trivy scanning** — add `ignore-unfixed: true` to the scanner so that
   base-image CVEs without upstream fixes don't re-accumulate; bulk-dismiss the
   existing ~210 alerts with reason `won't fix` and a documented comment linking
   to this ADR.
5. **Clear existing noise** — close the 168 stale drift-alert issues with a
   referenced explanation; merge the pending Dependabot PRs.

## Alternatives considered

### Alternative 1: Keep running with smaller clusters

Tried mentally. GKE and EKS both charge a **fixed control-plane fee** regardless
of workload size. Scaling node pools to zero saves node cost but not the
$144/month control-plane floor. Not economical for a permanent showcase.

### Alternative 2: Archive the repository

Would stop all CI activity and thus all noise — but also removes the ability to
demonstrate the CI/CD pipeline (unit tests, Terraform validate, Docker build)
which is itself a key part of the portfolio. Rejected.

### Alternative 3: Disable all workflows

Leaves the repo look "dead" and removes the ability to demonstrate that the CI
actually runs and passes. Rejected — kept unit tests, Terraform validate,
Docker build, Trivy scan, docs deployment on push/PR.

### Alternative 4: Just close the issues without fixing the workflow

Leaves the underlying bug that will re-create the same noise next time the
workflow runs. Rejected — the fix is a one-line correctness improvement that
applies in both active and showcase modes.

## Consequences

### Positive

- Repo presents as "controlled and documented", not "abandoned"
- The drift-workflow bug fix benefits any future active period (real bug, real fix)
- Trivy `ignore-unfixed: true` prevents permanent growth of unfixable alerts
- Clear reactivation path documented (~1 hour, $180–220/month ongoing)
- ADR + PORTFOLIO_STATUS.md turn a limitation into a demonstrated understanding
  of operational trade-offs — recruiters value documented decisions more than
  continuously-running infrastructure

### Negative

- The live demo links in older docs (e.g., `https://<elb-dns>/health`) no longer
  resolve. Mitigated by the README banner and status doc; live-verification
  evidence preserved in `DEPLOYMENT_EVIDENCE.md`.
- Any visitor running `terraform plan` against the state bucket will see full
  destroy plans. Mitigated by removing the remote state buckets after teardown;
  Terraform runs locally with empty state.

## Reactivation criteria

The portfolio returns to "Active" mode when any of the following is true:

- **Interview demonstration requested** — reactivate for the interview window,
  teardown after
- **Feature development** — implementing a new ADR that requires live cloud
  validation (e.g., adding a new managed service comparison)
- **Budget allocated** — if the monthly cost becomes sustainable for a period

Reactivation checklist is in `PORTFOLIO_STATUS.md §5`.

## References

- `PORTFOLIO_STATUS.md` — visitor-facing state document
- `.github/workflows/drift-detection.yml` — contains the corrected alert condition
- `.github/workflows/ci-mlops.yml` — contains `ignore-unfixed: true`
- CHANGELOG v3.6.1 entry (to be written on next release)

</div>
