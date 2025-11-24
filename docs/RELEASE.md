# 🚀 Release Process

This document defines the standard release process for the `ML-MLOps-Portfolio` projects. We follow **Semantic Versioning (SemVer)** and use **GitHub Releases** to manage deployment artifacts.

## 1. Versioning Strategy

We use the `MAJOR.MINOR.PATCH` format:
- **MAJOR**: Incompatible API changes (e.g., v1.0.0 -> v2.0.0)
- **MINOR**: Functionality added in a backwards compatible manner (e.g., v1.0.0 -> v1.1.0)
- **PATCH**: Backwards compatible bug fixes (e.g., v1.0.0 -> v1.0.1)

### Tagging
Tags are applied at the git level and trigger specific CI/CD pipelines.
Format: `v<version>-<project_code>` (optional suffix for monorepo clarity, though we currently release the whole repo or use specific tags).

Examples:
- `v1.0.0` (Global Release)
- `bankchurn-v1.2.0` (Project specific)

## 2. Release Workflow

### Step 1: Pre-Release Checks
1. Ensure all tests pass: `make test-all`
2. Verify documentation is up to date.
3. Check for security vulnerabilities: `make scan-all`

### Step 2: Create a Release Candidate
1. Create a branch `release/vX.Y.Z`
2. Bump version numbers in:
   - `pyproject.toml` (if applicable) or `setup.py`
   - `src/<package>/__init__.py` (`__version__`)
   - `CHANGELOG.md`

### Step 3: Validation
Run the full CI pipeline on the release branch.
```bash
git push origin release/vX.Y.Z
```
Wait for GitHub Actions to return green.

### Step 4: Finalize Release
1. Merge `release/vX.Y.Z` into `main`.
2. Tag the commit on `main`.
   ```bash
   git checkout main
   git pull
   git tag -a v1.0.0 -m "Release v1.0.0: Unified MLOps Portfolio"
   git push origin v1.0.0
   ```

### Step 5: Automated Deployment
The CI pipeline detects the tag and:
1. Builds production Docker images.
2. Tags them with `v1.0.0` and `latest`.
3. Pushes to **GitHub Container Registry (GHCR)**.
4. Creates a **GitHub Release** draft with auto-generated changelog.

## 3. Artifacts

Every release produces the following immutable artifacts:
- **Docker Images**: `ghcr.io/duqueom/bankchurn:v1.0.0`
- **Model Artifacts**: Saved in MLflow/S3 with the corresponding version tag.
- **Source Code**: Tarball/Zip via GitHub Releases.

## 4. Rollback Procedure

If a critical bug is found in `v1.0.0`:
1. Revert the changes in `main`.
2. Create a patch release `v1.0.1`.
3. Redeploy using the `v1.0.1` tag.
4. **Fast Rollback**: Manually redeploy the previous docker tag `v0.9.0` while fixing the bug.
