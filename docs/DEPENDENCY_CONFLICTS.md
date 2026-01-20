# Dependency Conflicts Analysis

## Overview

This document analyzes dependency conflicts across the portfolio projects and provides remediation plans.

## Identified Conflicts

### 1. Pydantic Version Conflict

**Projects Affected:**
- BankChurn-Predictor

**Issue:**
- `requirements-core.txt`: `pydantic>=1.9.0`
- `pyproject.toml`: `pydantic>=2.0.0`
- `requirements.in`: `pydantic>=1.9.0`
- `requirements.txt`: `pydantic==2.12.4` (locked)

**Impact:**
- Breaking changes between Pydantic v1 and v2
- Potential runtime errors with model validation
- Inconsistent API across environments

**Remediation Plan:**
1. **Standardize on Pydantic v2** (recommended)
   - Update all requirements to `pydantic>=2.0.0`
   - Migrate validation models to v2 syntax
   - Update import statements where needed

2. **Migration Steps:**
   ```bash
   # Update requirements
   sed -i 's/pydantic>=1.9.0/pydantic>=2.0.0/g' requirements*.txt
   sed -i 's/pydantic>=1.9.0/pydantic>=2.0.0/g' requirements*.in
   
   # Update pyproject.toml (already correct)
   # Test migration
   python -m pytest tests/test_config.py
   ```

### 2. PyArrow Dependency Scope

**Projects Affected:**
- CarVision-Market-Intelligence

**Issue:**
- Uses `pyarrow>=8.0.0` for data processing
- Heavy dependency for simple CSV operations

**Impact:**
- Large installation size (~200MB)
- Longer build times
- Potential version conflicts with other tools

**Remediation Plan:**
1. **Evaluate alternatives:**
   - Use pandas built-in CSV/Parquet readers
   - Consider `fastparquet` instead of `pyarrow`
   - Keep `pyarrow` only if Arrow format is required

2. **Optimization Steps:**
   ```bash
   # Test without pyarrow
   pip uninstall pyarrow
   python -c "import pandas as pd; pd.read_parquet('test.parquet')"
   
   # If fails, install minimal alternative
   pip install fastparquet
   ```

## Cross-Project Dependencies

### Shared Dependencies Matrix

| Dependency | BankChurn | CarVision | TelecomAI | Notes |
|------------|-----------|-----------|-----------|-------|
| pydantic | >=2.0.0 | >=1.10.0 | >=1.10 | Standardize on v2 |
| pyarrow | - | >=8.0.0 | 22.0.0 | Evaluate necessity |
| fastapi | >=0.78.0 | >=0.78.0 | >=0.78 | Consistent version |
| scikit-learn | Latest | Latest | >=1.0 | No conflicts |

### 3. TelecomAI Dependencies Analysis

**Projects Affected:**
- TelecomAI-Customer-Intelligence

**Current State:**
- Uses `pydantic>=1.10` (should be v2)
- Uses `pyarrow==22.0.0` (via mlflow dependencies)
- Uses `fastapi>=0.78` (consistent)
- Uses `scikit-learn>=1.0` (latest)

**Issues:**
- Pydantic v1 should be updated to v2 for consistency
- PyArrow pulled as transitive dependency via MLflow

**Remediation:**
1. Update `pydantic>=1.10` to `pydantic>=2.0.0` in `requirements.in`
2. Monitor PyArrow usage - may be required for MLflow integration

## Resolution Priority

1. **High Priority**: Pydantic version standardization across all projects
2. **Medium Priority**: PyArrow dependency evaluation (CarVision)
3. **Low Priority**: Minor version mismatches

## Testing Strategy

After resolving conflicts:

```bash
# 1. Clean environment
python -m venv test_env
source test_env/bin/activate

# 2. Install each project separately
cd BankChurn-Predictor && pip install -r requirements.txt
cd ../CarVision-Market-Intelligence && pip install -r requirements.txt
cd ../TelecomAI-Customer-Intelligence && pip install -r requirements.txt

# 3. Run tests
python -m pytest tests/ --cov=src/

# 4. Test integration
python scripts/run_experiments.py
```

## Prevention Measures

1. **Dependency Locking**: Use `pip-tools` for consistent dependency resolution
2. **Version Constraints**: Pin critical dependencies in `pyproject.toml`
3. **Regular Audits**: Monthly dependency conflict checks
4. **CI/CD Integration**: Add conflict detection to pipeline

## Tools for Dependency Management

- `pip-audit`: Security vulnerability scanning
- `pipdeptree`: Dependency tree visualization
- `pip-check`: Conflicts detection
- `safety`: Security checking

## Monitoring

Regular dependency updates check:
```bash
# Check for outdated packages
pip list --outdated

# Check for security issues
pip-audit

# Visualize dependency tree
pipdeptree
```

---

**Last Updated**: March 2026

---

**Last Updated**: March 2026
