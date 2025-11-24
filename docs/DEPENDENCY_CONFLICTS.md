# 📦 Dependency Management & Conflict Resolution

This document details the strategy for managing Python dependencies across the `ML-MLOps-Portfolio` and documents known conflicts and their remediations.

## 1. Strategy: Pinned Transitive Dependencies

To ensure **Reproducibility**, we do not rely on loose `requirements.txt` files. Instead, we use a two-step process:

1. **`requirements.in`**: Declares only top-level, direct dependencies with semantic versioning ranges (e.g., `pandas>=1.3.0`).
2. **`pip-compile` (pip-tools)**: Resolves all transitive dependencies and locks them to specific versions in `requirements.txt`.

### Workflow
```bash
# To add a dependency
echo "package_name>=X.Y" >> requirements.in

# To compile/lock versions
pip-compile requirements.in --output-file requirements.txt --resolver=backtracking
```

## 2. Known Conflicts & Resolutions

### 2.1 NumPy vs Scikit-learn vs SciPy
**Conflict**: Newer versions of NumPy (1.24+) deprecated `np.float`, causing crashes in older Scikit-learn (<1.0) and SciPy versions.
**Resolution**:
- We enforce `scikit-learn>=1.0` across all projects.
- We allow `numpy>=1.21` but the `pip-compile` process automatically selects a compatible version (typically 1.24.x or 1.26.x) that satisfies the latest Scikit-learn.

### 2.2 Pydantic V1 vs V2
**Conflict**: FastAPI recently updated to support Pydantic V2, but some older ML libraries or existing codebases rely on Pydantic V1 syntax (`BaseSettings`, etc.).
**Resolution**:
- We currently use `pydantic>=1.10.0` to maintain compatibility.
- For V2 migration, we explicitly import `pydantic.v1` where necessary or strictly pin to `<2.0.0` if a library demands it.
- **Current Status**: Projects are compatible with Pydantic V1. Future roadmap includes migration to V2.

### 2.3 Streamlit & Protobuf
**Conflict**: Streamlit versions can be sensitive to `protobuf` versions, sometimes clashing with `tensorboard` or `mlflow`.
**Resolution**:
- We let `pip-compile` resolve this.
- If a conflict arises, we pin `protobuf` explicitly in `requirements.in` (e.g., `protobuf<4.20`).

### 2.4 M1/M2 Mac (ARM64) Issues
**Conflict**: Some binary wheels (like `xgboost` or `scipy`) had issues on Apple Silicon in older versions.
**Resolution**:
- We use Docker for all development and deployment to abstract OS-level differences.
- Our Docker images use `python:3.11-slim` (Debian based) which has excellent wheel support for x86_64 and ARM64.

## 3. Global Dependency Matrix

To maintain consistency, we strive to keep core libraries synchronized across the portfolio:

| Library | BankChurn | CarVision | TelecomAI | Policy |
|---------|-----------|-----------|-----------|--------|
| **Python** | 3.11+ | 3.11+ | 3.11+ | Strict |
| **Pandas** | >=1.3 | >=1.3 | >=1.3 | Min 1.3 |
| **Sklearn**| >=1.0 | >=1.1 | >=1.0 | Min 1.0 |
| **FastAPI**| >=0.78 | >=0.78 | >=0.78 | Standard |
| **MLflow** | >=2.9 | >=2.9 | >=2.9 | Unified |

## 4. Remediation Steps for New Conflicts

If `pip-compile` fails to resolve dependencies:

1. **Identify the culprit**: Read the error message from `pip-tools`. It usually says "package A requires B<2.0, but package C requires B>=2.0".
2. **Check ecosystem updates**: Has a package released a breaking change recently?
3. **Pin in `requirements.in`**: Add a specific constraint to guide the resolver.
   ```text
   # requirements.in
   # Pinning numpy to avoid conflict with library X
   numpy<1.25
   ```
4. **Re-compile**: Run `pip-compile` again.
5. **Test**: Run the test suite (`make test`) to ensure the new set of packages works at runtime.
