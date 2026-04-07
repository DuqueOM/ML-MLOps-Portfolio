---
description: Full release process — version bump, changelog, Docker build, multi-cloud deploy, git tag
---

## Release Workflow

// turbo
1. Check that all CI checks pass on `main`:
   ```bash
   gh run list --branch main --limit 5
   ```

2. Run the full test suite locally:
   ```bash
   make test
   ```

// turbo
3. Confirm there are no uncommitted changes:
   ```bash
   git status && git diff --stat
   ```

4. Ask the user for the new version number (semver: major.minor.patch)

5. Update version in all relevant files:
   - Each service's `pyproject.toml`
   - `k8s/base/` deployment manifests (image tags)
   - `helm/ml-portfolio/Chart.yaml` (appVersion)
   - `README.md` version badge

6. Update `CHANGELOG.md` with entries for this release

7. Build Docker images for all 3 services:
   ```bash
   docker build -t bankchurn-predictor:v${VERSION} ./BankChurn-Predictor
   docker build -t nlpinsight-analyzer:v${VERSION} ./NLPInsight-Analyzer
   docker build -t chicagotaxi-demand:v${VERSION} ./ChicagoTaxi-Demand-Pipeline
   ```

8. Tag and push images to Artifact Registry

9. Deploy to GKE (primary):
   ```bash
   kubectl config current-context  # MUST verify cluster
   kubectl apply -k k8s/overlays/gcp/ --dry-run=client
   kubectl apply -k k8s/overlays/gcp/
   ```

10. Run smoke tests:
    ```bash
    ./scripts/smoke_test.sh
    ```

11. If smoke tests pass, deploy to EKS:
    ```bash
    kubectl config use-context <eks-context>
    kubectl apply -k k8s/overlays/aws/
    ./scripts/smoke_test.sh
    ```

12. Commit, tag, and push:
    ```bash
    git add -A
    git commit -m "Release v${VERSION}"
    git tag -a "v${VERSION}" -m "Release v${VERSION}"
    git push origin main --tags
    ```

13. Create GitHub release with changelog excerpt
